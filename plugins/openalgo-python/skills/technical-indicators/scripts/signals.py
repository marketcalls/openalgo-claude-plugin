#!/usr/bin/env python3
"""
Generate trading signals based on technical indicator strategies.

Usage:
    python signals.py --symbol NIFTY --exchange NSE_INDEX --strategy rsi_oversold
    python signals.py --symbol SBIN --exchange NSE --strategy macd_cross --interval 15m
    python signals.py --symbol RELIANCE --exchange NSE --strategy all
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


def rsi_strategy(df, oversold=30, overbought=70):
    """RSI overbought/oversold strategy."""
    df['RSI'] = talib.RSI(df['close'].values, timeperiod=14)

    latest = df.iloc[-1]
    signal = None

    if latest['RSI'] < oversold:
        signal = 'BUY'
        reason = f"RSI={latest['RSI']:.1f} (Oversold < {oversold})"
    elif latest['RSI'] > overbought:
        signal = 'SELL'
        reason = f"RSI={latest['RSI']:.1f} (Overbought > {overbought})"
    else:
        signal = 'HOLD'
        reason = f"RSI={latest['RSI']:.1f} (Neutral zone)"

    return {'signal': signal, 'strategy': 'RSI', 'reason': reason, 'value': latest['RSI']}


def macd_cross_strategy(df):
    """MACD crossover strategy."""
    macd, signal, hist = talib.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD'] = macd
    df['MACD_Signal'] = signal

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if latest['MACD'] > latest['MACD_Signal'] and prev['MACD'] <= prev['MACD_Signal']:
        signal_type = 'BUY'
        reason = "MACD crossed above Signal line (Bullish)"
    elif latest['MACD'] < latest['MACD_Signal'] and prev['MACD'] >= prev['MACD_Signal']:
        signal_type = 'SELL'
        reason = "MACD crossed below Signal line (Bearish)"
    else:
        signal_type = 'HOLD'
        reason = f"MACD={'Above' if latest['MACD'] > latest['MACD_Signal'] else 'Below'} Signal"

    return {'signal': signal_type, 'strategy': 'MACD Cross', 'reason': reason, 'value': latest['MACD']}


def ema_cross_strategy(df, fast=9, slow=21):
    """EMA crossover strategy."""
    df['EMA_Fast'] = talib.EMA(df['close'].values, timeperiod=fast)
    df['EMA_Slow'] = talib.EMA(df['close'].values, timeperiod=slow)

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if latest['EMA_Fast'] > latest['EMA_Slow'] and prev['EMA_Fast'] <= prev['EMA_Slow']:
        signal = 'BUY'
        reason = f"EMA {fast} crossed above EMA {slow} (Golden Cross)"
    elif latest['EMA_Fast'] < latest['EMA_Slow'] and prev['EMA_Fast'] >= prev['EMA_Slow']:
        signal = 'SELL'
        reason = f"EMA {fast} crossed below EMA {slow} (Death Cross)"
    else:
        trend = 'Bullish' if latest['EMA_Fast'] > latest['EMA_Slow'] else 'Bearish'
        signal = 'HOLD'
        reason = f"EMA trend: {trend}"

    return {'signal': signal, 'strategy': f'EMA {fast}/{slow} Cross', 'reason': reason,
            'value': latest['EMA_Fast'] - latest['EMA_Slow']}


def bollinger_band_strategy(df):
    """Bollinger Band mean reversion strategy."""
    upper, middle, lower = talib.BBANDS(df['close'].values, timeperiod=20)
    df['BB_Upper'] = upper
    df['BB_Middle'] = middle
    df['BB_Lower'] = lower

    latest = df.iloc[-1]
    close = latest['close']

    if close < lower[-1]:
        signal = 'BUY'
        reason = f"Price ({close:.2f}) below Lower BB ({lower[-1]:.2f})"
    elif close > upper[-1]:
        signal = 'SELL'
        reason = f"Price ({close:.2f}) above Upper BB ({upper[-1]:.2f})"
    else:
        signal = 'HOLD'
        position = (close - lower[-1]) / (upper[-1] - lower[-1]) * 100
        reason = f"Price at {position:.0f}% within bands"

    return {'signal': signal, 'strategy': 'Bollinger Bands', 'reason': reason, 'value': close}


def stochastic_strategy(df, oversold=20, overbought=80):
    """Stochastic oscillator strategy."""
    slowk, slowd = talib.STOCH(df['high'].values, df['low'].values, df['close'].values)
    df['Stoch_K'] = slowk
    df['Stoch_D'] = slowd

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if latest['Stoch_K'] < oversold and latest['Stoch_K'] > latest['Stoch_D'] and prev['Stoch_K'] <= prev['Stoch_D']:
        signal = 'BUY'
        reason = f"%K={latest['Stoch_K']:.1f} crossed above %D in oversold zone"
    elif latest['Stoch_K'] > overbought and latest['Stoch_K'] < latest['Stoch_D'] and prev['Stoch_K'] >= prev['Stoch_D']:
        signal = 'SELL'
        reason = f"%K={latest['Stoch_K']:.1f} crossed below %D in overbought zone"
    else:
        signal = 'HOLD'
        zone = 'Oversold' if latest['Stoch_K'] < oversold else 'Overbought' if latest['Stoch_K'] > overbought else 'Neutral'
        reason = f"%K={latest['Stoch_K']:.1f}, %D={latest['Stoch_D']:.1f} ({zone})"

    return {'signal': signal, 'strategy': 'Stochastic', 'reason': reason, 'value': latest['Stoch_K']}


def adx_trend_strategy(df, threshold=25):
    """ADX trend strength with DI crossover."""
    df['ADX'] = talib.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
    df['Plus_DI'] = talib.PLUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
    df['Minus_DI'] = talib.MINUS_DI(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if latest['ADX'] > threshold:
        if latest['Plus_DI'] > latest['Minus_DI'] and prev['Plus_DI'] <= prev['Minus_DI']:
            signal = 'BUY'
            reason = f"Strong uptrend: ADX={latest['ADX']:.1f}, +DI crossed above -DI"
        elif latest['Minus_DI'] > latest['Plus_DI'] and prev['Minus_DI'] <= prev['Plus_DI']:
            signal = 'SELL'
            reason = f"Strong downtrend: ADX={latest['ADX']:.1f}, -DI crossed above +DI"
        else:
            trend = 'Bullish' if latest['Plus_DI'] > latest['Minus_DI'] else 'Bearish'
            signal = 'HOLD'
            reason = f"Strong {trend} trend continuing: ADX={latest['ADX']:.1f}"
    else:
        signal = 'HOLD'
        reason = f"Weak trend: ADX={latest['ADX']:.1f} < {threshold}"

    return {'signal': signal, 'strategy': 'ADX Trend', 'reason': reason, 'value': latest['ADX']}


def supertrend_strategy(df, period=10, multiplier=3):
    """SuperTrend indicator strategy."""
    df['ATR'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
    hl2 = (df['high'] + df['low']) / 2

    upperband = hl2 + (multiplier * df['ATR'])
    lowerband = hl2 - (multiplier * df['ATR'])

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)

    for i in range(period, len(df)):
        if df['close'].iloc[i] > upperband.iloc[i-1]:
            supertrend.iloc[i] = lowerband.iloc[i]
            direction.iloc[i] = 1
        elif df['close'].iloc[i] < lowerband.iloc[i-1]:
            supertrend.iloc[i] = upperband.iloc[i]
            direction.iloc[i] = -1
        else:
            supertrend.iloc[i] = supertrend.iloc[i-1] if pd.notna(supertrend.iloc[i-1]) else upperband.iloc[i]
            direction.iloc[i] = direction.iloc[i-1] if pd.notna(direction.iloc[i-1]) else 1

    latest_dir = direction.iloc[-1]
    prev_dir = direction.iloc[-2]

    if latest_dir == 1 and prev_dir == -1:
        signal = 'BUY'
        reason = f"SuperTrend turned Bullish at {supertrend.iloc[-1]:.2f}"
    elif latest_dir == -1 and prev_dir == 1:
        signal = 'SELL'
        reason = f"SuperTrend turned Bearish at {supertrend.iloc[-1]:.2f}"
    else:
        trend = 'Bullish' if latest_dir == 1 else 'Bearish'
        signal = 'HOLD'
        reason = f"SuperTrend {trend}, level: {supertrend.iloc[-1]:.2f}"

    return {'signal': signal, 'strategy': 'SuperTrend', 'reason': reason, 'value': supertrend.iloc[-1]}


STRATEGIES = {
    'rsi_oversold': rsi_strategy,
    'macd_cross': macd_cross_strategy,
    'ema_cross': ema_cross_strategy,
    'bollinger': bollinger_band_strategy,
    'stochastic': stochastic_strategy,
    'adx_trend': adx_trend_strategy,
    'supertrend': supertrend_strategy,
}


def run_all_strategies(df):
    """Run all available strategies."""
    results = []
    for name, func in STRATEGIES.items():
        try:
            result = func(df.copy())
            results.append(result)
        except Exception as e:
            print(f"  Error in {name}: {e}")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate trading signals based on technical strategies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Strategies:
  rsi_oversold  - RSI overbought/oversold
  macd_cross    - MACD line crossover
  ema_cross     - EMA 9/21 crossover
  bollinger     - Bollinger Band mean reversion
  stochastic    - Stochastic oscillator
  adx_trend     - ADX trend strength
  supertrend    - SuperTrend indicator
  all           - Run all strategies

Examples:
  python signals.py --symbol NIFTY --exchange NSE_INDEX --strategy rsi_oversold
  python signals.py --symbol SBIN --exchange NSE --strategy macd_cross --interval 15m
  python signals.py --symbol RELIANCE --exchange NSE --strategy all --days 10
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")
    parser.add_argument("--strategy", "-st", default="all",
                        choices=list(STRATEGIES.keys()) + ['all'],
                        help="Strategy to use")
    parser.add_argument("--interval", "-i", default="5m",
                        choices=["1m", "3m", "5m", "10m", "15m", "30m", "1h", "D"],
                        help="Candle interval")
    parser.add_argument("--days", "-d", type=int, default=30, help="Days of data")

    args = parser.parse_args()

    client = get_client()

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"\nFetching {args.symbol} data...")

    df = client.history(
        symbol=args.symbol,
        exchange=args.exchange,
        interval=args.interval,
        start_date=start_date,
        end_date=end_date
    )

    if df is None or len(df) < 50:
        print("Error: Insufficient data (need at least 50 candles)")
        sys.exit(1)

    print(f"Analyzing {len(df)} candles...")

    print(f"\n{'='*60}")
    print(f"  SIGNAL ANALYSIS: {args.symbol} ({args.exchange})")
    print(f"  Interval: {args.interval} | Data: {args.days} days")
    print(f"  Price: {df.iloc[-1]['close']:.2f}")
    print(f"{'='*60}")

    if args.strategy == 'all':
        results = run_all_strategies(df)
    else:
        results = [STRATEGIES[args.strategy](df)]

    print(f"\n{'Strategy':<20} {'Signal':<8} {'Reason'}")
    print("-" * 70)

    buy_count = sell_count = hold_count = 0
    for result in results:
        signal = result['signal']
        if signal == 'BUY':
            signal_str = f"\033[92m{signal}\033[0m"
            buy_count += 1
        elif signal == 'SELL':
            signal_str = f"\033[91m{signal}\033[0m"
            sell_count += 1
        else:
            signal_str = signal
            hold_count += 1

        print(f"{result['strategy']:<20} {signal_str:<17} {result['reason']}")

    print("-" * 70)
    print(f"\nSummary: {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD")

    if buy_count > sell_count:
        print(f"\n  \033[92mOverall Bias: BULLISH\033[0m")
    elif sell_count > buy_count:
        print(f"\n  \033[91mOverall Bias: BEARISH\033[0m")
    else:
        print(f"\n  Overall Bias: NEUTRAL")


if __name__ == "__main__":
    main()
