#!/usr/bin/env python3
"""
Get market quotes using OpenAlgo API.

Usage:
    python quotes.py --symbol RELIANCE --exchange NSE
    python quotes.py --symbols RELIANCE,TCS,INFY --exchange NSE
    python quotes.py --symbols NIFTY,BANKNIFTY --exchange NSE_INDEX
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


def get_single_quote(symbol, exchange):
    """Get quote for a single symbol."""
    client = get_client()

    response = client.quotes(symbol=symbol, exchange=exchange)

    if response.get('status') == 'success':
        data = response.get('data', {})
        change = data['ltp'] - data['prev_close']
        change_pct = (change / data['prev_close']) * 100

        print(f"\n{symbol} ({exchange})")
        print(f"  LTP: {data['ltp']} ({change:+.2f}, {change_pct:+.2f}%)")
        print(f"  Open: {data['open']} | High: {data['high']} | Low: {data['low']}")
        print(f"  Bid: {data['bid']} | Ask: {data['ask']}")
        print(f"  Volume: {data['volume']:,}")
        print(f"  Prev Close: {data['prev_close']}")
    else:
        print(f"Error: {response}")

    return response


def get_multiple_quotes(symbols, exchange):
    """Get quotes for multiple symbols."""
    client = get_client()

    symbol_list = [{"symbol": s.strip(), "exchange": exchange} for s in symbols.split(",")]

    response = client.multiquotes(symbols=symbol_list)

    if response.get('status') == 'success':
        print(f"\n{'Symbol':<15} {'LTP':>12} {'Change':>12} {'Change%':>10} {'Volume':>15}")
        print("-" * 70)

        for item in response.get('results', []):
            symbol = item['symbol']
            data = item.get('data', {})
            change = data['ltp'] - data['prev_close']
            change_pct = (change / data['prev_close']) * 100 if data['prev_close'] else 0

            print(f"{symbol:<15} {data['ltp']:>12.2f} {change:>+12.2f} {change_pct:>+10.2f}% {data['volume']:>15,}")
    else:
        print(f"Error: {response}")

    return response


def main():
    parser = argparse.ArgumentParser(
        description="Get market quotes using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single symbol
  python quotes.py --symbol RELIANCE --exchange NSE

  # Multiple symbols
  python quotes.py --symbols RELIANCE,TCS,INFY,HDFCBANK --exchange NSE

  # Index quotes
  python quotes.py --symbols NIFTY,BANKNIFTY,FINNIFTY --exchange NSE_INDEX

  # F&O quotes
  python quotes.py --symbol NIFTY30JAN25FUT --exchange NFO
        """
    )

    parser.add_argument("--symbol", "-s", help="Single symbol to quote")
    parser.add_argument("--symbols", help="Comma-separated list of symbols")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")

    args = parser.parse_args()

    if args.symbols:
        get_multiple_quotes(args.symbols, args.exchange)
    elif args.symbol:
        get_single_quote(args.symbol, args.exchange)
    else:
        parser.error("Provide either --symbol or --symbols")


if __name__ == "__main__":
    main()
