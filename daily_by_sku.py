"""Считает заказы и выручку по связке «артикул - день» из sales.csv."""
import csv
import sys

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


if __name__ == "__main__":
    print(len(read_orders("sales.csv")))