# 冷链轨迹深度登记

规模：中型。使用者：冷链质控员。核心规则：超过8°C的线性温度轨迹按阈值交点与交接端点切分积分，长缺测区间不插值。

## 功能模块
| 模块 | 使用者动作 | 入口 | 核心文件 | 测试 |
|---|---|---|---|---|
| M1 轨迹采信 | 采信字节与保留行号 | `/intake`、`/api/intake` | `app/modules/intake/reader.py` `app/modules/intake/service.py` | `tests/test_intake.py` |
| M2 探头校准 | 归一时间和修正温度 | `/contract`、`/api/contract` | `app/modules/contract/normalize.py` `app/modules/contract/service.py` | `tests/test_contract.py` |
| M3 交接区间 | 切分责任段与裁决冲突 | `/model`、`/api/model` | `app/modules/model/intervals.py` `app/modules/model/service.py` | `tests/test_model.py` |
| M4 超温积分 | 阈值交点与梯形积分 | `/calculate`、`/api/calculate` | `app/modules/calculate/integral.py` `app/modules/calculate/service.py` | `tests/test_calculate.py` |
| M5 质量隔离 | 筛查坏行与导出证据 | `/quarantine`、`/api/quarantine` | `app/modules/quarantine/rules.py` `app/modules/quarantine/service.py` | `tests/test_quarantine.py` |
| M6 责任对账 | 行数分钟和积分守恒 | `/reconcile`、`/api/reconcile` | `app/modules/reconcile/compare.py` `app/modules/reconcile/service.py` | `tests/test_reconcile.py` |
| M7 批次复核 | 内容去重与版本复核、补签发布 | `/batches`、`/api/batches` | `app/modules/batches/review.py` `app/modules/batches/service.py` `app/modules/batches/supplement.py` | `tests/test_batches.py` `tests/test_supplement.py` |

## 陷阱登记
| TRAP | 现象 | 朴素实现会怎样 | 本项目处理 | 处理位置 | 测试 |
|---|---|---|---|---|---|
| TRAP-01 | 混合编码 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/intake/reader.py` | `tests/test_intake.py::test_legacy_encoding` |
| TRAP-02 | BOM表头 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/intake/reader.py` | `tests/test_intake.py::test_bom_sample` |
| TRAP-06 | 全角温度 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/contract/normalize.py` | `tests/test_contract.py::test_fullwidth` |
| TRAP-07 | 空值哨兵 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/contract/normalize.py` | `tests/test_contract.py::test_missing` |
| TRAP-11 | 偏移一致 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/contract/normalize.py` | `tests/test_contract.py::test_timezone_equivalence` |
| TRAP-13 | 乱序到达 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/model/service.py` | `tests/test_model.py::test_late_kept` |
| TRAP-14 | 同键冲突 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/model/service.py` | `tests/test_model.py::test_conflict_all_isolated` |
| TRAP-15 | 温标混用 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/contract/normalize.py` | `tests/test_contract.py::test_fahrenheit_correction` |
| TRAP-23 | 交接边界 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/model/intervals.py` | `tests/test_model.py::test_half_open_owner` |
| TRAP-26 | 陈旧复核 | 静默误算或覆盖 | 原值保留并确定性判定；由脏样例触发 | `app/modules/batches/service.py` | `tests/test_batches.py::test_optimistic_review` |
| TRAP-27 | 补签越界与重试 | 改写已复核账或重复计入 | 补签追加发布新正式账，旧账整包保留；签号幂等，缺证据拒绝 | `app/modules/batches/supplement.py` `app/store.py` | `tests/test_supplement.py` |

## 对账规则
输入数据行=有效采样+隔离行+空行。责任覆盖分钟=正常+超温+未知。各责任方热暴露积分之和等于总积分；展示保留六位小数，守恒容差0.00001。

## 补签发布
交接补签到达时当天正式责任账追加发布，不改写已复核批次。补签区间与既有交接重叠时以最新签收为准裁切旧区间，合并后重算分段、积分与对账；产生责任冲突或四账不平则拒绝并保留当前正式账。签号、区间、签收时间与证据引用缺一即拒绝。签号唯一，同一补签重试返回首次发布结果，不新增记录；同签号不同内容返回409。补签档案、新账版本与版本链在同一事务写入，失败整体回滚恢复旧版。原始采样、隔离行与已确认记录原样带入新版；补签前结论可按批次号经 `/api/batches/{run_id}` 追回。复核页展示按责任方的前后责任分钟、热暴露变化与采用依据。

## 流水线与恢复
每个业务模块可用同一份内置样例独立试跑。文件超过2MB或10000条会拒绝。编码与结构先校验，坏行隔离后继续。SQLite仅在完整计算成功后事务写入。重复运行的输入摘要、校准摘要、交接摘要、规则版本及参数完全一致时复用批次。重新打开数据库保留批次；旧版本复核返回409。

## 已知不覆盖
不连接实时探头，不外推首尾采样，不将缺测判断成温度合格。交接责任冲突会阻止复核。GB18030只是明确的设备编码兼容链，不推断任意字符集。