"""Считает заказы и выручку по связке «артикул - день» из sales.csv."""
import csv
import sys
from collections import defaultdict

STATUS_ALIASES = {"delivered": "delivered", "cancelled": "cancelled", "canceled": "cancelled"}


def parse_row(line):
    """Разбирает одну строку выгрузки.

    В нашем файле каждая строка целиком обёрнута в кавычки, поэтому обычный
    csv-ридер видит одно поле. В этом случае разбираем содержимое ещё раз.
    """
    fields = next(csv.reader([line]))
    if len(fields) == 1:
        fields = next(csv.reader([fields[0]]))
    return fields


def read_orders(path):
    """Читает выгрузку, убирает дубли и приводит статусы к двум значениям."""
    orders = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = f.read().splitlines()
    header = parse_row(lines[0])
    for line in lines[1:]:
        if not line.strip():
            continue
        row = dict(zip(header, (v.strip() for v in parse_row(line))))
        status = STATUS_ALIASES.get(row["status"].lower())
        if status is None:
            raise ValueError(f"Неизвестный статус {row['status']!r} в заказе {row['order_id']}")
        row["status"] = status
        if row["order_id"] in orders:
            if orders[row["order_id"]] != row:
                print(f"Заказ {row['order_id']} повторяется с другими данными, берём первую строку",
                      file=sys.stderr)
            continue
        orders[row["order_id"]] = row
    return list(orders.values())


def aggregate(orders):
    """Возвращает строки (sku, order_date, orders, revenue), отсортированные по sku и дате."""
    count = defaultdict(int)
    revenue = defaultdict(int)
    for o in orders:
        key = (o["sku"], o["order_date"])
        count[key] += 1
        if o["status"] == "delivered":
            revenue[key] += int(o["quantity"]) * int(o["price"])
    return [(sku, day, count[(sku, day)], revenue[(sku, day)]) for sku, day in sorted(count)]


def main(src="sales.csv", dst="daily_by_sku.csv"):
    rows = aggregate(read_orders(src))
    with open(dst, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "order_date", "orders", "revenue"])
        w.writerows(rows)
    print(f"Готово: {len(rows)} строк в {dst}")


if __name__ == "__main__":
    main(*sys.argv[1:3])