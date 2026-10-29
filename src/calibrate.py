"""Only 2017â€“2021 counts enter illustrative policy thresholds."""
from fractions import Fraction
from config import ROOT,CAL_YEARS,PANELS,QUANTILES
from accounting import read,monthly,q7,save_json

def main():
    counts,_=monthly(read(),CAL_YEARS);thresholds=[]
    for omit in [None,*CAL_YEARS]:
        for panel in PANELS:
            rows=[r for r in counts if r['panel']==panel and int(r['month'][:4])!=omit]
            for n,d in QUANTILES:
                if omit is not None and (n,d)!=(19,20):continue
                for grain in ['events','products']:
                    q=q7([r[grain] for r in rows],Fraction(n,d))
                    thresholds.append({'omitted_year':omit,'panel':panel,'q_numerator':n,'q_denominator':d,'grain':grain,'months':len(rows),'numerator':q.numerator,'denominator':q.denominator})
    save_json(ROOT/'results/calibration.json',{'calibration_years':CAL_YEARS,'convention':'Type7; exact rational; flag strictly greater; no optimization','thresholds':thresholds})
    print('Saved64fixed thresholds from calibration only.')

if __name__=='__main__':main()
