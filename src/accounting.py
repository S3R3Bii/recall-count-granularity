"""Exact finite-snapshot counting and fixed linear quantiles."""
import csv,json
from collections import defaultdict,Counter
from fractions import Fraction
from config import ROOT,PANELS

def read():
    with (ROOT/'data/records.csv').open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def q7(values,q):
    values=sorted(values);assert values
    h=(len(values)-1)*q;i=h.numerator//h.denominator
    return Fraction(values[i])+(h-i)*(values[min(i+1,len(values)-1)]-values[i])

def monthly(rows,years):
    buckets=defaultdict(list)
    for r in rows:
        if int(r['report_date'][:4]) not in years:continue
        month=r['report_date'][:4]+'-'+r['report_date'][4:6]
        buckets['All',month].append(r);buckets[r['classification'],month].append(r)
    result=[];members=[]
    for panel in PANELS:
        for year in years:
            for m in range(1,13):
                month=f'{year}-{m:02}';group=buckets[panel,month];counts=Counter(r['event_id'] for r in group)
                p=len(group);e=len(counts);u=len({r['recall_number'] for r in group});sizes=sorted(counts.values(),reverse=True)
                for event,n in sorted(counts.items()):members.append({'panel':panel,'month':month,'event_id':event,'products':n})
                result.append({'panel':panel,'month':month,'products':p,'unique_products':u,'events':e,'excess_products':p-e,'fanout':p/e if e else 0,'largest_event_products':max(sizes,default=0),'top5_product_fraction':sum(sizes[:5])/p if p else 0,'product_hhi':sum(n*n for n in sizes)/(p*p) if p else 0})
    return result,members

def write_csv(path,rows):
    assert rows
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def save_json(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')

def flag(n,t):return int(n*t['denominator']>t['numerator'])
