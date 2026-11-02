import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from daily_by_sku import aggregate, read_orders

HEADER = "order_id,order_date,sku,quantity,price,status"


def load(lines, quote_rows=True):
    text = "\r\n".join(f'"{l}"' if quote_rows else l for l in [HEADER] + lines) + "\r\n"
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(text)
    try:
        return aggregate(read_orders(f.name))
    finally:
        os.remove(f.name)


class DailyBySkuTest(unittest.TestCase):
    def test_revenue_only_delivered_orders_count_all(self):
        rows = load(["1,2026-09-01,A,2,100,delivered", "2,2026-09-01,A,1,100,cancelled"])
        self.assertEqual(rows, [("A", "2026-09-01", 2, 200)])

    def test_duplicate_counted_once(self):
        rows = load(["1,2026-09-01,A,1,100,delivered"] * 2)
        self.assertEqual(rows, [("A", "2026-09-01", 1, 100)])

    def test_status_variants(self):
        rows = load(["1,2026-09-01,A,1,100,Delivered ", "2,2026-09-01,A,1,100,CANCELED"])
        self.assertEqual(rows, [("A", "2026-09-01", 2, 100)])

    def test_missing_quantity_cancelled(self):
        rows = load(["1,2026-09-01,A,,100,cancelled"])
        self.assertEqual(rows, [("A", "2026-09-01", 1, 0)])

    def test_sorting(self):
        rows = load(["1,2026-09-02,B,1,10,delivered", "2,2026-09-02,A,1,10,delivered",
                     "3,2026-09-01,A,1,10,delivered"])
        self.assertEqual([r[:2] for r in rows],
                         [("A", "2026-09-01"), ("A", "2026-09-02"), ("B", "2026-09-02")])

    def test_unquoted_rows_also_work(self):
        rows = load(["1,2026-09-01,A,1,100,delivered"], quote_rows=False)
        self.assertEqual(rows, [("A", "2026-09-01", 1, 100)])


if __name__ == "__main__":
    unittest.main()