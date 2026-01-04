#!/usr/bin/env python3
"""
Portfolio management script using OpenAlgo API.

Usage:
    python portfolio.py --summary
    python portfolio.py --positions
    python portfolio.py --holdings
    python portfolio.py --orders
    python portfolio.py --trades
    python portfolio.py --funds
"""

import os
import sys
import argparse
from datetime import datetime
from openalgo import api

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host)


def show_funds():
    """Display account funds information."""
    client = get_client()
    response = client.funds()

    if response.get('status') == 'success':
        data = response.get('data', {})
        print("\n=== FUNDS ===")
        print(f"  Available Cash:    ₹{float(data.get('availablecash', 0)):>12,.2f}")
        print(f"  Collateral:        ₹{float(data.get('collateral', 0)):>12,.2f}")
        print(f"  M2M Realized:      ₹{float(data.get('m2mrealized', 0)):>12,.2f}")
        print(f"  M2M Unrealized:    ₹{float(data.get('m2munrealized', 0)):>12,.2f}")
        print(f"  Utilized Margin:   ₹{float(data.get('utiliseddebits', 0)):>12,.2f}")
    else:
        print(f"Error: {response}")


def show_positions():
    """Display open positions."""
    client = get_client()
    response = client.positionbook()

    if response.get('status') == 'success':
        data = response.get('data', [])
        print("\n=== POSITIONS ===")

        if not data:
            print("  No open positions")
            return

        total_pnl = 0
        print(f"\n{'Symbol':<20} {'Exch':<6} {'Prod':<5} {'Qty':>8} {'Avg Price':>12} {'LTP':>12} {'P&L':>12}")
        print("-" * 85)

        for pos in data:
            qty = int(pos.get('quantity', 0))
            pnl = float(pos.get('pnl', 0))
            total_pnl += pnl

            pnl_str = f"₹{pnl:>10,.2f}"
            if pnl > 0:
                pnl_str = f"\033[92m{pnl_str}\033[0m"  # Green
            elif pnl < 0:
                pnl_str = f"\033[91m{pnl_str}\033[0m"  # Red

            print(f"{pos.get('symbol', ''):<20} "
                  f"{pos.get('exchange', ''):<6} "
                  f"{pos.get('product', ''):<5} "
                  f"{qty:>8} "
                  f"₹{float(pos.get('average_price', 0)):>10,.2f} "
                  f"₹{float(pos.get('ltp', 0)):>10,.2f} "
                  f"{pnl_str}")

        print("-" * 85)
        print(f"{'Total P&L:':<65} ₹{total_pnl:>12,.2f}")
    else:
        print(f"Error: {response}")


def show_holdings():
    """Display delivery holdings."""
    client = get_client()
    response = client.holdings()

    if response.get('status') == 'success':
        data = response.get('data', {})
        holdings = data.get('holdings', [])
        stats = data.get('statistics', {})

        print("\n=== HOLDINGS ===")

        if not holdings:
            print("  No holdings")
            return

        print(f"\n{'Symbol':<20} {'Exch':<6} {'Qty':>8} {'P&L':>12} {'P&L %':>10}")
        print("-" * 65)

        for hold in holdings:
            pnl = float(hold.get('pnl', 0))
            pnl_pct = float(hold.get('pnlpercent', 0))

            print(f"{hold.get('symbol', ''):<20} "
                  f"{hold.get('exchange', ''):<6} "
                  f"{hold.get('quantity', 0):>8} "
                  f"₹{pnl:>10,.2f} "
                  f"{pnl_pct:>9.2f}%")

        print("-" * 65)
        print(f"\nStatistics:")
        print(f"  Total Holding Value:  ₹{float(stats.get('totalholdingvalue', 0)):>12,.2f}")
        print(f"  Total Investment:     ₹{float(stats.get('totalinvvalue', 0)):>12,.2f}")
        print(f"  Total P&L:            ₹{float(stats.get('totalprofitandloss', 0)):>12,.2f}")
        print(f"  Total P&L %:          {float(stats.get('totalpnlpercentage', 0)):>12.2f}%")
    else:
        print(f"Error: {response}")


