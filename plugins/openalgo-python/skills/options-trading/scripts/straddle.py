#!/usr/bin/env python3
"""
Place Straddle/Strangle strategies using OpenAlgo API.

Straddle: Buy/Sell ATM Call + ATM Put
Strangle: Buy/Sell OTM Call + OTM Put

Usage:
    python straddle.py --underlying NIFTY --expiry 30JAN25 --action BUY --quantity 75
    python straddle.py --underlying NIFTY --expiry 30JAN25 --action SELL --quantity 75 --strangle --offset 3
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


def straddle_strangle(underlying, expiry_date, action, quantity, strangle=False,
                      offset=3, exchange="NSE_INDEX", product="NRML", strategy=None):
    """
    Place a Straddle or Strangle strategy.

    Straddle (ATM):
    - Long Straddle: BUY ATM CE + BUY ATM PE (profit from big moves)
    - Short Straddle: SELL ATM CE + SELL ATM PE (profit from no movement)

    Strangle (OTM):
    - Long Strangle: BUY OTM CE + BUY OTM PE (cheaper than straddle)
    - Short Strangle: SELL OTM CE + SELL OTM PE (wider profit zone)

    Args:
        underlying: Underlying symbol
        expiry_date: Expiry date in DDMMMYY format
        action: BUY (long) or SELL (short)
        quantity: Quantity per leg
        strangle: True for strangle, False for straddle
        offset: OTM offset for strangle (default: 3)
        exchange: Exchange code
        product: NRML or MIS
        strategy: Strategy name

    Returns:
        dict: API response with execution details
    """
    client = get_client()

    strategy_type = "Strangle" if strangle else "Straddle"
    direction = "Long" if action == "BUY" else "Short"

    if strategy is None:
        strategy = f"{direction} {strategy_type}"

    strike_offset = f"OTM{offset}" if strangle else "ATM"

    print(f"\nPlacing {direction} {strategy_type}:")
    print(f"  Underlying: {underlying}")
    print(f"  Expiry: {expiry_date}")
    print(f"  Action: {action}")
    print(f"  Strike: {strike_offset}")
    print(f"  Quantity: {quantity}")

    legs = [
        {"offset": strike_offset, "option_type": "CE", "action": action, "quantity": quantity},
        {"offset": strike_offset, "option_type": "PE", "action": action, "quantity": quantity}
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
            print(f"\n[SUCCESS] {strategy_type} placed!")
            print(f"  Underlying LTP: {response.get('underlying_ltp')}")
            print(f"\n  Leg Results:")
            for result in response.get('results', []):
                status = "[OK]" if result.get('status') == 'success' else "[FAIL]"
                print(f"    {status} {result.get('action')} {result.get('symbol')} - {result.get('orderid')}")
        else:
            print(f"\n[ERROR] {strategy_type} failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Place Straddle/Strangle strategies using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Strategy Comparison:
  STRADDLE (ATM)             STRANGLE (OTM)
  ├─ Higher premium          ├─ Lower premium
  ├─ Lower breakeven         ├─ Higher breakeven
  └─ Higher delta            └─ Lower delta

Long Straddle/Strangle:
  - Use before events (earnings, budget, RBI policy)
  - Profit from big moves in either direction
  - Risk: Premium paid (limited loss)

Short Straddle/Strangle:
  - Use when expecting low volatility
  - Profit from theta decay
  - Risk: Unlimited if market moves big

Examples:
  # Long Straddle (before event)
  python straddle.py --underlying NIFTY --expiry 30JAN25 --action BUY --quantity 75

  # Short Straddle (low vol expectation)
  python straddle.py --underlying NIFTY --expiry 30JAN25 --action SELL --quantity 75

  # Long Strangle (cheaper than straddle)
  python straddle.py --underlying BANKNIFTY --expiry 30JAN25 --action BUY --quantity 30 --strangle --offset 4

  # Short Strangle (wider profit zone)
  python straddle.py --underlying NIFTY --expiry 30JAN25 --action SELL --quantity 75 --strangle --offset 5
        """
    )

    parser.add_argument("--underlying", "-u", required=True, help="Underlying symbol")
    parser.add_argument("--expiry", "-e", required=True, help="Expiry date (DDMMMYY)")
    parser.add_argument("--action", "-a", required=True, choices=["BUY", "SELL"], help="BUY (long) or SELL (short)")
    parser.add_argument("--quantity", "-q", type=int, required=True, help="Quantity per leg")
    parser.add_argument("--strangle", action="store_true", help="Use OTM strikes (strangle) instead of ATM (straddle)")
    parser.add_argument("--offset", type=int, default=3, help="OTM offset for strangle (default: 3)")
    parser.add_argument("--exchange", default="NSE_INDEX", choices=["NSE_INDEX", "BSE_INDEX"], help="Exchange")
    parser.add_argument("--product", "-p", default="NRML", choices=["NRML", "MIS"], help="Product type")
    parser.add_argument("--strategy", help="Custom strategy name")

    args = parser.parse_args()

    straddle_strangle(
        underlying=args.underlying,
        expiry_date=args.expiry,
        action=args.action,
        quantity=args.quantity,
        strangle=args.strangle,
        offset=args.offset,
        exchange=args.exchange,
        product=args.product,
        strategy=args.strategy
    )


if __name__ == "__main__":
    main()
