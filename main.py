# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"

# Your code below this line.
# Imports
from pathlib import Path
from datetime import datetime, timedelta
import argparse
from rich.console import Console
from rich.table import Table

# -----------------------
# Initialize Rich Console
# -----------------------
console = Console()  # Rich library console for colored output and tables

# -----------------------
# File paths
# -----------------------
DATA_DIR = Path("data")  # Directory to store data files
BOUGHT_FILE_CSV = DATA_DIR / "bought.csv"
SOLD_FILE_CSV = DATA_DIR / "sold.csv"
DATE_FILE = DATA_DIR / "current_date.txt"

# -----------------------
# Utility Functions
# -----------------------

def ensure_data_files():
    """
    Ensure that the data directory and required files exist.
    If missing, create empty CSV files with headers and a date file.
    """
    DATA_DIR.mkdir(exist_ok=True)

    # Create bought.csv if missing
    if not BOUGHT_FILE_CSV.exists():
        pd.DataFrame(columns=["id", "product_name", "buy_date", "buy_price", "expiration_date"]).to_csv(BOUGHT_FILE_CSV, index=False)

    # Create sold.csv if missing
    if not SOLD_FILE_CSV.exists():
        pd.DataFrame(columns=["id", "bought_id", "sell_date", "sell_price"]).to_csv(SOLD_FILE_CSV, index=False)

    # Create current_date.txt if missing
    if not DATE_FILE.exists():
        DATE_FILE.write_text(datetime.today().strftime("%Y-%m-%d"))

def get_current_date():
    """Return the current date stored in current_date.txt."""
    return datetime.strptime(DATE_FILE.read_text().strip(), "%Y-%m-%d").date()

def set_current_date(date):
    """Set the current date by writing to current_date.txt."""
    DATE_FILE.write_text(date.strftime("%Y-%m-%d"))

def advance_time(days):
    """
    Advance the current date by a given number of days.
    """
    new_date = get_current_date() + timedelta(days=days)
    set_current_date(new_date)
    console.print(f"[green]OK[/green] - New date: {new_date}")

# -----------------------
# File Handling (CSV, Excel, JSON)
# -----------------------

def read_data(file_path: Path):
    """
    Read a data file (CSV, Excel, JSON) into a pandas DataFrame.
    """
    ext = file_path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file type. Use CSV, Excel, or JSON.")

def write_data(df: pd.DataFrame, file_path: Path):
    """
    Write a pandas DataFrame to a file (CSV, Excel, JSON).
    """
    ext = file_path.suffix.lower()
    if ext == ".csv":
        df.to_csv(file_path, index=False)
    elif ext in [".xls", ".xlsx"]:
        df.to_excel(file_path, index=False)
    elif ext == ".json":
        df.to_json(file_path, orient="records", indent=4)
    else:
        raise ValueError("Unsupported file type. Use CSV, Excel, or JSON.")

def get_next_id(df: pd.DataFrame):
    """
    Get the next sequential ID for a new row.
    """
    return 0 if df.empty else df["id"].max() + 1

def is_in_period(date, today, period):
    """
    Check if a given date falls within a specified period relative to today.
    Period can be day, week, month, or year.
    """
    if period == "day":
        return date == today
    elif period == "week":
        return date.isocalendar()[:2] == today.isocalendar()[:2]
    elif period == "month":
        return date.year == today.year and date.month == today.month
    elif period == "year":
        return date.year == today.year
    return False

# -----------------------
# Core Features
# -----------------------

def buy(product_name, price, expiration_date, file_format="csv"):
    """
    Add a product to inventory (bought file).
    """
    ensure_data_files()
    current_date = get_current_date()
    file_path = DATA_DIR / f"bought.{file_format}"
    
    df = read_data(file_path) if file_path.exists() else pd.DataFrame(columns=["id", "product_name", "buy_date", "buy_price", "expiration_date"])
    new_id = get_next_id(df)
    
    df.loc[len(df)] = [new_id, product_name, current_date.strftime("%Y-%m-%d"), price, expiration_date]
    write_data(df, file_path)
    
    console.print(f"[green]OK[/green] - Bought {product_name} on {current_date} ({file_format.upper()})")

def sell(product_name, price, file_format="csv"):
    """
    Sell a product from inventory (move to sold file).
    """
    ensure_data_files()
    current_date = get_current_date()
    
    bought_path = DATA_DIR / f"bought.{file_format}"
    sold_path = DATA_DIR / f"sold.{file_format}"
    
    bought_df = read_data(bought_path)
    sold_df = read_data(sold_path) if sold_path.exists() else pd.DataFrame(columns=["id", "bought_id", "sell_date", "sell_price"])
    
    sold_ids = set(sold_df["bought_id"].astype(str))
    
    for idx, item in bought_df.iterrows():
        if item["product_name"] == product_name and str(item["id"]) not in sold_ids:
            new_id = get_next_id(sold_df)
            sold_df.loc[len(sold_df)] = [new_id, item["id"], current_date.strftime("%Y-%m-%d"), price]
            write_data(sold_df, sold_path)
            console.print(f"[green]OK[/green] - Sold {product_name} on {current_date} ({file_format.upper()})")
            return
    
    console.print("[red]ERROR[/red]: Product not in stock.")

# -----------------------
# Reports
# -----------------------

