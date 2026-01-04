#!/usr/bin/env python3
"""
Stream real-time market data using OpenAlgo WebSocket.

Usage:
    python stream.py --symbols NIFTY,BANKNIFTY --exchange NSE_INDEX --mode ltp
    python stream.py --symbols RELIANCE,TCS,INFY --exchange NSE --mode quote
    python stream.py --symbols SBIN --exchange NSE --mode depth
"""

import os
import sys
import argparse
import time
from datetime import datetime
from openalgo import api


def get_client(verbose=True):
    """Initialize OpenAlgo client with WebSocket."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")
    ws_url = os.environ.get("OPENALGO_WS_URL", "ws://127.0.0.1:8765")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host, ws_url=ws_url, verbose=verbose)


def on_ltp(data):
    """Callback for LTP updates."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {data['exchange']}:{data['symbol']} = {data['data'].get('ltp', 'N/A')}")


def on_quote(data):
    """Callback for Quote updates."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    d = data['data']
    print(f"[{timestamp}] {data['symbol']}: O={d.get('open')} H={d.get('high')} "
          f"L={d.get('low')} LTP={d.get('ltp')} Vol={d.get('volume', 0):,}")


def on_depth(data):
    """Callback for Depth updates."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    d = data['data']

    bids = d.get('bids', [])
    asks = d.get('asks', [])

    best_bid = bids[0] if bids else {'price': 'N/A', 'quantity': 0}
    best_ask = asks[0] if asks else {'price': 'N/A', 'quantity': 0}

    print(f"[{timestamp}] {data['symbol']}: "
          f"Bid={best_bid['price']} ({best_bid['quantity']}) | "
          f"Ask={best_ask['price']} ({best_ask['quantity']}) | "
          f"LTP={d.get('ltp')}")


def stream_data(symbols, exchange, mode="ltp", duration=60, verbose=1):
    """
    Stream real-time market data.

    Args:
        symbols: Comma-separated list of symbols
        exchange: Exchange code
        mode: Stream mode (ltp, quote, depth)
        duration: How long to stream in seconds (0 = infinite)
        verbose: Verbosity level (0=silent, 1=basic, 2=debug)

    Modes:
        ltp: Last Traded Price only (fastest)
        quote: OHLC + Bid/Ask
        depth: Full order book (5 levels)
    """
    client = get_client(verbose=verbose)

    instruments = [{"exchange": exchange, "symbol": s.strip()} for s in symbols.split(",")]

    print(f"\nStarting {mode.upper()} stream:")
    print(f"  Symbols: {symbols}")
    print(f"  Exchange: {exchange}")
    print(f"  Duration: {'Infinite' if duration == 0 else f'{duration}s'}")
    print(f"  Press Ctrl+C to stop\n")

    try:
        # Connect to WebSocket
        client.connect()

        # Subscribe based on mode
        if mode == "ltp":
            client.subscribe_ltp(instruments, on_data_received=on_ltp)
        elif mode == "quote":
            client.subscribe_quote(instruments, on_data_received=on_quote)
        elif mode == "depth":
            client.subscribe_depth(instruments, on_data_received=on_depth)

        # Run for specified duration
        if duration > 0:
            time.sleep(duration)
        else:
            # Infinite loop until Ctrl+C
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStream stopped by user")

    finally:
        # Unsubscribe and disconnect
        print("Cleaning up...")
        if mode == "ltp":
            client.unsubscribe_ltp(instruments)
        elif mode == "quote":
            client.unsubscribe_quote(instruments)
        elif mode == "depth":
            client.unsubscribe_depth(instruments)

        client.disconnect()
        print("Disconnected")


def main():
    parser = argparse.ArgumentParser(
        description="Stream real-time market data using OpenAlgo WebSocket",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Stream Modes:
  ltp   - Last Traded Price only (fastest, lowest bandwidth)
  quote - OHLC + Bid/Ask (moderate bandwidth)
  depth - Full order book with 5 levels (highest bandwidth)

Verbose Levels:
  0 - Silent (errors only)
  1 - Basic (connection, subscription logs)
  2 - Debug (all data updates from SDK)

Examples:
  # Stream NIFTY and BANKNIFTY LTP
  python stream.py --symbols NIFTY,BANKNIFTY --exchange NSE_INDEX --mode ltp

  # Stream stock quotes for 5 minutes
  python stream.py --symbols RELIANCE,TCS,INFY --exchange NSE --mode quote --duration 300

  # Stream market depth (order book)
  python stream.py --symbols SBIN --exchange NSE --mode depth

  # Silent mode (only show data callbacks)
  python stream.py --symbols NIFTY --exchange NSE_INDEX --mode ltp --verbose 0

  # Debug mode (show all SDK output)
  python stream.py --symbols NIFTY --exchange NSE_INDEX --mode ltp --verbose 2

  # Infinite stream (until Ctrl+C)
  python stream.py --symbols NIFTY --exchange NSE_INDEX --mode quote --duration 0
        """
    )

    parser.add_argument("--symbols", "-s", required=True, help="Comma-separated list of symbols")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "BFO", "CDS", "BCD", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")
    parser.add_argument("--mode", "-m", default="ltp", choices=["ltp", "quote", "depth"],
                        help="Stream mode (default: ltp)")
    parser.add_argument("--duration", "-d", type=int, default=60,
                        help="Stream duration in seconds (0 for infinite, default: 60)")
    parser.add_argument("--verbose", "-v", type=int, default=1, choices=[0, 1, 2],
                        help="Verbosity level (default: 1)")

    args = parser.parse_args()

    stream_data(
        symbols=args.symbols,
        exchange=args.exchange,
        mode=args.mode,
        duration=args.duration,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
