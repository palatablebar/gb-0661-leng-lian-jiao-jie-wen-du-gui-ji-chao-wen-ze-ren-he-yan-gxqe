from decimal import Decimal

def excess(left,right,minutes,threshold):
    a=Decimal(left)-Decimal(threshold);b=Decimal(right)-Decimal(threshold);d=Decimal(minutes)
    if a<=0 and b<=0:return Decimal(0),Decimal(0)
    if a>=0 and b>=0:return d,d*(a+b)/2
    positive=max(a,b);duration=d*positive/abs(b-a)
    return duration,duration*positive/2

def fmt(n):return str(n.quantize(Decimal('0.000001')))
