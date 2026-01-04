#!/usr/bin/env python3
"""
Calculate margin requirements using OpenAlgo API.

Usage:
    python margin.py --symbol NIFTY30JAN2526000CE --exchange NFO --action SELL --quantity 75
    python margin.py --spread --buy NIFTY30JAN2526000CE --sell NIFTY30JAN2526500CE --quantity 75
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


def calculate_margin(positions):
    """
    Calculate margin for given positions.

    Args:
        positions: List of position dictionaries

    Returns:
        dict: Margin calculation response
    """
    client = get_client()

    print("\nCalculating margin for:")
    for i, pos in enumerate(positions, 1):
        print(f"  {i}. {pos['action']} {pos['quantity']} {pos['symbol']} ({pos['exchange']})")

    response = client.margin(positions=positions)

    if response.get('status') == 'success':
        data = response.get('data', {})
        print("\n=== MARGIN REQUIREMENT ===")
        print(f"  Total Margin:     ₹{data.get('total_margin_required', 0):>12,.2f}")
        print(f"  SPAN Margin:      ₹{data.get('span_margin', 0):>12,.2f}")
        print(f"  Exposure Margin:  ₹{data.get('exposure_margin', 0):>12,.2f}")

        # Check available funds
        funds = client.funds()
        if funds.get('status') == 'success':
            available = float(funds['data'].get('availablecash', 0))
            required = data.get('total_margin_required', 0)

            print(f"\n  Available Cash:   ₹{available:>12,.2f}")

            if available >= required:
                print(f"  \033[92mSufficient margin available\033[0m")
            else:
                shortfall = required - available
                print(f"  \033[91mMargin shortfall: ₹{shortfall:,.2f}\033[0m")
    else:
        print(f"\nError: {response}")

    return response


def single_position_margin(symbol, exchange, action, quantity, product="NRML", pricetype="MARKET"):
    """Calculate margin for a single position."""
    positions = [{
        "symbol": symbol,
        "exchange": exchange,
        "action": action,
        "product": product,
        "pricetype": pricetype,
        "quantity": str(quantity)
    }]

    return calculate_margin(positions)


def spread_margin(buy_symbol, sell_symbol, exchange, quantity, product="NRML"):
    """Calculate margin for a spread (hedge benefit)."""
    positions = [
        {
            "symbol": buy_symbol,
            "exchange": exchange,
            "action": "BUY",
            "product": product,
            "pricetype": "MARKET",
            "quantity": str(quantity)
        },
        {
            "symbol": sell_symbol,
            "exchange": exchange,
            "action": "SELL",
            "product": product,
            "pricetype": "MARKET",
            "quantity": str(quantity)
        }
    ]

    print("\n=== SPREAD MARGIN (with hedge benefit) ===")
    spread_result = calculate_margin(positions)

    # Also show individual margins for comparison
    print("\n--- Individual Margins (for comparison) ---")

    print(f"\nBuy leg alone ({buy_symbol}):")
    buy_result = calculate_margin([positions[0]])

    print(f"\nSell leg alone ({sell_symbol}):")
    sell_result = calculate_margin([positions[1]])

    # Calculate hedge benefit
    if all(r.get('status') == 'success' for r in [spread_result, buy_result, sell_result]):
        spread_margin = spread_result['data'].get('total_margin_required', 0)
        buy_margin = buy_result['data'].get('total_margin_required', 0)
        sell_margin = sell_result['data'].get('total_margin_required', 0)
        individual_total = buy_margin + sell_margin

        if individual_total > 0:
            benefit = individual_total - spread_margin
            benefit_pct = (benefit / individual_total) * 100

            print(f"\n=== HEDGE BENEFIT ===")
            print(f"  Individual Total: ₹{individual_total:>12,.2f}")
            print(f"  Spread Margin:    ₹{spread_margin:>12,.2f}")
            print(f"  Benefit:          ₹{benefit:>12,.2f} ({benefit_pct:.1f}%)")

    return spread_result


def main():
    parser = argparse.ArgumentParser(
        description="Calculate margin requirements using OpenAlgo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single position margin
  python margin.py --symbol NIFTY30JAN2526000CE --exchange NFO --action SELL --quantity 75

  # Spread margin (hedge benefit)
  python margin.py --spread --buy NIFTY30JAN2526000CE --sell NIFTY30JAN2526500CE --quantity 75

  # Future margin
  python margin.py --symbol NIFTY30JAN25FUT --exchange NFO --action BUY --quantity 75

  # Stock delivery (no margin)
  python margin.py --symbol RELIANCE --exchange NSE --action BUY --quantity 10 --product CNC
        """
    )

    parser.add_argument("--symbol", "-s", help="Trading symbol")
    parser.add_argument("--exchange", "-e", default="NFO",
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX"],
                        help="Exchange code")
    parser.add_argument("--action", "-a", choices=["BUY", "SELL"], help="Order action")
    parser.add_argument("--quantity", "-q", type=int, help="Order quantity")
    parser.add_argument("--product", "-p", default="NRML", choices=["CNC", "NRML", "MIS"],
                        help="Product type")

    parser.add_argument("--spread", action="store_true", help="Calculate spread margin")
    parser.add_argument("--buy", help="Buy leg symbol (for spread)")
    parser.add_argument("--sell", help="Sell leg symbol (for spread)")

    args = parser.parse_args()

    if args.spread:
        if not all([args.buy, args.sell, args.quantity]):
            parser.error("--spread requires --buy, --sell, and --quantity")

        spread_margin(
            buy_symbol=args.buy,
            sell_symbol=args.sell,
            exchange=args.exchange,
            quantity=args.quantity,
            product=args.product
        )
    else:
        if not all([args.symbol, args.action, args.quantity]):
            parser.error("Required: --symbol, --action, --quantity")

        single_position_margin(
            symbol=args.symbol,
            exchange=args.exchange,
            action=args.action,
            quantity=args.quantity,
            product=args.product
        )


if __name__ == "__main__":
    main()
