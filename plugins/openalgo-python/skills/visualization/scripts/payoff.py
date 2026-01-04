#!/usr/bin/env python3
"""
Generate options payoff diagrams using OpenAlgo data.

Usage:
    python payoff.py --strategy long_call --strike 26000 --premium 250
    python payoff.py --strategy iron_condor --underlying NIFTY --expiry 30JAN25
    python payoff.py --strategy straddle --strike 26000 --call-premium 250 --put-premium 245
"""

import os
import sys
import argparse
import numpy as np

try:
    import plotly.graph_objects as go
except ImportError:
    print("Error: plotly is required. Install with: pip install plotly")
    sys.exit(1)

from openalgo import api


def get_client():
    """Initialize OpenAlgo client with API key."""
    api_key = os.environ.get("OPENALGO_API_KEY")
    host = os.environ.get("OPENALGO_HOST", "http://127.0.0.1:5000")

    if not api_key:
        return None

    return api(api_key=api_key, host=host)


def long_call_payoff(spot_range, strike, premium):
    """Long call option payoff."""
    return np.maximum(spot_range - strike, 0) - premium


def short_call_payoff(spot_range, strike, premium):
    """Short call option payoff."""
    return premium - np.maximum(spot_range - strike, 0)


def long_put_payoff(spot_range, strike, premium):
    """Long put option payoff."""
    return np.maximum(strike - spot_range, 0) - premium


def short_put_payoff(spot_range, strike, premium):
    """Short put option payoff."""
    return premium - np.maximum(strike - spot_range, 0)


def create_payoff_chart(strategy, **kwargs):
    """
    Create payoff diagram for various options strategies.

    Supported strategies:
    - long_call, short_call
    - long_put, short_put
    - straddle, strangle
    - iron_condor
    - bull_call_spread, bear_put_spread
    - butterfly

    Args:
        strategy: Strategy name
        **kwargs: Strategy-specific parameters

    Returns:
        Plotly figure object
    """
    strike = kwargs.get('strike', 26000)
    premium = kwargs.get('premium', 250)
    spot = kwargs.get('spot', strike)

    # Define spot range (±5% from strike)
    spot_range = np.arange(spot * 0.95, spot * 1.05, spot * 0.001)

    fig = go.Figure()

    if strategy == 'long_call':
        payoff = long_call_payoff(spot_range, strike, premium)
        title = f'Long Call (Strike: {strike}, Premium: {premium})'

    elif strategy == 'short_call':
        payoff = short_call_payoff(spot_range, strike, premium)
        title = f'Short Call (Strike: {strike}, Premium: {premium})'

    elif strategy == 'long_put':
        payoff = long_put_payoff(spot_range, strike, premium)
        title = f'Long Put (Strike: {strike}, Premium: {premium})'

    elif strategy == 'short_put':
        payoff = short_put_payoff(spot_range, strike, premium)
        title = f'Short Put (Strike: {strike}, Premium: {premium})'

    elif strategy == 'straddle':
        call_prem = kwargs.get('call_premium', 250)
        put_prem = kwargs.get('put_premium', 245)

        long_straddle = (long_call_payoff(spot_range, strike, call_prem) +
                        long_put_payoff(spot_range, strike, put_prem))
        short_straddle = -long_straddle

        fig.add_trace(go.Scatter(x=spot_range, y=long_straddle, name='Long Straddle',
                                 line=dict(color='green', width=2)))
        fig.add_trace(go.Scatter(x=spot_range, y=short_straddle, name='Short Straddle',
                                 line=dict(color='red', width=2)))
        title = f'Straddle (Strike: {strike})'
        payoff = None

    elif strategy == 'strangle':
        call_strike = kwargs.get('call_strike', strike * 1.02)
        put_strike = kwargs.get('put_strike', strike * 0.98)
        call_prem = kwargs.get('call_premium', 100)
        put_prem = kwargs.get('put_premium', 100)

        long_strangle = (long_call_payoff(spot_range, call_strike, call_prem) +
                        long_put_payoff(spot_range, put_strike, put_prem))

        fig.add_trace(go.Scatter(x=spot_range, y=long_strangle, name='Long Strangle',
                                 fill='tozeroy', line=dict(color='green', width=2)))
        title = f'Strangle (CE: {call_strike}, PE: {put_strike})'
        payoff = None

    elif strategy == 'iron_condor':
        pe_buy = kwargs.get('pe_buy', strike * 0.96)
        pe_sell = kwargs.get('pe_sell', strike * 0.98)
        ce_sell = kwargs.get('ce_sell', strike * 1.02)
        ce_buy = kwargs.get('ce_buy', strike * 1.04)

        pe_buy_prem = kwargs.get('pe_buy_premium', 30)
        pe_sell_prem = kwargs.get('pe_sell_premium', 80)
        ce_sell_prem = kwargs.get('ce_sell_premium', 80)
        ce_buy_prem = kwargs.get('ce_buy_premium', 30)

        payoff = (long_put_payoff(spot_range, pe_buy, pe_buy_prem) +
                 short_put_payoff(spot_range, pe_sell, pe_sell_prem) +
                 short_call_payoff(spot_range, ce_sell, ce_sell_prem) +
                 long_call_payoff(spot_range, ce_buy, ce_buy_prem))

        title = f'Iron Condor (PE: {pe_buy}/{pe_sell}, CE: {ce_sell}/{ce_buy})'

    elif strategy == 'bull_call_spread':
        buy_strike = strike
        sell_strike = kwargs.get('sell_strike', strike * 1.02)
        buy_prem = kwargs.get('buy_premium', 200)
        sell_prem = kwargs.get('sell_premium', 100)

        payoff = (long_call_payoff(spot_range, buy_strike, buy_prem) +
                 short_call_payoff(spot_range, sell_strike, sell_prem))

        title = f'Bull Call Spread (Buy: {buy_strike}, Sell: {sell_strike})'

    elif strategy == 'bear_put_spread':
        buy_strike = strike
        sell_strike = kwargs.get('sell_strike', strike * 0.98)
        buy_prem = kwargs.get('buy_premium', 200)
        sell_prem = kwargs.get('sell_premium', 100)

        payoff = (long_put_payoff(spot_range, buy_strike, buy_prem) +
                 short_put_payoff(spot_range, sell_strike, sell_prem))

        title = f'Bear Put Spread (Buy: {buy_strike}, Sell: {sell_strike})'

    elif strategy == 'butterfly':
        lower = kwargs.get('lower_strike', strike * 0.98)
        upper = kwargs.get('upper_strike', strike * 1.02)
        lower_prem = kwargs.get('lower_premium', 150)
        mid_prem = kwargs.get('mid_premium', 80)
        upper_prem = kwargs.get('upper_premium', 30)

        payoff = (long_call_payoff(spot_range, lower, lower_prem) +
                 2 * short_call_payoff(spot_range, strike, mid_prem) +
                 long_call_payoff(spot_range, upper, upper_prem))

        title = f'Butterfly (Lower: {lower}, Mid: {strike}, Upper: {upper})'

    else:
        print(f"Unknown strategy: {strategy}")
        return None

    # Add payoff trace if not already added
    if payoff is not None:
        color = 'green' if 'long' in strategy or 'bull' in strategy else 'purple'
        fig.add_trace(go.Scatter(
            x=spot_range, y=payoff,
            name=strategy.replace('_', ' ').title(),
            fill='tozeroy',
            line=dict(color=color, width=2)
        ))

    # Common layout
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=strike, line_dash="dash", line_color="blue",
                  annotation_text=f"Strike: {strike}")

    fig.update_layout(
        title=title,
        xaxis_title='Spot Price at Expiry',
        yaxis_title='Profit/Loss',
        template='plotly_dark',
        height=500
    )

    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Generate options payoff diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Strategies:
  long_call, short_call, long_put, short_put
  straddle, strangle
  iron_condor
  bull_call_spread, bear_put_spread
  butterfly

