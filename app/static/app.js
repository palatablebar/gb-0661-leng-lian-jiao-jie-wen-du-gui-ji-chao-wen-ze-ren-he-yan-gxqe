const state = {busy:false};
const feedback=document.getElementById('feedback');
async function request(path,payload){
 state.busy=true;feedback.hidden=false;feedback.textContent='正在处理…';
 try{const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw new Error(data.detail||'运行失败，请重试');location.reload();}
 catch(error){feedback.textContent=error.message;}finally{state.busy=false;document.querySelectorAll('button').forEach(b=>b.disabled=false);}
}
document.getElementById('run').addEventListener('click',()=>{
 if(state.busy)return;
 document.getElementById('run').disabled=true;
 const raw=document.getElementById('csv-text')?.value;
 request('/api/runs',{sample:document.getElementById('sample').value,...(raw?{csv_text:raw}:{}),threshold:document.getElementById('threshold')?.value||'8',max_gap:Number(document.getElementById('gap')?.value||15)});
});
document.getElementById('review')?.addEventListener('click',event=>{if(state.busy)return;const b=event.currentTarget;b.disabled=true;request('/api/batches/review',{run_id:b.dataset.run,version:Number(b.dataset.version)});});
