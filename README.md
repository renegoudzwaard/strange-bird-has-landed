# strange-bird-has-landed

# SuperPy Inventory Management CLI

SuperPy is a command-line inventory management tool and is designed for small businesses, hobbyists, or anyone needing to track products, sales, and revenue efficiently.
This version uses Rich for enhanced terminal output and supports multiple data formats, including CSV, Excel, and JSON, making it both user-friendly and flexible.


## Features

- Add and sell products:
  Can be used for tracking your inventory with automatic date handling.
- Time manipulation: 
  Can be used for setting or advance the system date to simulate business operations.
- Comprehensive reports: 
  Can be used for generating inventory, revenue, and profit reports in a readable Rich table format.
- Multi-format support: 
  Can be used for importing and exporting data and reports in CSV, Excel, or JSON.
- Data conversion: 
  Can be used for converting existing CSV files to Excel or JSON effortlessly.


## Technical Highlights

1. Rich Library for Enhanced CLI Experience
Problem solved: 
Traditional CLI outputs can be difficult to read, especially with large inventories or complex reports.  
Implementation choice: 
Using Rich, all tables and messages are visually enhanced with colors, borders, and formatting.  
Benefit: 
Users can instantly identify key information, such as product counts, profits, and revenue trends, without manually parsing raw data.

2. Multi-format Data Handling (CSV, Excel, JSON)
Problem solved: 
Many inventory tools lock you into a single file format, limiting compatibility with other software like Excel or data analytics tools.  
Implementation choice: 
The program uses pandas to read and write CSV, Excel, and JSON formats seamlessly.  
Benefit: 
Users can export reports or convert existing files to the format they need, ensuring flexibility for analysis, backups, or sharing with partners.

3. Automated Inventory and Sales Linking
Problem solved: 
Manually tracking which products are sold and which are available can be error-prone.  
Implementation choice: 
Each product has a unique ID, and sold items are linked to their purchase record.  
Benefit: 
This allows accurate profit calculation and ensures the inventory report always reflects unsold products, eliminating mistakes and double-counting.


## Installation

```bash
git clone <repository-url>
cd superpy
pip install pandas rich openpyxl


Usage Examples:

Add a new product
python superpy.py buy --product-name Milk --price 1.20 --expiration-date 2026-06-16

Sell a product
python superpy.py sell --product-name Milk --price 1.90

Advance the current date by 7 days
python superpy.py --advance-time 7

Generate an inventory report
python superpy.py report inventory

Generate a revenue report for the week and export to Excel
python superpy.py report revenue --period week --export revenue_week.xlsx

Convert bought.csv to JSON
python superpy.py convert --file bought --to json

CLI Output Examples
Inventory Report (Rich Table)
=================================================
= Product name = Count = Buy Price = Expiration =
= Milk	       = 10    = 1.2       = 2026-06-16 =
= Eggs	       = 30    = 0.2	   = 2026-06-03 =
= Bread	       = 5     = 1.0	   = 2026-06-12 =
=================================================

Revenue Report
[bold yellow]Week revenue: 45.50[/bold yellow]

Profit Report
[bold yellow]Week profit: 12.75[/bold yellow]

Note: 
Actual CLI will display these tables with color formatting and borders via Rich.

Why Choose SuperPy?
Readable output with Rich makes management tasks intuitive.
Multi-format support ensures interoperability with other tools.
Automated linking of sales to purchases provides accurate financial reports and reduces human errors.
The CLI approach makes it fast and lightweight—no GUI overhead.

SuperPy is perfect for small business owners, hobbyists, or anyone needing accurate, flexible, and visually appealing inventory management directly from the terminal.



