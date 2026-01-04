#!/usr/bin/env python3
"""
Place basket orders (multiple orders simultaneously) using OpenAlgo API.

Usage:
    python basket_order.py --file orders.json
    python basket_order.py --orders '[{"symbol":"INFY","exchange":"NSE","action":"BUY","quantity":1,"pricetype":"MARKET","product":"MIS"}]'
"""

import os
import sys
import json
import argparse
from openalgo import api


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host)


def basket_order(orders):
    """
    Place multiple orders simultaneously using OpenAlgo API.

    Args:
        orders: List of order dictionaries, each containing:
            - symbol: Trading symbol
            - exchange: Exchange code (NSE, BSE, NFO, etc.)
            - action: BUY or SELL
            - quantity: Order quantity
            - pricetype: MARKET, LIMIT, SL, SL-M
            - product: CNC, NRML, MIS
            - price: (optional) Limit price
            - trigger_price: (optional) Trigger price

    Returns:
        dict: API response with status for each order

    Example orders:
        [
            {"symbol": "INFY", "exchange": "NSE", "action": "BUY", "quantity": 1, "pricetype": "MARKET", "product": "MIS"},
            {"symbol": "TCS", "exchange": "NSE", "action": "BUY", "quantity": 1, "pricetype": "MARKET", "product": "MIS"},
            {"symbol": "WIPRO", "exchange": "NSE", "action": "SELL", "quantity": 1, "pricetype": "MARKET", "product": "MIS"}
        ]
    """
    client = get_client()

    print(f"\nPlacing Basket Order with {len(orders)} orders:")
    for i, order in enumerate(orders, 1):
        print(f"  {i}. {order['action']} {order['quantity']} {order['symbol']} @ {order.get('pricetype', 'MARKET')}")

    try:
        response = client.basketorder(orders=orders)

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Basket order executed!")
            for result in response.get('results', []):
                status_icon = "[OK]" if result.get('status') == 'success' else "[FAIL]"
                print(f"  {status_icon} {result.get('symbol')}: {result.get('orderid', 'N/A')}")
        else:
            print(f"\n[ERROR] Basket order failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def create_sector_basket(sector, action, quantity_per_stock, product="MIS"):
    """
    Create a basket of orders for a specific sector.

    Args:
        sector: Sector name (IT, BANKING, AUTO, PHARMA, ENERGY)
        action: BUY or SELL
        quantity_per_stock: Quantity for each stock
        product: Product type

    Returns:
        list: List of order dictionaries
    """
    sectors = {
        "IT": ["INFY", "TCS", "WIPRO", "HCLTECH", "TECHM"],
        "BANKING": ["HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK"],
        "AUTO": ["TATAMOTORS", "MARUTI", "M&M", "BAJAJ-AUTO", "HEROMOTOCO"],
        "PHARMA": ["SUNPHARMA", "DRREDDY", "CIPLA", "DIVISLAB", "APOLLOHOSP"],
        "ENERGY": ["RELIANCE", "ONGC", "NTPC", "POWERGRID", "ADANIGREEN"]
    }

    if sector.upper() not in sectors:
        print(f"Unknown sector: {sector}. Available: {list(sectors.keys())}")
        return []

    stocks = sectors[sector.upper()]
    orders = []

    for symbol in stocks:
        orders.append({
            "symbol": symbol,
            "exchange": "NSE",
            "action": action,
            "quantity": quantity_per_stock,
            "pricetype": "MARKET",
            "product": product
        })

    return orders


def main():
    parser = argparse.ArgumentParser(
        description="Place basket orders using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From JSON string
  python basket_order.py --orders '[{"symbol":"INFY","exchange":"NSE","action":"BUY","quantity":1,"pricetype":"MARKET","product":"MIS"},{"symbol":"TCS","exchange":"NSE","action":"BUY","quantity":1,"pricetype":"MARKET","product":"MIS"}]'

  # From JSON file
  python basket_order.py --file my_orders.json

  # Sector basket
  python basket_order.py --sector IT --action BUY --quantity 1

  # Banking sector sell
  python basket_order.py --sector BANKING --action SELL --quantity 5 --product MIS
        """
    )

    parser.add_argument("--orders", help="JSON string of orders")
    parser.add_argument("--file", "-f", help="JSON file containing orders")
    parser.add_argument("--sector", choices=["IT", "BANKING", "AUTO", "PHARMA", "ENERGY"],
                        help="Create sector basket")
    parser.add_argument("--action", choices=["BUY", "SELL"], help="Action for sector basket")
    parser.add_argument("--quantity", "-q", type=int, default=1, help="Quantity per stock for sector basket")
    parser.add_argument("--product", "-p", default="MIS", choices=["CNC", "NRML", "MIS"],
                        help="Product type for sector basket")

    args = parser.parse_args()

    orders = None

    if args.orders:
        orders = json.loads(args.orders)
    elif args.file:
        with open(args.file, 'r') as f:
            orders = json.load(f)
    elif args.sector and args.action:
        orders = create_sector_basket(args.sector, args.action, args.quantity, args.product)
    else:
        parser.error("Provide --orders, --file, or --sector with --action")

    if orders:
        basket_order(orders)


if __name__ == "__main__":
    main()
