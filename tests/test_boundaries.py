import sys,unittest
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from accounting import monthly,q7,flag
from ingest import validate

def row(product,event,date,cl='Class I'):
    return dict(recall_number=product,event_id=event,report_date=date,classification=cl,product_type='Food',source_year=date[:4],source_skip='0',source_row='0')

class Boundaries(unittest.TestCase):
    def test_products_preserved(self):
        counts,members=monthly([row('a','1','20170101'),row('b','1','20170102'),row('c','2','20170102')],[2017]);r=counts[0]
        self.assertEqual((r['products'],r['events'],r['excess_products']),(3,2,1));self.assertEqual(r['fanout'],1.5);self.assertEqual(r['product_hhi'],5/9)
    def test_cross_month_event(self):
        counts,_=monthly([row('a','1','20170101'),row('b','1','20170201')],[2017]);self.assertEqual(sum(r['events'] for r in counts if r['panel']=='All'),2)
    def test_class_overlap(self):
        counts,_=monthly([row('a','1','20170101'),row('b','1','20170102','Class II')],[2017]);self.assertEqual(counts[0]['events'],1);self.assertEqual(sum(r['events'] for r in counts if r['panel']!='All'),2)
    def test_quantile_interpolation(self):self.assertEqual(q7([0,10,20,30],Fraction(19,20)),Fraction(57,2))
    def test_strict_boundary(self):self.assertEqual([flag(n,{'numerator':3,'denominator':1}) for n in [2,3,4]],[0,0,1])
    def test_own_grain_comparator(self):
        self.assertEqual(flag(10,{'numerator':4,'denominator':1}),1);self.assertEqual(flag(10,{'numerator':12,'denominator':1}),0)
    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Duplicate'):validate([row('a','1','20170101'),row('a','2','20170102')])
    def test_missing_month_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Missing month'):validate([row('a','1','20170101')])
    def test_unknown_class_rejected(self):
        with self.assertRaises(AssertionError):validate([row('a','1','20170101','Unknown')])

if __name__=='__main__':unittest.main()
