"""Retain all grain policies, panels and prespecified sensitivities."""
import argparse,json
from collections import defaultdict
from config import ROOT,CAL_YEARS,EVAL_YEARS,PANELS,QUANTILES
from accounting import read,monthly,write_csv,save_json,flag

def analyze(phase):
    years=CAL_YEARS if phase=='development' else EVAL_YEARS
    rows=read();counts,members=monthly(rows,years);out=ROOT/'results'/phase;out.mkdir(exist_ok=True)
    write_csv(out/'monthly_counts.csv',counts);write_csv(out/'event_memberships.csv',members)
    thresholds=json.loads((ROOT/'results/calibration.json').read_text())['thresholds'];flags=[]
    for r in counts:
        for omit in [None,*CAL_YEARS]:
            for n,d in QUANTILES:
                if omit is not None and (n,d)!=(19,20):continue
                options=[t for t in thresholds if t['panel']==r['panel'] and t['omitted_year']==omit and (t['q_numerator'],t['q_denominator'])==(n,d)]
                et=next(t for t in options if t['grain']=='events');pt=next(t for t in options if t['grain']=='products')
                flags.append({'panel':r['panel'],'month':r['month'],'omitted_year':'' if omit is None else omit,'q':f'{n}/{d}','event_flag':flag(r['events'],et),'product_same_threshold_flag':flag(r['products'],et),'product_own_threshold_flag':flag(r['products'],pt)})
    write_csv(out/'monthly_flags.csv',flags)
    summary=[]
    for panel in PANELS:
        for omit in [None,*CAL_YEARS]:
            for n,d in QUANTILES:
                if omit is not None and (n,d)!=(19,20):continue
                group=[f for f in flags if f['panel']==panel and f['omitted_year']==('' if omit is None else omit) and f['q']==f'{n}/{d}']
                for label,col in [('same_event_threshold','product_same_threshold_flag'),('own_product_threshold','product_own_threshold_flag')]:
                    summary.append({'panel':panel,'omitted_year':'' if omit is None else omit,'q':f'{n}/{d}','product_policy':label,'months':len(group),'event_flags':sum(f['event_flag'] for f in group),'product_flags':sum(f[col] for f in group),'both':sum(f[col]*f['event_flag'] for f in group),'product_only':sum(f[col]*(1-f['event_flag']) for f in group),'event_only':sum((1-f[col])*f['event_flag'] for f in group),'neither':sum((1-f[col])*(1-f['event_flag']) for f in group)})
    write_csv(out/'flag_summary.csv',summary)
    event_months=defaultdict(set);event_classes=defaultdict(set)
    for r in rows:
        if int(r['report_date'][:4]) in years:
            event_months[r['event_id']].add(r['report_date'][:6]);event_classes[r['event_id']].add(r['classification'])
    allrows=[r for r in counts if r['panel']=='All']
    save_json(out/'summary.json',{'phase':phase,'years':years,'source_products':sum(r['products'] for r in allrows),'event_months':sum(r['events'] for r in allrows),'distinct_event_ids':len(event_months),'multi_month_event_ids':sum(len(x)>1 for x in event_months.values()),'multi_class_event_ids':sum(len(x)>1 for x in event_classes.values()),'max_monthly_fanout':max(r['fanout'] for r in allrows),'product_event_month_ratio':sum(r['products'] for r in allrows)/sum(r['events'] for r in allrows)})
    print(json.dumps({'phase':phase,'monthly_cells':len(counts),'membership_cells':len(members),'policy_month_cells':len(flags),'summary_rows':len(summary)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['development','evaluation']);analyze(parser.parse_args().phase)
