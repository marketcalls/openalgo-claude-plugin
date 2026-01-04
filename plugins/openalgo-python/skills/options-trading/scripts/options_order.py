#!/usr/bin/env python3
"""
Place single-leg options orders using OpenAlgo API.

Usage:
    python options_order.py --underlying NIFTY --expiry 30JAN25 --offset ATM --option-type CE --action BUY --quantity 75
    python options_order.py --underlying BANKNIFTY --expiry 30JAN25 --offset OTM3 --option-type PE --action SELL --quantity 30
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


def options_order(underlying, expiry_date, offset, option_type, action, quantity,
                  exchange="NSE_INDEX", product="NRML", pricetype="MARKET",
                  splitsize=0, strategy="OptionsStrategy"):
    """
    Place a single-leg options order using OpenAlgo API.

    Args:
        underlying: Underlying symbol (NIFTY, BANKNIFTY, FINNIFTY, or stock symbol)
        expiry_date: Expiry date in DDMMMYY format (e.g., 30JAN25)
        offset: Strike offset (ATM, ITM1-10, OTM1-10)
        option_type: CE (Call) or PE (Put)
        action: BUY or SELL
        quantity: Number of lots * lot size
        exchange: Exchange code (NSE_INDEX, BSE_INDEX, NSE for stocks)
        product: NRML (overnight) or MIS (intraday)
        pricetype: MARKET or LIMIT
        splitsize: Max quantity per order (0 = no splitting)
        strategy: Strategy name for tracking

    Returns:
        dict: API response with orderid, symbol, and execution details
    """
    client = get_client()

    print(f"\nPlacing Options Order:")
    print(f"  Underlying: {underlying}")
    print(f"  Expiry: {expiry_date}")
    print(f"  Offset: {offset}")
    print(f"  Option Type: {option_type}")
    print(f"  Action: {action}")
    print(f"  Quantity: {quantity}")
    print(f"  Product: {product}")

    try:
        response = client.optionsorder(
            strategy=strategy,
            underlying=underlying,
            exchange=exchange,
            expiry_date=expiry_date,
            offset=offset,
            option_type=option_type,
            action=action,
            quantity=quantity,
            pricetype=pricetype,
            product=product,
            splitsize=splitsize
        )

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Options order placed!")
            print(f"  Order ID: {response.get('orderid')}")
            print(f"  Symbol: {response.get('symbol')}")
            print(f"  Exchange: {response.get('exchange')}")
            print(f"  Underlying LTP: {response.get('underlying_ltp')}")
        else:
            print(f"\n[ERROR] Order failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Place single-leg options orders using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Offset Examples:
  ATM    - At The Money strike
  ITM1   - 1 strike In The Money
  ITM5   - 5 strikes In The Money
  OTM1   - 1 strike Out of The Money
  OTM5   - 5 strikes Out of The Money

Common Lot Sizes:
  NIFTY: 75, BANKNIFTY: 30, FINNIFTY: 65

Examples:
  # Buy ATM NIFTY Call
  python options_order.py --underlying NIFTY --expiry 30JAN25 --offset ATM --option-type CE --action BUY --quantity 75

  # Sell OTM BANKNIFTY Put
  python options_order.py --underlying BANKNIFTY --expiry 30JAN25 --offset OTM5 --option-type PE --action SELL --quantity 30

  # Buy ITM NIFTY Put
  python options_order.py --underlying NIFTY --expiry 30JAN25 --offset ITM3 --option-type PE --action BUY --quantity 75

  # Stock option
  python options_order.py --underlying RELIANCE --exchange NSE --expiry 30JAN25 --offset ATM --option-type CE --action BUY --quantity 250
        """
    )

    parser.add_argument("--underlying", "-u", required=True, help="Underlying symbol (NIFTY, BANKNIFTY, etc.)")
    parser.add_argument("--expiry", "-e", required=True, help="Expiry date (DDMMMYY format, e.g., 30JAN25)")
    parser.add_argument("--offset", "-o", required=True, help="Strike offset (ATM, ITM1-10, OTM1-10)")
    parser.add_argument("--option-type", "-t", required=True, choices=["CE", "PE"], help="Option type")
    parser.add_argument("--action", "-a", required=True, choices=["BUY", "SELL"], help="Order action")
    parser.add_argument("--quantity", "-q", type=int, required=True, help="Order quantity (should be multiple of lot size)")
    parser.add_argument("--exchange", default="NSE_INDEX",
                        choices=["NSE_INDEX", "BSE_INDEX", "NSE", "BSE"],
                        help="Exchange (default: NSE_INDEX)")
    parser.add_argument("--product", "-p", default="NRML", choices=["NRML", "MIS"], help="Product type")
    parser.add_argument("--pricetype", default="MARKET", choices=["MARKET", "LIMIT"], help="Price type")
    parser.add_argument("--splitsize", type=int, default=0, help="Split size for large orders (0 = no split)")
    parser.add_argument("--strategy", default="OptionsStrategy", help="Strategy name")

    args = parser.parse_args()

    options_order(
        underlying=args.underlying,
        expiry_date=args.expiry,
        offset=args.offset,
        option_type=args.option_type,
        action=args.action,
        quantity=args.quantity,
        exchange=args.exchange,
        product=args.product,
        pricetype=args.pricetype,
        splitsize=args.splitsize,
        strategy=args.strategy
    )


if __name__ == "__main__":
    main()
