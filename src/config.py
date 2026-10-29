"""Fixed administrative panel and temporal partitions; no fitted model."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELDS=['recall_number','event_id','report_date','classification','product_type']
CLASSES=['Class I','Class II','Class III']
PANELS=['All',*CLASSES]
YEARS=list(range(2017,2026))
CAL_YEARS=list(range(2017,2022))
EVAL_YEARS=list(range(2022,2026))
QUANTILES=[(9,10),(19,20),(99,100)]
