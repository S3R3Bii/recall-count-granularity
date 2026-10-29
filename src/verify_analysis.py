"""SQLite/decimal/int reconstruction, independently of production counting and flags."""
import argparse,csv,json,sqlite3
from collections import defaultdict
from decimal import Decimal
from fractions import Fraction
from config import ROOT,PANELS,CAL_YEARS,EVAL_YEARS

def records(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main(phase):
    db=sqlite3.connect(':memory:');db.execute('CREATE TABLE r(product TEXT,event TEXT,month TEXT,class TEXT)')
    original=records(ROOT/'data/records.csv');db.executemany('INSERT INTO r VALUES(?,?,?,?)',[(r['recall_number'],r['event_id'],r['report_date'][:4]+'-'+r['report_date'][4:6],r['classification']) for r in original])
    checks=0;max_delta=0.0;allcounts={};allmembers={}
    for panel in PANELS:
        where='' if panel=='All' else ' WHERE class=?';params=[] if panel=='All' else [panel]
        for m,p,u,e in db.execute('SELECT month,COUNT(*),COUNT(DISTINCT product),COUNT(DISTINCT event) FROM r'+where+' GROUP BY month',params):allcounts[panel,m]=(p,u,e)
        for m,event,n in db.execute('SELECT month,event,COUNT(*) FROM r'+where+' GROUP BY month,event',params):allmembers[panel,m,event]=n
    cal=json.loads((ROOT/'results/calibration.json').read_text());thresholds={}
    for t in cal['thresholds']:
        vals=[]
        for year in CAL_YEARS:
            if year==t['omitted_year']:continue
            for m in range(1,13):vals.append(allcounts.get((t['panel'],f'{year}-{m:02}'),(0,0,0))[2 if t['grain']=='events' else 0])
        vals.sort();h=Decimal(len(vals)-1)*Decimal(t['q_numerator'])/Decimal(t['q_denominator']);lo=int(h);hi=min(lo+1,len(vals)-1)
        value=Decimal(vals[lo])+(h-lo)*Decimal(vals[hi]-vals[lo]);actual=Fraction(t['numerator'],t['denominator'])
        assert Fraction(value)==actual and t['months']==len(vals);checks+=2
        thresholds[t['panel'],t['omitted_year'],f"{t['q_numerator']}/{t['q_denominator']}",t['grain']]=actual
    folder=ROOT/'results'/phase;years=CAL_YEARS if phase=='development' else EVAL_YEARS
    counted=records(folder/'monthly_counts.csv');assert len(counted)==len(years)*12*len(PANELS)
    for row in counted:
        key=row['panel'],row['month'];p,u,e=allcounts.get(key,(0,0,0));sizes=[n for (panel,m,_),n in allmembers.items() if (panel,m)==key];sizes.sort(reverse=True)
        expected={'products':p,'unique_products':u,'events':e,'excess_products':p-e,'largest_event_products':max(sizes,default=0)}
        for k,v in expected.items():assert int(row[k])==v;checks+=1
        for k,value in [('fanout',Fraction(p,e) if e else Fraction()),('top5_product_fraction',Fraction(sum(sizes[:5]),p) if p else Fraction()),('product_hhi',sum((Fraction(n,p)**2 for n in sizes),Fraction()) if p else Fraction())]:
            delta=abs(float(row[k])-float(value));assert delta<=1e-12;max_delta=max(max_delta,delta);checks+=1
    memberships=records(folder/'event_memberships.csv');expected={(p,m,e):n for (p,m,e),n in allmembers.items() if int(m[:4]) in years}
    assert len(memberships)==len(expected)
    for row in memberships:assert int(row['products'])==expected[row['panel'],row['month'],row['event_id']];checks+=1
    flags=records(folder/'monthly_flags.csv');expectedflags={}
    for r in flags:
        omit=int(r['omitted_year']) if r['omitted_year'] else None;p,_,e=allcounts.get((r['panel'],r['month']),(0,0,0));et=thresholds[r['panel'],omit,r['q'],'events'];pt=thresholds[r['panel'],omit,r['q'],'products']
        fs=[int(Fraction(e)>et),int(Fraction(p)>et),int(Fraction(p)>pt)]
        for col,v in zip(['event_flag','product_same_threshold_flag','product_own_threshold_flag'],fs):assert int(r[col])==v;checks+=1
        key=r['panel'],r['omitted_year'],r['q'];expectedflags.setdefault(key,[]).append(fs)
    summary=records(folder/'flag_summary.csv')
    assert len(summary)==64
    for r in summary:
        pairs=[(f[0],f[1 if r['product_policy']=='same_event_threshold' else 2]) for f in expectedflags[r['panel'],r['omitted_year'],r['q']]]
        hist={(a,b):sum((x,y)==(a,b) for x,y in pairs) for a in [0,1] for b in [0,1]}
        values={'months':len(pairs),'event_flags':hist[1,0]+hist[1,1],'product_flags':hist[0,1]+hist[1,1],'both':hist[1,1],'product_only':hist[0,1],'event_only':hist[1,0],'neither':hist[0,0]}
        for k,v in values.items():assert int(r[k])==v;checks+=1
        assert sum(hist.values())==len(years)*12
    s=json.loads((folder/'summary.json').read_text());where=' WHERE CAST(substr(month,1,4) AS INTEGER) BETWEEN ? AND ?';params=[min(years),max(years)]
    p,e,distinct=db.execute('SELECT COUNT(*),COUNT(DISTINCT event||":"||month),COUNT(DISTINCT event) FROM r'+where,params).fetchone()
    multi_month=db.execute('SELECT COUNT(*) FROM (SELECT event FROM r'+where+' GROUP BY event HAVING COUNT(DISTINCT month)>1)',params).fetchone()[0]
    multi_class=db.execute('SELECT COUNT(*) FROM (SELECT event FROM r'+where+' GROUP BY event HAVING COUNT(DISTINCT class)>1)',params).fetchone()[0]
    for k,v in [('source_products',p),('event_months',e),('distinct_event_ids',distinct),('multi_month_event_ids',multi_month),('multi_class_event_ids',multi_class)]:assert s[k]==v;checks+=1
    assert s['product_event_month_ratio']==p/e;checks+=1
    cert={'status':'PASS','phase':phase,'independent_value_checks':checks,'max_float_delta':max_delta,'methods':'SQLite distinct/grouped counts; decimal type7 quantiles; Fraction comparisons/concentration; independent contingency histograms','tolerance':'Exact integers/rational thresholds/flags;1e-12 absolute for reported float ratios only'}
    (folder/'INDEPENDENT_CHECK.json').write_text(json.dumps(cert,indent=2)+'\n',encoding='utf-8');print(json.dumps(cert))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['development','evaluation']);main(p.parse_args().phase)
