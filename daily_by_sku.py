"""Считает заказы и выручку по связке «артикул - день» из sales.csv."""
import csv


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
    """Читает выгрузку и возвращает список заказов (словарей)."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        lines = f.read().splitlines()
    header = parse_row(lines[0])
    orders = []
    for line in lines[1:]:
        if not line.strip():
            continue
        orders.append(dict(zip(header, (v.strip() for v in parse_row(line)))))
    return orders


if __name__ == "__main__":
    print(len(read_orders("sales.csv")))