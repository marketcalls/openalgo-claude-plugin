#!/usr/bin/env python3
"""
Place smart orders that consider current position using OpenAlgo API.

Usage:
    python smart_order.py --symbol TATAMOTORS --exchange NSE --action SELL --quantity 5 --position-size 10
    python smart_order.py --symbol SBIN --exchange NSE --action BUY --quantity 10 --position-size 0 --product MIS
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


def smart_order(symbol, exchange, action, quantity, position_size, product="MIS",
                price_type="MARKET", strategy="SmartStrategy"):
    """
    Place a smart order that considers current position.

    The smart order automatically adjusts the order quantity based on the
    current position to reach the desired position_size.

    Args:
        symbol: Trading symbol
        exchange: Exchange code
        action: BUY or SELL
        quantity: Order quantity
        position_size: Desired final position size
        product: Product type (CNC, NRML, MIS)
        price_type: Order type (MARKET, LIMIT)
        strategy: Strategy name for tracking

    Example:
        If current position is 0 and you want position_size=5 with action=BUY:
        - Order will buy 5 to reach position of 5

        If current position is 3 and you want position_size=-5 with action=SELL:
        - Order will sell 8 to reach position of -5

    Returns:
        dict: API response with orderid and status
    """
    client = get_client()

    print(f"\nPlacing Smart {action} order:")
    print(f"  Symbol: {symbol}")
    print(f"  Exchange: {exchange}")
    print(f"  Quantity: {quantity}")
    print(f"  Target Position Size: {position_size}")
    print(f"  Product: {product}")
    print(f"  Price Type: {price_type}")

    try:
        response = client.placesmartorder(
            strategy=strategy,
            symbol=symbol,
            action=action,
            exchange=exchange,
            price_type=price_type,
            product=product,
            quantity=quantity,
            position_size=position_size
        )

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Smart order placed successfully!")
            print(f"  Order ID: {response.get('orderid')}")
        else:
            print(f"\n[ERROR] Order failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Place smart orders using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Smart Order Logic:
  The smart order adjusts quantity based on current position to reach target position_size.

Examples:
  # Build long position
  python smart_order.py --symbol RELIANCE --exchange NSE --action BUY --quantity 10 --position-size 10

  # Reverse position (if currently long 5, will sell 10 to go short 5)
  python smart_order.py --symbol TATAMOTORS --exchange NSE --action SELL --quantity 5 --position-size -5

  # Scale into position
  python smart_order.py --symbol SBIN --exchange NSE --action BUY --quantity 5 --position-size 15

  # Square off (set position-size to 0)
  python smart_order.py --symbol INFY --exchange NSE --action SELL --quantity 10 --position-size 0
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX", "NCDEX"],
                        help="Exchange code")
    parser.add_argument("--action", "-a", required=True, choices=["BUY", "SELL"], help="Order action")
    parser.add_argument("--quantity", "-q", type=int, required=True, help="Order quantity")
    parser.add_argument("--position-size", "-ps", type=int, required=True,
                        help="Target position size (can be negative for short)")
    parser.add_argument("--product", "-p", default="MIS", choices=["CNC", "NRML", "MIS"], help="Product type")
    parser.add_argument("--price-type", "-t", default="MARKET", choices=["MARKET", "LIMIT"], help="Price type")
    parser.add_argument("--strategy", default="SmartStrategy", help="Strategy name")

    args = parser.parse_args()

    smart_order(
        symbol=args.symbol,
        exchange=args.exchange,
        action=args.action,
        quantity=args.quantity,
        position_size=args.position_size,
        product=args.product,
        price_type=args.price_type,
        strategy=args.strategy
    )


if __name__ == "__main__":
    main()
