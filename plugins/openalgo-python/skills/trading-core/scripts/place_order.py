#!/usr/bin/env python3
"""
Place orders using OpenAlgo API.

Usage:
    python place_order.py --symbol RELIANCE --exchange NSE --action BUY --quantity 1 --product MIS
    python place_order.py --symbol SBIN --exchange NSE --action BUY --quantity 10 --product MIS --price-type LIMIT --price 750
    python place_order.py --symbol NIFTY30JAN25FUT --exchange NFO --action BUY --quantity 50 --product NRML
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
        print("Get your API key from OpenAlgo application and set it:")
        print("  Windows: setx OPENALGO_API_KEY \"your-api-key\"")
        print("  macOS/Linux: export OPENALGO_API_KEY=\"your-api-key\"")
        sys.exit(1)

    return api(api_key=api_key, host=host)


def place_order(symbol, exchange, action, quantity, product, price_type="MARKET",
                price=0, trigger_price=0, disclosed_quantity=0, strategy="PythonStrategy"):
    """
    Place an order using OpenAlgo API.

    Args:
        symbol: Trading symbol (e.g., RELIANCE, NIFTY30JAN25FUT)
        exchange: Exchange code (NSE, BSE, NFO, BFO, CDS, BCD, MCX)
        action: BUY or SELL
        quantity: Number of shares/lots
        product: Product type (CNC, NRML, MIS)
        price_type: Order type (MARKET, LIMIT, SL, SL-M)
        price: Limit price (for LIMIT/SL orders)
        trigger_price: Trigger price (for SL/SL-M orders)
        disclosed_quantity: Disclosed quantity
        strategy: Strategy name for tracking

    Returns:
        dict: API response with orderid and status
    """
    client = get_client()

    print(f"\nPlacing {action} order:")
    print(f"  Symbol: {symbol}")
    print(f"  Exchange: {exchange}")
    print(f"  Quantity: {quantity}")
    print(f"  Product: {product}")
    print(f"  Price Type: {price_type}")
    if price_type in ["LIMIT", "SL"]:
        print(f"  Price: {price}")
    if price_type in ["SL", "SL-M"]:
        print(f"  Trigger Price: {trigger_price}")

    try:
        response = client.placeorder(
            strategy=strategy,
            symbol=symbol,
            action=action,
            exchange=exchange,
            price_type=price_type,
            product=product,
            quantity=quantity,
            price=str(price) if price else "0",
            trigger_price=str(trigger_price) if trigger_price else "0",
            disclosed_quantity=str(disclosed_quantity) if disclosed_quantity else "0"
        )

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Order placed successfully!")
            print(f"  Order ID: {response.get('orderid')}")
        else:
            print(f"\n[ERROR] Order failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Place orders using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Market order
  python place_order.py --symbol RELIANCE --exchange NSE --action BUY --quantity 1 --product MIS

  # Limit order
  python place_order.py --symbol SBIN --exchange NSE --action BUY --quantity 10 --product MIS --price-type LIMIT --price 750

  # Stop loss order
  python place_order.py --symbol INFY --exchange NSE --action SELL --quantity 5 --product MIS --price-type SL --price 1500 --trigger-price 1505

  # F&O order
  python place_order.py --symbol NIFTY30JAN25FUT --exchange NFO --action BUY --quantity 50 --product NRML
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX", "NCDEX"],
                        help="Exchange code")
    parser.add_argument("--action", "-a", required=True, choices=["BUY", "SELL"], help="Order action")
    parser.add_argument("--quantity", "-q", type=int, required=True, help="Order quantity")
    parser.add_argument("--product", "-p", required=True, choices=["CNC", "NRML", "MIS"], help="Product type")
    parser.add_argument("--price-type", "-t", default="MARKET",
                        choices=["MARKET", "LIMIT", "SL", "SL-M"], help="Price type (default: MARKET)")
    parser.add_argument("--price", type=float, default=0, help="Limit price (for LIMIT/SL orders)")
    parser.add_argument("--trigger-price", type=float, default=0, help="Trigger price (for SL/SL-M orders)")
    parser.add_argument("--disclosed-quantity", type=int, default=0, help="Disclosed quantity")
    parser.add_argument("--strategy", default="PythonStrategy", help="Strategy name for tracking")

    args = parser.parse_args()

    place_order(
        symbol=args.symbol,
        exchange=args.exchange,
        action=args.action,
        quantity=args.quantity,
        product=args.product,
        price_type=args.price_type,
        price=args.price,
        trigger_price=args.trigger_price,
        disclosed_quantity=args.disclosed_quantity,
        strategy=args.strategy
    )


if __name__ == "__main__":
    main()
