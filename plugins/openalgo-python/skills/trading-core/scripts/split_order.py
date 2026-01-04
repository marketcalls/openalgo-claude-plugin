#!/usr/bin/env python3
"""
Split large orders into smaller chunks using OpenAlgo API.

Usage:
    python split_order.py --symbol YESBANK --exchange NSE --action SELL --quantity 500 --split-size 100
    python split_order.py --symbol SBIN --exchange NSE --action BUY --quantity 1000 --split-size 200 --product MIS
"""

import os
import sys
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


def split_order(symbol, exchange, action, quantity, split_size, product="MIS", price_type="MARKET"):
    """
    Split a large order into smaller chunks to minimize market impact.

    This is useful for:
    - Large orders that might move the market
    - Avoiding freeze quantity limits
    - Better execution in illiquid stocks

    Args:
        symbol: Trading symbol
        exchange: Exchange code
        action: BUY or SELL
        quantity: Total quantity to trade
        split_size: Maximum quantity per order
        product: Product type (CNC, NRML, MIS)
        price_type: Order type (MARKET, LIMIT)

    Returns:
        dict: API response with results for each split order

    Example:
        quantity=500, split_size=100 creates:
        - Order 1: 100 qty
        - Order 2: 100 qty
        - Order 3: 100 qty
        - Order 4: 100 qty
        - Order 5: 100 qty
    """
    client = get_client()

    num_orders = (quantity + split_size - 1) // split_size
    print(f"\nSplit Order Details:")
    print(f"  Symbol: {symbol}")
    print(f"  Exchange: {exchange}")
    print(f"  Action: {action}")
    print(f"  Total Quantity: {quantity}")
    print(f"  Split Size: {split_size}")
    print(f"  Number of Orders: {num_orders}")
    print(f"  Product: {product}")

    try:
        response = client.splitorder(
            symbol=symbol,
            exchange=exchange,
            action=action,
            quantity=quantity,
            splitsize=split_size,
            price_type=price_type,
            product=product
        )

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Split order executed!")
            print(f"  Total Quantity: {response.get('total_quantity')}")
            print(f"  Split Size: {response.get('split_size')}")
            print(f"\n  Order Results:")
            for result in response.get('results', []):
                status_icon = "[OK]" if result.get('status') == 'success' else "[FAIL]"
                print(f"    {status_icon} Order {result.get('order_num')}: "
                      f"Qty={result.get('quantity')}, ID={result.get('orderid')}")
        else:
            print(f"\n[ERROR] Split order failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Split large orders into smaller chunks using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Why use split orders?
  - Minimize market impact on large orders
  - Stay within exchange freeze quantity limits
  - Better fills in illiquid stocks
  - TWAP-like execution

Examples:
  # Split 500 into 100 each
  python split_order.py --symbol YESBANK --exchange NSE --action SELL --quantity 500 --split-size 100

  # Split 1000 into 200 each for delivery
  python split_order.py --symbol SBIN --exchange NSE --action BUY --quantity 1000 --split-size 200 --product CNC

  # F&O split order (respecting lot size)
  python split_order.py --symbol NIFTY30JAN25FUT --exchange NFO --action BUY --quantity 500 --split-size 50 --product NRML
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX", "NCDEX"],
                        help="Exchange code")
    parser.add_argument("--action", "-a", required=True, choices=["BUY", "SELL"], help="Order action")
    parser.add_argument("--quantity", "-q", type=int, required=True, help="Total quantity")
    parser.add_argument("--split-size", "-ss", type=int, required=True, help="Max quantity per order")
    parser.add_argument("--product", "-p", default="MIS", choices=["CNC", "NRML", "MIS"], help="Product type")
    parser.add_argument("--price-type", "-t", default="MARKET", choices=["MARKET", "LIMIT"], help="Price type")

    args = parser.parse_args()

    split_order(
        symbol=args.symbol,
        exchange=args.exchange,
        action=args.action,
        quantity=args.quantity,
        split_size=args.split_size,
        product=args.product,
        price_type=args.price_type
    )


if __name__ == "__main__":
    main()
