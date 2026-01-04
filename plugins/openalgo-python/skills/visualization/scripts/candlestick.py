#!/usr/bin/env python3
"""
Generate candlestick charts using OpenAlgo data.

Usage:
    python candlestick.py --symbol SBIN --exchange NSE --interval 5m --days 5
    python candlestick.py --symbol NIFTY --exchange NSE_INDEX --interval D --days 30 --output chart.html
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from openalgo import api

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    print("Error: plotly is required. Install with: pip install plotly")
    sys.exit(1)


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        print("Error: OPENALGO_API_KEY environment variable is not set.")
        sys.exit(1)

    return api(api_key=api_key, host=host)


def create_candlestick_chart(symbol, exchange, interval, days, output=None,
                              show_volume=True, show_ma=True):
    """
    Create a candlestick chart with optional volume and moving averages.

    Args:
        symbol: Trading symbol
        exchange: Exchange code
        interval: Candle interval
        days: Number of days of data
        output: Output file path (HTML)
        show_volume: Show volume bars
        show_ma: Show moving averages

    Returns:
        Plotly figure object
    """
    client = get_client()

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print(f"\nFetching data for {symbol}...")

    df = client.history(
        symbol=symbol,
        exchange=exchange,
        interval=interval,
        start_date=start_date,
        end_date=end_date
    )

    if df is None or len(df) == 0:
        print("Error: No data returned")
        return None

    print(f"Retrieved {len(df)} candles")

    # Calculate moving averages if requested
    if show_ma and len(df) >= 20:
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        if len(df) >= 50:
            df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['EMA_9'] = df['close'].ewm(span=9, adjust=False).mean()

    # Create subplots
    if show_volume:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                           vertical_spacing=0.03,
                           row_heights=[0.7, 0.3])
    else:
        fig = make_subplots(rows=1, cols=1)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=symbol,
        increasing_line_color='green',
        decreasing_line_color='red'
    ), row=1, col=1)

    # Moving averages
    if show_ma and 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_20'],
            name='SMA 20', line=dict(color='blue', width=1)
        ), row=1, col=1)

        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_50'],
                name='SMA 50', line=dict(color='orange', width=1)
            ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df['EMA_9'],
            name='EMA 9', line=dict(color='purple', width=1)
        ), row=1, col=1)

    # Volume bars
    if show_volume:
        colors = ['green' if c >= o else 'red' for c, o in zip(df['close'], df['open'])]
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            marker_color=colors,
            name='Volume',
            showlegend=False
        ), row=2, col=1)

    # Layout
    fig.update_layout(
        title=f'{symbol} ({exchange}) - {interval} Chart',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=700
    )

    if show_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    # Save or show
    if output:
        fig.write_html(output)
        print(f"\nChart saved to: {output}")
    else:
        fig.show()

    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Generate candlestick charts using OpenAlgo data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic chart
  python candlestick.py --symbol SBIN --exchange NSE --interval 5m --days 5

  # Daily chart for a month
  python candlestick.py --symbol NIFTY --exchange NSE_INDEX --interval D --days 30

  # Save to file
  python candlestick.py --symbol RELIANCE --exchange NSE --interval 15m --days 10 --output reliance.html

  # Without volume
  python candlestick.py --symbol TCS --exchange NSE --interval 1h --days 15 --no-volume

  # Without moving averages
  python candlestick.py --symbol INFY --exchange NSE --interval 5m --days 3 --no-ma
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    parser.add_argument("--exchange", "-e", required=True,
                        choices=["NSE", "BSE", "NFO", "MCX", "NSE_INDEX", "BSE_INDEX"],
                        help="Exchange code")
    parser.add_argument("--interval", "-i", default="5m",
                        choices=["1m", "3m", "5m", "10m", "15m", "30m", "1h", "D"],
                        help="Candle interval (default: 5m)")
    parser.add_argument("--days", "-d", type=int, default=5, help="Number of days (default: 5)")
    parser.add_argument("--output", "-o", help="Output file path (.html)")
    parser.add_argument("--no-volume", action="store_true", help="Hide volume bars")
    parser.add_argument("--no-ma", action="store_true", help="Hide moving averages")

    args = parser.parse_args()

    create_candlestick_chart(
        symbol=args.symbol,
        exchange=args.exchange,
        interval=args.interval,
        days=args.days,
        output=args.output,
        show_volume=not args.no_volume,
        show_ma=not args.no_ma
    )


if __name__ == "__main__":
    main()
