#!/usr/bin/env python3
"""
Calculate technical indicators using TA-Lib and OpenAlgo data.

Usage:
    python indicators.py --symbol SBIN --exchange NSE --interval 5m --days 5
    python indicators.py --symbol NIFTY --exchange NSE_INDEX --interval D --days 30 --output indicators.csv
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
    print("Install with: pip install TA-Lib numpy pandas")
    sys.exit(1)


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host)


def calculate_indicators(df):
    """
    Calculate comprehensive technical indicators.

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with all indicators added
    """
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_ = df['open'].values
    volume = df['volume'].values.astype(float)

    print("\nCalculating indicators...")

    # === TREND INDICATORS ===
    print("  - Moving Averages (SMA, EMA)")
    df['SMA_10'] = talib.SMA(close, timeperiod=10)
    df['SMA_20'] = talib.SMA(close, timeperiod=20)
    df['SMA_50'] = talib.SMA(close, timeperiod=50)
    df['EMA_9'] = talib.EMA(close, timeperiod=9)
    df['EMA_21'] = talib.EMA(close, timeperiod=21)

    # Bollinger Bands
    print("  - Bollinger Bands")
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = talib.BBANDS(close, timeperiod=20)
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle'] * 100

    # === MOMENTUM INDICATORS ===
    print("  - RSI")
    df['RSI'] = talib.RSI(close, timeperiod=14)

    print("  - MACD")
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    print("  - Stochastic")
    df['Stoch_K'], df['Stoch_D'] = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)

    print("  - ADX")
    df['ADX'] = talib.ADX(high, low, close, timeperiod=14)
    df['Plus_DI'] = talib.PLUS_DI(high, low, close, timeperiod=14)
    df['Minus_DI'] = talib.MINUS_DI(high, low, close, timeperiod=14)

    print("  - CCI, Williams %R, MOM, ROC")
    df['CCI'] = talib.CCI(high, low, close, timeperiod=20)
    df['Williams_R'] = talib.WILLR(high, low, close, timeperiod=14)
    df['MOM'] = talib.MOM(close, timeperiod=10)
    df['ROC'] = talib.ROC(close, timeperiod=10)

    # === VOLATILITY INDICATORS ===
    print("  - ATR, NATR")
    df['ATR'] = talib.ATR(high, low, close, timeperiod=14)
    df['NATR'] = talib.NATR(high, low, close, timeperiod=14)

    # === VOLUME INDICATORS ===
    print("  - OBV, MFI, AD")
    df['OBV'] = talib.OBV(close, volume)
    df['MFI'] = talib.MFI(high, low, close, volume, timeperiod=14)
    df['AD'] = talib.AD(high, low, close, volume)

    return df


def generate_signals(df):
    """Generate trading signals based on indicators."""
    # RSI signals
    df['RSI_Signal'] = np.where(df['RSI'] < 30, 'OVERSOLD',
                       np.where(df['RSI'] > 70, 'OVERBOUGHT', 'NEUTRAL'))

    # MACD signals
    df['MACD_Cross'] = np.where(
        (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1)),
        'BUY',
        np.where(
            (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1)),
            'SELL',
            'HOLD'
        )
    )

    # EMA crossover
    df['EMA_Cross'] = np.where(df['EMA_9'] > df['EMA_21'], 'BULLISH', 'BEARISH')

    # BB signals
    df['BB_Signal'] = np.where(df['close'] < df['BB_Lower'], 'OVERSOLD',
                      np.where(df['close'] > df['BB_Upper'], 'OVERBOUGHT', 'NEUTRAL'))

    # ADX trend strength
    df['Trend_Strength'] = np.where(df['ADX'] > 25, 'STRONG',
                           np.where(df['ADX'] > 20, 'MODERATE', 'WEAK'))

    return df


def display_latest(df, symbol):
    """Display latest indicator values."""
    latest = df.iloc[-1]

    print(f"\n{'='*60}")
    print(f"  TECHNICAL ANALYSIS: {symbol}")
    print(f"  {df.index[-1]}")
    print(f"{'='*60}")

    print(f"\n  PRICE")
    print(f"    Close: {latest['close']:.2f}")
    print(f"    Change: {((latest['close']/df.iloc[-2]['close'])-1)*100:+.2f}%")

    print(f"\n  TREND")
    print(f"    SMA 20: {latest['SMA_20']:.2f} ({'Above' if latest['close'] > latest['SMA_20'] else 'Below'})")
    print(f"    SMA 50: {latest['SMA_50']:.2f} ({'Above' if latest['close'] > latest['SMA_50'] else 'Below'})")
    print(f"    EMA 9/21: {latest['EMA_Cross']}")

    print(f"\n  BOLLINGER BANDS")
    print(f"    Upper: {latest['BB_Upper']:.2f}")
    print(f"    Middle: {latest['BB_Middle']:.2f}")
    print(f"    Lower: {latest['BB_Lower']:.2f}")
    print(f"    Width: {latest['BB_Width']:.2f}%")
    print(f"    Signal: {latest['BB_Signal']}")

    print(f"\n  MOMENTUM")
    print(f"    RSI(14): {latest['RSI']:.2f} - {latest['RSI_Signal']}")
    print(f"    MACD: {latest['MACD']:.4f}")
    print(f"    MACD Signal: {latest['MACD_Signal']:.4f}")
    print(f"    MACD Cross: {latest['MACD_Cross']}")
    print(f"    Stoch %K: {latest['Stoch_K']:.2f}")
    print(f"    Stoch %D: {latest['Stoch_D']:.2f}")

    print(f"\n  TREND STRENGTH")
    print(f"    ADX: {latest['ADX']:.2f} - {latest['Trend_Strength']}")
    print(f"    +DI: {latest['Plus_DI']:.2f}")
    print(f"    -DI: {latest['Minus_DI']:.2f}")

    print(f"\n  VOLATILITY")
    print(f"    ATR: {latest['ATR']:.2f}")
    print(f"    NATR: {latest['NATR']:.2f}%")

    print(f"\n  VOLUME")
    print(f"    MFI: {latest['MFI']:.2f}")
    print(f"    Volume: {int(latest['volume']):,}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate technical indicators using TA-Lib",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 5-minute analysis
  python indicators.py --symbol SBIN --exchange NSE --interval 5m --days 5

  # Daily analysis for a month
  python indicators.py --symbol NIFTY --exchange NSE_INDEX --interval D --days 30

  # Save to CSV
  python indicators.py --symbol RELIANCE --exchange NSE --interval 15m --days 10 --output analysis.csv
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")
    parser.add_argument("--interval", "-i", default="5m",
                        choices=["1m", "3m", "5m", "10m", "15m", "30m", "1h", "D"],
                        help="Candle interval")
    parser.add_argument("--days", "-d", type=int, default=5, help="Number of days")
    parser.add_argument("--output", "-o", help="Output CSV file path")

    args = parser.parse_args()

    client = get_client()

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"\nFetching {args.symbol} data from {start_date} to {end_date}...")

    df = client.history(
        symbol=args.symbol,
        exchange=args.exchange,
        interval=args.interval,
        start_date=start_date,
        end_date=end_date
    )

    if df is None or len(df) == 0:
        print("Error: No data returned")
        sys.exit(1)

    print(f"Retrieved {len(df)} candles")

    # Calculate indicators
    df = calculate_indicators(df)
    df = generate_signals(df)

    # Display latest values
    display_latest(df, args.symbol)

    # Save to file if requested
    if args.output:
        df.to_csv(args.output)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