Examples:
  # Long Call
  python payoff.py --strategy long_call --strike 26000 --premium 250

  # Straddle
  python payoff.py --strategy straddle --strike 26000 --call-premium 250 --put-premium 245

  # Iron Condor
  python payoff.py --strategy iron_condor --strike 26000

  # Bull Call Spread
  python payoff.py --strategy bull_call_spread --strike 26000 --sell-strike 26500 --buy-premium 200 --sell-premium 100

  # Save to file
  python payoff.py --strategy iron_condor --strike 26000 --output payoff.html
        """
    )

    parser.add_argument("--strategy", "-s", required=True,
                        choices=['long_call', 'short_call', 'long_put', 'short_put',
                                'straddle', 'strangle', 'iron_condor',
                                'bull_call_spread', 'bear_put_spread', 'butterfly'],
                        help="Options strategy")
    parser.add_argument("--strike", type=float, default=26000, help="Strike price")
    parser.add_argument("--premium", type=float, default=250, help="Option premium")
    parser.add_argument("--call-premium", type=float, help="Call option premium")
    parser.add_argument("--put-premium", type=float, help="Put option premium")
    parser.add_argument("--sell-strike", type=float, help="Sell strike for spreads")
    parser.add_argument("--buy-premium", type=float, help="Buy premium for spreads")
    parser.add_argument("--sell-premium", type=float, help="Sell premium for spreads")
    parser.add_argument("--output", "-o", help="Output file path (.html)")

    args = parser.parse_args()

    kwargs = {
        'strike': args.strike,
        'premium': args.premium,
        'spot': args.strike
    }

    if args.call_premium:
        kwargs['call_premium'] = args.call_premium
    if args.put_premium:
        kwargs['put_premium'] = args.put_premium
    if args.sell_strike:
        kwargs['sell_strike'] = args.sell_strike
    if args.buy_premium:
        kwargs['buy_premium'] = args.buy_premium
    if args.sell_premium:
        kwargs['sell_premium'] = args.sell_premium

    fig = create_payoff_chart(args.strategy, **kwargs)

    if fig:
        if args.output:
            fig.write_html(args.output)
            print(f"Chart saved to: {args.output}")
        else:
            fig.show()


if __name__ == "__main__":
    main()
