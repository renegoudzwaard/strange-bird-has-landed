# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.
# Imports
import csv
import argparse
from datetime import datetime, timedelta
import os

DATA_DIR = "data"
BOUGHT_FILE = os.path.join(DATA_DIR, "bought.csv")
SOLD_FILE = os.path.join(DATA_DIR, "sold.csv")
DATE_FILE = os.path.join(DATA_DIR, "current_date.txt")

# -----------------------
# Utility Functions
# -----------------------

def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(BOUGHT_FILE):
        with open(BOUGHT_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "product_name", "buy_date", "buy_price", "expiration_date"])

    if not os.path.exists(SOLD_FILE):
        with open(SOLD_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "bought_id", "sell_date", "sell_price"])

    if not os.path.exists(DATE_FILE):
        with open(DATE_FILE, "w") as f:
            f.write(datetime.today().strftime("%Y-%m-%d"))

def get_current_date():
    with open(DATE_FILE, "r") as f:
        return datetime.strptime(f.read().strip(), "%Y-%m-%d").date()

def set_current_date(date):
    with open(DATE_FILE, "w") as f:
        f.write(date.strftime("%Y-%m-%d"))

def advance_time(days):
    current = get_current_date()
    new_date = current + timedelta(days=days)
    set_current_date(new_date)
    print("OK")

def get_next_id(file):
    with open(file, "r") as f:
        reader = list(csv.reader(f))
        return len(reader)

# -----------------------
# Core Features
# -----------------------

def buy(product_name, price, expiration_date):
    ensure_data_files()
    current_date = get_current_date()

    with open(BOUGHT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            get_next_id(BOUGHT_FILE),
            product_name,
            current_date,
            price,
            expiration_date
        ])

    print("OK")

def sell(product_name, price):
    ensure_data_files()
    current_date = get_current_date()

    with open(BOUGHT_FILE, "r") as f:
        bought = list(csv.DictReader(f))

    with open(SOLD_FILE, "r") as f:
        sold = list(csv.DictReader(f))

    sold_ids = {row["bought_id"] for row in sold}

    for item in bought:
        if item["product_name"] == product_name and item["id"] not in sold_ids:
            with open(SOLD_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    get_next_id(SOLD_FILE),
                    item["id"],
                    current_date,
                    price
                ])
            print("OK")
            return

    print("ERROR: Product not in stock.")

# -----------------------
# Reports
# -----------------------

def report_inventory():
    ensure_data_files()

    with open(BOUGHT_FILE, "r") as f:
        bought = list(csv.DictReader(f))

    with open(SOLD_FILE, "r") as f:
        sold = list(csv.DictReader(f))

    sold_ids = {row["bought_id"] for row in sold}

    inventory = {}

    for item in bought:
        if item["id"] not in sold_ids:
            name = item["product_name"]
            inventory.setdefault(name, []).append(item)

    print("+--------------+-------+-----------+-----------------+")
    print("| Product Name | Count | Buy Price | Expiration Date |")
    print("+==============+=======+===========+=================+")

    for name, items in inventory.items():
        print(f"| {name:<12} | {len(items):<5} | {items[0]['buy_price']:<9} | {items[0]['expiration_date']} |")

    print("+--------------+-------+-----------+-----------------+")

def report_revenue():
    ensure_data_files()

    today = get_current_date()

    with open(SOLD_FILE, "r") as f:
        sold = list(csv.DictReader(f))

    revenue = 0
    for item in sold:
        if datetime.strptime(item["sell_date"], "%Y-%m-%d").date() == today:
            revenue += float(item["sell_price"])

    print(f"Today's revenue: {revenue}")

def report_profit():
    ensure_data_files()

    with open(SOLD_FILE, "r") as f:
        sold = list(csv.DictReader(f))

    with open(BOUGHT_FILE, "r") as f:
        bought = {row["id"]: row for row in csv.DictReader(f)}

    profit = 0

    for item in sold:
        buy_price = float(bought[item["bought_id"]]["buy_price"])
        sell_price = float(item["sell_price"])
        profit += (sell_price - buy_price)

    print(f"Total profit: {profit}")

# -----------------------
# CLI Setup
# -----------------------

def main():
    parser = argparse.ArgumentParser(description="SuperPy Inventory Tool")

    parser.add_argument("--advance-time", type=int, help="Advance time by days")

    subparsers = parser.add_subparsers(dest="command")

    # Buy
    buy_parser = subparsers.add_parser("buy")
    buy_parser.add_argument("--product-name", required=True)
    buy_parser.add_argument("--price", type=float, required=True)
    buy_parser.add_argument("--expiration-date", required=True)

    # Sell
    sell_parser = subparsers.add_parser("sell")
    sell_parser.add_argument("--product-name", required=True)
    sell_parser.add_argument("--price", type=float, required=True)

    # Reports
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("type", choices=["inventory", "revenue", "profit"])

    args = parser.parse_args()

    ensure_data_files()

    if args.advance_time:
        advance_time(args.advance_time)
    elif args.command == "buy":
        buy(args.product_name, args.price, args.expiration_date)
    elif args.command == "sell":
        sell(args.product_name, args.price)
    elif args.command == "report":
        if args.type == "inventory":
            report_inventory()
        elif args.type == "revenue":
            report_revenue()
        elif args.type == "profit":
            report_profit()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
