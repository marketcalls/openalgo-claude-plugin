#!/usr/bin/env python3
"""
Get historical OHLCV data using OpenAlgo API.

Usage:
    python history.py --symbol SBIN --exchange NSE --interval 5m --start 2025-01-01 --end 2025-01-15
    python history.py --symbol NIFTY --exchange NSE_INDEX --interval D --start 2024-01-01 --end 2024-12-31
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from openalgo import api


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host)


def get_history(symbol, exchange, interval, start_date, end_date, output=None):
    """
    Get historical OHLCV data.

    Args:
        symbol: Trading symbol
        exchange: Exchange code
        interval: Candle interval (1m, 3m, 5m, 10m, 15m, 30m, 1h, D)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        output: Output file path (optional)

    Returns:
        Pandas DataFrame with OHLCV data
    """
    client = get_client()

    print(f"\nFetching historical data:")
    print(f"  Symbol: {symbol}")
    print(f"  Exchange: {exchange}")
    print(f"  Interval: {interval}")
    print(f"  Period: {start_date} to {end_date}")

    try:
        df = client.history(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )

        if df is not None and len(df) > 0:
            print(f"\n[SUCCESS] Retrieved {len(df)} candles")

            # Summary statistics
            print(f"\n  Summary:")
            print(f"    High: {df['high'].max():.2f}")
            print(f"    Low: {df['low'].min():.2f}")
            print(f"    Avg Volume: {df['volume'].mean():,.0f}")
            print(f"    Total Volume: {df['volume'].sum():,}")

            # Show first and last few rows
            print(f"\n  First 5 candles:")
            print(df.head().to_string())

            print(f"\n  Last 5 candles:")
            print(df.tail().to_string())

            # Save to file if requested
            if output:
                if output.endswith('.csv'):
                    df.to_csv(output)
                elif output.endswith('.json'):
                    df.to_json(output, orient='records', date_format='iso')
                else:
                    df.to_csv(output + '.csv')
                print(f"\n  Saved to: {output}")

            return df
        else:
            print("\n[WARNING] No data returned")
            return None

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return None


def get_available_intervals():
    """Get available intervals from the API."""
    client = get_client()

    response = client.intervals()

    if response.get('status') == 'success':
        data = response.get('data', {})
        print("\nAvailable Intervals:")
        for category, intervals in data.items():
            if intervals:
                print(f"  {category}: {', '.join(intervals)}")
    else:
        print(f"Error: {response}")


def main():
    parser = argparse.ArgumentParser(
        description="Get historical OHLCV data using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Intervals:
  Minutes: 1m, 3m, 5m, 10m, 15m, 30m
  Hours: 1h
  Days: D

Examples:
  # 5-minute candles
  python history.py --symbol SBIN --exchange NSE --interval 5m --start 2025-01-01 --end 2025-01-15

  # Daily candles for a year
  python history.py --symbol NIFTY --exchange NSE_INDEX --interval D --start 2024-01-01 --end 2024-12-31

  # Save to CSV
  python history.py --symbol RELIANCE --exchange NSE --interval 15m --start 2025-01-01 --end 2025-01-10 --output reliance_data.csv

  # Today's 1-minute data
  python history.py --symbol BANKNIFTY --exchange NSE_INDEX --interval 1m --today

  # List available intervals
  python history.py --list-intervals
        """
    )

    parser.add_argument("--symbol", "-s", help="Trading symbol")
    parser.add_argument("--exchange", "-e",
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")
    parser.add_argument("--interval", "-i", default="5m",
                        choices=["1m", "3m", "5m", "10m", "15m", "30m", "1h", "D"],
                        help="Candle interval (default: 5m)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--today", action="store_true", help="Get today's data")
    parser.add_argument("--output", "-o", help="Output file path (.csv or .json)")
    parser.add_argument("--list-intervals", action="store_true", help="List available intervals")

    args = parser.parse_args()

    if args.list_intervals:
        get_available_intervals()
        return

    if not args.symbol or not args.exchange:
        parser.error("--symbol and --exchange are required")

    if args.today:
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = today
        end_date = today
    elif args.start and args.end:
        start_date = args.start
        end_date = args.end
    else:
        # Default to last 7 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    get_history(
        symbol=args.symbol,
        exchange=args.exchange,
        interval=args.interval,
        start_date=start_date,
        end_date=end_date,
        output=args.output
    )


if __name__ == "__main__":
    main()
