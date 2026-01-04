#!/usr/bin/env python3
"""
Place Iron Condor strategy using OpenAlgo API.

Iron Condor is a 4-leg options strategy:
- Buy OTM Call (protection)
- Sell OTM Call (collect premium)
- Buy OTM Put (protection)
- Sell OTM Put (collect premium)

Usage:
    python iron_condor.py --underlying NIFTY --expiry 30JAN25 --quantity 75
    python iron_condor.py --underlying NIFTY --expiry 30JAN25 --quantity 75 --sell-offset 4 --buy-offset 6
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


def iron_condor(underlying, expiry_date, quantity, sell_offset=4, buy_offset=6,
                exchange="NSE_INDEX", product="NRML", strategy="Iron Condor"):
    """
    Place an Iron Condor strategy.

    Iron Condor Payoff:
    - Max Profit: Net premium received (when price stays between sold strikes)
    - Max Loss: Width between strikes - Premium received
    - Breakeven: Sold strike ± Premium received

    Args:
        underlying: Underlying symbol (NIFTY, BANKNIFTY)
        expiry_date: Expiry date in DDMMMYY format
        quantity: Quantity per leg (should be lot size)
        sell_offset: OTM offset for sold options (default: 4)
        buy_offset: OTM offset for bought options (default: 6)
        exchange: Exchange code
        product: NRML or MIS
        strategy: Strategy name

    Returns:
        dict: API response with all leg execution details
    """
    client = get_client()

    print(f"\nPlacing Iron Condor:")
    print(f"  Underlying: {underlying}")
    print(f"  Expiry: {expiry_date}")
    print(f"  Quantity: {quantity}")
    print(f"  Sell Strikes: OTM{sell_offset}")
    print(f"  Buy Strikes: OTM{buy_offset}")

    legs = [
        {"offset": f"OTM{buy_offset}", "option_type": "CE", "action": "BUY", "quantity": quantity},
        {"offset": f"OTM{buy_offset}", "option_type": "PE", "action": "BUY", "quantity": quantity},
        {"offset": f"OTM{sell_offset}", "option_type": "CE", "action": "SELL", "quantity": quantity},
        {"offset": f"OTM{sell_offset}", "option_type": "PE", "action": "SELL", "quantity": quantity}
    ]

    print(f"\n  Legs:")
    for i, leg in enumerate(legs, 1):
        print(f"    {i}. {leg['action']} {leg['option_type']} @ {leg['offset']}")

    try:
        response = client.optionsmultiorder(
            strategy=strategy,
            underlying=underlying,
            exchange=exchange,
            expiry_date=expiry_date,
            legs=legs,
            product=product,
            pricetype="MARKET"
        )

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Iron Condor placed!")
            print(f"  Underlying LTP: {response.get('underlying_ltp')}")
            print(f"\n  Leg Results:")
            for result in response.get('results', []):
                status = "[OK]" if result.get('status') == 'success' else "[FAIL]"
                print(f"    {status} Leg {result.get('leg')}: {result.get('action')} "
                      f"{result.get('symbol')} - {result.get('orderid')}")
        else:
            print(f"\n[ERROR] Iron Condor failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Place Iron Condor strategy using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Iron Condor Structure:
  BUY  OTM6 CE (far OTM call - protection)
  SELL OTM4 CE (near OTM call - premium)
  SELL OTM4 PE (near OTM put - premium)
  BUY  OTM6 PE (far OTM put - protection)

Best Use Cases:
  - Low volatility expectation
  - Range-bound markets
  - Weekly expiry (faster theta decay)

Risk Profile:
  - Max Profit: Premium received
  - Max Loss: Strike width - Premium
  - Win Rate: Higher (price must move significantly to lose)

Examples:
  # Standard Iron Condor on NIFTY
  python iron_condor.py --underlying NIFTY --expiry 30JAN25 --quantity 75

  # Wider wings for BANKNIFTY
  python iron_condor.py --underlying BANKNIFTY --expiry 30JAN25 --quantity 30 --sell-offset 3 --buy-offset 5

  # Aggressive (closer to ATM)
  python iron_condor.py --underlying NIFTY --expiry 30JAN25 --quantity 75 --sell-offset 2 --buy-offset 4
        """
    )

    parser.add_argument("--underlying", "-u", required=True, help="Underlying symbol")
    parser.add_argument("--expiry", "-e", required=True, help="Expiry date (DDMMMYY)")
    parser.add_argument("--quantity", "-q", type=int, required=True, help="Quantity per leg")
    parser.add_argument("--sell-offset", type=int, default=4, help="OTM offset for sold options (default: 4)")
    parser.add_argument("--buy-offset", type=int, default=6, help="OTM offset for bought options (default: 6)")
    parser.add_argument("--exchange", default="NSE_INDEX", choices=["NSE_INDEX", "BSE_INDEX"], help="Exchange")
    parser.add_argument("--product", "-p", default="NRML", choices=["NRML", "MIS"], help="Product type")
    parser.add_argument("--strategy", default="Iron Condor", help="Strategy name")

    args = parser.parse_args()

    iron_condor(
        underlying=args.underlying,
        expiry_date=args.expiry,
        quantity=args.quantity,
        sell_offset=args.sell_offset,
        buy_offset=args.buy_offset,
        exchange=args.exchange,
        product=args.product,
        strategy=args.strategy
    )


if __name__ == "__main__":
    main()
