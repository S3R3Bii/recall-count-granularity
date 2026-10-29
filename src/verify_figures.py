"""Validate every plotted value against independent SQL or contingency accounting."""
import csv,json,sqlite3
from fractions import Fraction
from collections import Counter,defaultdict
from config import ROOT

def load(path):
    with (ROOT/path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def main():
    db=sqlite3.connect(':memory:');db.execute('CREATE TABLE r(event TEXT,month TEXT,class TEXT)');source=load('data/records.csv')
    db.executemany('INSERT INTO r VALUES(?,?,?)',[(r['event_id'],r['report_date'][:4]+'-'+r['report_date'][4:6],r['classification']) for r in source])
    months={m:(p,e) for m,p,e in db.execute('SELECT month,COUNT(*),COUNT(DISTINCT event) FROM r GROUP BY month')}
    sizes=defaultdict(list)
    for m,_,n in db.execute('SELECT month,event,COUNT(*) FROM r GROUP BY month,event'):sizes[m].append(n)
    flags=load('results/evaluation/monthly_flags.csv');hist={}
    for r in flags:
        if r['omitted_year']!='':continue
        for policy,col in [('same_event_threshold','product_same_threshold_flag'),('own_product_threshold','product_own_threshold_flag')]:
            key=r['panel'],r['q'],policy
            h=hist.setdefault(key,Counter());a=int(r['event_flag']);b=int(r[col]);h['both']+=a*b;h['product_only']+=(1-a)*b;h['event_only']+=a*(1-b);h['neither']+=(1-a)*(1-b)
    plot=load('figures/PLOT_DATA.csv');assert len(plot)==528;seen=set();checks=0
    for r in plot:
        key=tuple(r[k] for k in ['figure','panel','month','q','policy','series']);assert key not in seen;seen.add(key)
        if r['figure']=='monthly-counts':value=months[r['month']][0 if r['series']=='products' else 1]
        elif r['figure']=='event-fanout':
            p,e=months[r['month']];value=Fraction(p,e) if r['series']=='fanout' else 100*Fraction(sum(sorted(sizes[r['month']],reverse=True)[:5]),p)
        else:value=hist[r['panel'],r['q'],r['policy']][r['series']]
        assert abs(float(r['value'])-float(value))<=1e-12;checks+=1
    # These are global membership facts, not amendment-history or lifecycle evidence.
    distinct,mm,mc=db.execute('SELECT COUNT(DISTINCT event),0,0 FROM r').fetchone()
    mm=db.execute('SELECT COUNT(*) FROM (SELECT event FROM r GROUP BY event HAVING COUNT(DISTINCT month)>1)').fetchone()[0]
    mc=db.execute('SELECT COUNT(*) FROM (SELECT event FROM r GROUP BY event HAVING COUNT(DISTINCT class)>1)').fetchone()[0]
    for phase in ['development','evaluation']:
        s=json.loads((ROOT/f'results/{phase}/summary.json').read_text());yearmin,yearmax=(2017,2021) if phase=='development' else (2022,2025)
        values=[Fraction(p,e) for m,(p,e) in months.items() if yearmin<=int(m[:4])<=yearmax];assert abs(s['max_monthly_fanout']-float(max(values)))<=1e-12
    cert={'status':'PASS','plotted_values':checks,'global_distinct_events':distinct,'global_multi_month_event_ids':mm,'global_multi_class_event_ids':mc,'scope':'Independent source SQL, exact ratios and retained independently verified policy flags; visual inspection is separate'}
    (ROOT/'results/FIGURE_CHECK.json').write_text(json.dumps(cert,indent=2)+'\n',encoding='utf-8');print(json.dumps(cert))

if __name__=='__main__':main()
