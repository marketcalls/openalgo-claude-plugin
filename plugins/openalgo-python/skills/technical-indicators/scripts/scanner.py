#!/usr/bin/env python3
"""
Scan multiple symbols for candlestick patterns and indicator signals.

Usage:
    python scanner.py --symbols RELIANCE,TCS,INFY,SBIN --exchange NSE --pattern bullish
    python scanner.py --symbols NIFTY,BANKNIFTY --exchange NSE_INDEX --pattern all
    python scanner.py --watchlist nifty50 --pattern bearish
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from openalgo import api

try:
    import talib
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    sys.exit(1)


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host)


# Predefined watchlists
WATCHLISTS = {
    'nifty50': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'ITC', 'SBIN',
                'BHARTIARTL', 'KOTAKBANK', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN',
                'SUNPHARMA', 'BAJFINANCE', 'WIPRO', 'HCLTECH', 'ULTRACEMCO'],
    'banknifty': ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'SBIN', 'INDUSINDBK',
                  'BANKBARODA', 'FEDERALBNK', 'IDFCFIRSTB', 'PNB', 'AUBANK', 'BANDHANBNK'],
    'it': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM', 'LTIM', 'PERSISTENT', 'COFORGE', 'MPHASIS'],
    'pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'APOLLOHOSP', 'BIOCON', 'LUPIN'],
    'auto': ['TATAMOTORS', 'MARUTI', 'M&M', 'BAJAJ-AUTO', 'HEROMOTOCO', 'EICHERMOT', 'ASHOKLEY'],
    'indices': ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY'],
}

# Candlestick pattern functions
BULLISH_PATTERNS = {
    'HAMMER': talib.CDLHAMMER,
    'INVERTED_HAMMER': talib.CDLINVERTEDHAMMER,
    'BULLISH_ENGULFING': lambda o, h, l, c: np.where(talib.CDLENGULFING(o, h, l, c) > 0,
                                                      talib.CDLENGULFING(o, h, l, c), 0),
    'MORNING_STAR': talib.CDLMORNINGSTAR,
    'THREE_WHITE_SOLDIERS': talib.CDL3WHITESOLDIERS,
    'PIERCING': talib.CDLPIERCING,
    'BULLISH_HARAMI': lambda o, h, l, c: np.where(talib.CDLHARAMI(o, h, l, c) > 0,
                                                   talib.CDLHARAMI(o, h, l, c), 0),
    'DRAGONFLY_DOJI': talib.CDLDRAGONFLYDOJI,
}

BEARISH_PATTERNS = {
    'SHOOTING_STAR': talib.CDLSHOOTINGSTAR,
    'HANGING_MAN': talib.CDLHANGINGMAN,
    'BEARISH_ENGULFING': lambda o, h, l, c: np.where(talib.CDLENGULFING(o, h, l, c) < 0,
                                                      abs(talib.CDLENGULFING(o, h, l, c)), 0),
    'EVENING_STAR': talib.CDLEVENINGSTAR,
    'THREE_BLACK_CROWS': talib.CDL3BLACKCROWS,
    'DARK_CLOUD': talib.CDLDARKCLOUDCOVER,
    'BEARISH_HARAMI': lambda o, h, l, c: np.where(talib.CDLHARAMI(o, h, l, c) < 0,
                                                   abs(talib.CDLHARAMI(o, h, l, c)), 0),
    'GRAVESTONE_DOJI': talib.CDLGRAVESTONEDOJI,
}

NEUTRAL_PATTERNS = {
    'DOJI': talib.CDLDOJI,
    'SPINNING_TOP': talib.CDLSPINNINGTOP,
    'HIGH_WAVE': talib.CDLHIGHWAVE,
}


def scan_patterns(df, pattern_type='all'):
    """
    Scan for candlestick patterns.

    Args:
        df: DataFrame with OHLCV data
        pattern_type: 'bullish', 'bearish', 'neutral', or 'all'

    Returns:
        List of detected patterns
    """
    o = df['open'].values
    h = df['high'].values
    l = df['low'].values
    c = df['close'].values

    patterns_to_scan = {}

    if pattern_type in ['bullish', 'all']:
        patterns_to_scan.update(BULLISH_PATTERNS)
    if pattern_type in ['bearish', 'all']:
        patterns_to_scan.update(BEARISH_PATTERNS)
    if pattern_type in ['neutral', 'all']:
        patterns_to_scan.update(NEUTRAL_PATTERNS)

    detected = []
    for name, func in patterns_to_scan.items():
        try:
            result = func(o, h, l, c)
            if result[-1] != 0:
                pattern_type_str = 'BULLISH' if name in BULLISH_PATTERNS else \
                                   'BEARISH' if name in BEARISH_PATTERNS else 'NEUTRAL'
                detected.append({
                    'pattern': name.replace('_', ' ').title(),
                    'type': pattern_type_str,
                    'strength': abs(result[-1])
                })
        except Exception:
            pass

    return detected


def scan_indicator_signals(df):
    """Scan for indicator-based signals."""
    signals = []

    close = df['close'].values
    high = df['high'].values
    low = df['low'].values

    # RSI
    rsi = talib.RSI(close, timeperiod=14)
    if rsi[-1] < 30:
        signals.append({'indicator': 'RSI', 'signal': 'OVERSOLD', 'value': f"{rsi[-1]:.1f}"})
    elif rsi[-1] > 70:
        signals.append({'indicator': 'RSI', 'signal': 'OVERBOUGHT', 'value': f"{rsi[-1]:.1f}"})

    # MACD Cross
    macd, signal, _ = talib.MACD(close)
    if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
        signals.append({'indicator': 'MACD', 'signal': 'BULLISH CROSS', 'value': ''})
    elif macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
        signals.append({'indicator': 'MACD', 'signal': 'BEARISH CROSS', 'value': ''})

    # BB Touch
    upper, middle, lower = talib.BBANDS(close, timeperiod=20)
    if close[-1] < lower[-1]:
        signals.append({'indicator': 'BB', 'signal': 'BELOW LOWER', 'value': ''})
    elif close[-1] > upper[-1]:
        signals.append({'indicator': 'BB', 'signal': 'ABOVE UPPER', 'value': ''})

    # Volume Spike
    if len(df) > 20:
        avg_vol = df['volume'].rolling(20).mean().iloc[-1]
        if df['volume'].iloc[-1] > avg_vol * 2:
            signals.append({'indicator': 'VOLUME', 'signal': 'SPIKE', 'value': f"{df['volume'].iloc[-1]/avg_vol:.1f}x"})

    return signals


def scan_symbol(client, symbol, exchange, interval, days, pattern_type):
    """Scan a single symbol for patterns and signals."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        df = client.history(
            symbol=symbol,
            exchange=exchange,
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )

        if df is None or len(df) < 20:
            return None

        patterns = scan_patterns(df, pattern_type)
        signals = scan_indicator_signals(df)

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        change_pct = ((latest['close'] / prev['close']) - 1) * 100

        return {
            'symbol': symbol,
            'price': latest['close'],
            'change': change_pct,
            'patterns': patterns,
            'signals': signals
        }

    except Exception as e:
        print(f"  Error scanning {symbol}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Scan symbols for candlestick patterns and signals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Watchlists:
  nifty50   - Top 20 Nifty 50 stocks
  banknifty - Bank Nifty constituents
  it        - IT sector stocks
  pharma    - Pharma sector stocks
  auto      - Auto sector stocks
  indices   - Major indices

Pattern Types:
  bullish - Hammer, Morning Star, Engulfing, etc.
  bearish - Shooting Star, Evening Star, Dark Cloud, etc.
  neutral - Doji, Spinning Top, High Wave
  all     - All patterns

Examples:
  # Scan specific symbols
  python scanner.py --symbols RELIANCE,TCS,INFY --exchange NSE --pattern bullish

  # Scan watchlist
  python scanner.py --watchlist nifty50 --pattern all

  # Scan indices
  python scanner.py --watchlist indices --exchange NSE_INDEX --pattern bullish

  # Daily timeframe
  python scanner.py --symbols SBIN,HDFCBANK --exchange NSE --interval D --pattern bearish
        """
    )

    parser.add_argument("--symbols", "-s", help="Comma-separated list of symbols")
    parser.add_argument("--watchlist", "-w", choices=list(WATCHLISTS.keys()), help="Predefined watchlist")
    parser.add_argument("--exchange", "-e", default="NSE",
                        choices=["NSE", "BSE", "NFO", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")
    parser.add_argument("--interval", "-i", default="D",
                        choices=["5m", "15m", "30m", "1h", "D"],
                        help="Candle interval")
    parser.add_argument("--pattern", "-p", default="all",
                        choices=["bullish", "bearish", "neutral", "all"],
                        help="Pattern type to scan")
    parser.add_argument("--days", "-d", type=int, default=30, help="Days of data")

    args = parser.parse_args()

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",")]
    elif args.watchlist:
        symbols = WATCHLISTS[args.watchlist]
        if args.watchlist == 'indices':
            args.exchange = 'NSE_INDEX'
    else:
        parser.error("Provide either --symbols or --watchlist")

    client = get_client()

    print(f"\n{'='*70}")
    print(f"  PATTERN SCANNER")
    print(f"  Symbols: {len(symbols)} | Exchange: {args.exchange} | Interval: {args.interval}")
    print(f"  Pattern Type: {args.pattern.upper()}")
    print(f"{'='*70}")

    results = []
    print(f"\nScanning {len(symbols)} symbols...")

    for i, symbol in enumerate(symbols, 1):
        sys.stdout.write(f"\r  [{i}/{len(symbols)}] Scanning {symbol}...          ")
        sys.stdout.flush()

        result = scan_symbol(client, symbol, args.exchange, args.interval, args.days, args.pattern)
        if result and (result['patterns'] or result['signals']):
            results.append(result)

    print(f"\r  Scan complete. Found signals in {len(results)} symbols.          ")

    if not results:
        print("\n  No patterns or signals detected.")
        return

    # Display results
    print(f"\n{'='*70}")
    print(f"  RESULTS")
    print(f"{'='*70}")

    for result in results:
        symbol = result['symbol']
        price = result['price']
        change = result['change']

        change_str = f"{change:+.2f}%"
        if change > 0:
            change_str = f"\033[92m{change_str}\033[0m"
        elif change < 0:
            change_str = f"\033[91m{change_str}\033[0m"

        print(f"\n  {symbol} - {price:.2f} ({change_str})")

        if result['patterns']:
            print(f"    Patterns:")
            for p in result['patterns']:
                type_color = '\033[92m' if p['type'] == 'BULLISH' else '\033[91m' if p['type'] == 'BEARISH' else '\033[93m'
                print(f"      {type_color}[{p['type']}]\033[0m {p['pattern']}")

        if result['signals']:
            print(f"    Signals:")
            for s in result['signals']:
                value_str = f" ({s['value']})" if s['value'] else ""
                print(f"      [{s['indicator']}] {s['signal']}{value_str}")

    # Summary
    print(f"\n{'='*70}")
    bullish_count = sum(1 for r in results for p in r['patterns'] if p['type'] == 'BULLISH')
    bearish_count = sum(1 for r in results for p in r['patterns'] if p['type'] == 'BEARISH')

    print(f"  Summary: {bullish_count} bullish patterns, {bearish_count} bearish patterns")


if __name__ == "__main__":
    main()