def report_inventory(file_format="csv", export_path=None):
    """
    Show current inventory in a Rich table.
    Can export inventory to CSV, Excel, or JSON.
    """
    bought_path = DATA_DIR / f"bought.{file_format}"
    sold_path = DATA_DIR / f"sold.{file_format}"

    bought_df = read_data(bought_path)
    sold_df = read_data(sold_path) if sold_path.exists() else pd.DataFrame(columns=["id", "bought_id", "sell_date", "sell_price"])
    
    sold_ids = set(sold_df["bought_id"].astype(str))
    inventory_df = bought_df[~bought_df["id"].astype(str).isin(sold_ids)]
    
    # Rich table
    table = Table(title="Inventory Report")
    table.add_column("Product Name", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Buy Price", justify="right")
    table.add_column("Expiration Date", justify="center")
    
    for name, group in inventory_df.groupby("product_name"):
        table.add_row(name, str(len(group)), str(group['buy_price'].iloc[0]), str(group['expiration_date'].iloc[0]))
    
    console.print(table)

    # Export report if path provided
    if export_path:
        write_data(inventory_df, Path(export_path))
        console.print(f"[green]Report exported to {export_path}[/green]")

def report_revenue(period, file_format="csv", export_path=None):
    """
    Calculate total revenue for a given period.
    Can export revenue report to CSV, Excel, or JSON.
    """
    sold_path = DATA_DIR / f"sold.{file_format}"
    sold_df = read_data(sold_path)
    
    today = get_current_date()
    sold_df["sell_date"] = pd.to_datetime(sold_df["sell_date"]).dt.date
    filtered = sold_df[sold_df["sell_date"].apply(lambda d: is_in_period(d, today, period))]
    revenue = filtered["sell_price"].sum()
    
    console.print(f"[bold yellow]{period.capitalize()} revenue: {revenue}[/bold yellow]")
    
    if export_path:
        write_data(filtered, Path(export_path))
        console.print(f"[green]Revenue report exported to {export_path}[/green]")

def report_profit(period, file_format="csv", export_path=None):
    """
    Calculate total profit (sell_price - buy_price) for a given period.
    Can export profit report to CSV, Excel, or JSON.
    """
    bought_path = DATA_DIR / f"bought.{file_format}"
    sold_path = DATA_DIR / f"sold.{file_format}"
    
    bought_df = read_data(bought_path).set_index("id")
    sold_df = read_data(sold_path)
    
    today = get_current_date()
    sold_df["sell_date"] = pd.to_datetime(sold_df["sell_date"]).dt.date
    
    profit_list = []
    total_profit = 0
    for _, row in sold_df.iterrows():
        if is_in_period(row["sell_date"], today, period):
            buy_price = float(bought_df.at[row["bought_id"], "buy_price"])
            sell_price = float(row["sell_price"])
            profit = sell_price - buy_price
            total_profit += profit
            profit_list.append({**row.to_dict(), "profit": profit})
    
    console.print(f"[bold yellow]{period.capitalize()} profit: {total_profit}[/bold yellow]")
    
    if export_path:
        write_data(pd.DataFrame(profit_list), Path(export_path))
        console.print(f"[green]Profit report exported to {export_path}[/green]")

# -----------------------
# Data Conversion
# -----------------------

def convert_data(file_type: str, target_format: str):
    """
    Convert bought/sold files to another format (csv, xlsx, json).
    """
    file_type = file_type.lower()
    target_format = target_format.lower()
    
    if file_type not in ["bought", "sold"]:
        console.print("[red]ERROR:[/red] file_type must be 'bought' or 'sold'")
        return
    
    source_file = DATA_DIR / f"{file_type}.csv"
    if not source_file.exists():
        console.print(f"[red]ERROR:[/red] Source file {source_file} does not exist.")
        return
    
    df = read_data(source_file)
    target_file = DATA_DIR / f"{file_type}.{target_format}"
    write_data(df, target_file)
    console.print(f"[green]OK:[/green] {file_type} file converted to {target_file}")

# -----------------------
# CLI Setup
# -----------------------

def main():
    parser = argparse.ArgumentParser(description="SuperPy Inventory Tool (Rich + Multi-format Reports)")
    
    parser.add_argument("--set-date", type=str, help="Set current date (YYYY-MM-DD)")
    parser.add_argument("--advance-time", type=int, help="Advance time by days")
    parser.add_argument("--format", type=str, choices=["csv", "xlsx", "json"], default="csv", help="Data file format")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Buy command
    buy_parser = subparsers.add_parser("buy")
    buy_parser.add_argument("--product-name", required=True)
    buy_parser.add_argument("--price", type=float, required=True)
    buy_parser.add_argument("--expiration-date", required=True)
    
    # Sell command
    sell_parser = subparsers.add_parser("sell")
    sell_parser.add_argument("--product-name", required=True)
    sell_parser.add_argument("--price", type=float, required=True)
    
    # Report command
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("type", choices=["inventory", "revenue", "profit"])
    report_parser.add_argument("--period", choices=["day", "week", "month", "year"], default="day")
    report_parser.add_argument("--export", type=str, help="Export report to file (csv/json/xlsx)")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert bought/sold files to another format")
    convert_parser.add_argument("--file", choices=["bought", "sold"], required=True, help="File to convert")
    convert_parser.add_argument("--to", choices=["csv", "xlsx", "json"], required=True, help="Target format")
    
    args = parser.parse_args()
    ensure_data_files()
    
    # Handle commands
    if args.set_date:
        set_current_date(datetime.strptime(args.set_date, "%Y-%m-%d").date())
        console.print(f"[green]Current date set to: {get_current_date()}[/green]")
    elif args.advance_time:
        advance_time(args.advance_time)
    elif args.command == "buy":
        buy(args.product_name, args.price, args.expiration_date, args.format)
    elif args.command == "sell":
        sell(args.product_name, args.price, args.format)
    elif args.command == "report":
        if args.type == "inventory":
            report_inventory(args.format, args.export)
        elif args.type == "revenue":
            report_revenue(args.period, args.format, args.export)
        elif args.type == "profit":
            report_profit(args.period, args.format, args.export)
    elif args.command == "convert":
        convert_data(args.file, args.to)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