def show_orders():
    """Display order book."""
    client = get_client()
    response = client.orderbook()

    if response.get('status') == 'success':
        data = response.get('data', {})
        orders = data.get('orders', [])
        stats = data.get('statistics', {})

        print("\n=== ORDER BOOK ===")

        if not orders:
            print("  No orders today")
            return

        print(f"\n{'Time':<12} {'Symbol':<20} {'Action':<6} {'Qty':>6} {'Price':>10} {'Type':<8} {'Status':<12}")
        print("-" * 85)

        for order in orders:
            timestamp = order.get('timestamp', '')
            if timestamp:
                # Extract time part
                time_part = timestamp.split(' ')[-1] if ' ' in timestamp else timestamp

            status = order.get('order_status', '')
            status_colored = status
            if status == 'complete':
                status_colored = f"\033[92m{status}\033[0m"
            elif status in ['rejected', 'cancelled']:
                status_colored = f"\033[91m{status}\033[0m"
            elif status == 'open':
                status_colored = f"\033[93m{status}\033[0m"

            print(f"{time_part:<12} "
                  f"{order.get('symbol', ''):<20} "
                  f"{order.get('action', ''):<6} "
                  f"{order.get('quantity', ''):>6} "
                  f"₹{float(order.get('price', 0)):>8,.2f} "
                  f"{order.get('pricetype', ''):<8} "
                  f"{status_colored:<12}")

        print("-" * 85)
        print(f"\nSummary: {int(stats.get('total_completed_orders', 0))} completed, "
              f"{int(stats.get('total_open_orders', 0))} open, "
              f"{int(stats.get('total_rejected_orders', 0))} rejected")
    else:
        print(f"Error: {response}")


def show_trades():
    """Display trade book."""
    client = get_client()
    response = client.tradebook()

    if response.get('status') == 'success':
        data = response.get('data', [])

        print("\n=== TRADE BOOK ===")

        if not data:
            print("  No trades today")
            return

        total_value = 0
        print(f"\n{'Time':<12} {'Symbol':<20} {'Action':<6} {'Qty':>6} {'Avg Price':>12} {'Value':>14}")
        print("-" * 80)

        for trade in data:
            value = float(trade.get('trade_value', 0))
            total_value += value

            print(f"{trade.get('timestamp', ''):<12} "
                  f"{trade.get('symbol', ''):<20} "
                  f"{trade.get('action', ''):<6} "
                  f"{trade.get('quantity', 0):>6} "
                  f"₹{float(trade.get('average_price', 0)):>10,.2f} "
                  f"₹{value:>12,.2f}")

        print("-" * 80)
        print(f"{'Total Traded Value:':<55} ₹{total_value:>14,.2f}")
    else:
        print(f"Error: {response}")


def show_summary():
    """Display complete portfolio summary."""
    print(f"\n{'='*60}")
    print(f"  PORTFOLIO SUMMARY - {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}")
    print(f"{'='*60}")

    show_funds()
    show_positions()
    show_holdings()


def main():
    parser = argparse.ArgumentParser(
        description="Portfolio management with OpenAlgo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full portfolio summary
  python portfolio.py --summary

  # Just positions
  python portfolio.py --positions

  # Just holdings
  python portfolio.py --holdings

  # Just orders
  python portfolio.py --orders

  # Just trades
  python portfolio.py --trades

  # Just funds
  python portfolio.py --funds

  # Multiple views
  python portfolio.py --positions --orders
        """
    )

    parser.add_argument("--summary", "-s", action="store_true", help="Show complete portfolio summary")
    parser.add_argument("--funds", "-f", action="store_true", help="Show funds/margin info")
    parser.add_argument("--positions", "-p", action="store_true", help="Show open positions")
    parser.add_argument("--holdings", "-h", action="store_true", help="Show delivery holdings")
    parser.add_argument("--orders", "-o", action="store_true", help="Show order book")
    parser.add_argument("--trades", "-t", action="store_true", help="Show trade book")

    args = parser.parse_args()

    # If no specific option, show summary
    if not any([args.summary, args.funds, args.positions, args.holdings, args.orders, args.trades]):
        args.summary = True

    if args.summary:
        show_summary()
    else:
        if args.funds:
            show_funds()
        if args.positions:
            show_positions()
        if args.holdings:
            show_holdings()
        if args.orders:
            show_orders()
        if args.trades:
            show_trades()


if __name__ == "__main__":
    main()
