#!/usr/bin/env python3
"""
Calculate Option Greeks using OpenAlgo API.

Usage:
    python greeks.py --symbol NIFTY30JAN2526000CE --exchange NFO
    python greeks.py --symbol BANKNIFTY30JAN2555000PE --exchange NFO --underlying BANKNIFTY
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


def calculate_greeks(symbol, exchange="NFO", underlying_symbol=None, underlying_exchange="NSE_INDEX",
                     interest_rate=0.0):
    """
    Calculate Option Greeks for a given option contract.

    Greeks Explanation:
    - Delta: Rate of change of option price with respect to underlying price
             CE: 0 to 1, PE: -1 to 0, ATM ≈ 0.5/-0.5
    - Gamma: Rate of change of delta with respect to underlying price
             Highest at ATM, decreases as you go ITM/OTM
    - Theta: Daily time decay (usually negative)
             Accelerates as expiry approaches
    - Vega: Sensitivity to volatility changes
             Higher for ATM options with more time to expiry
    - Rho: Sensitivity to interest rate changes
             Usually minimal impact

    Args:
        symbol: Option symbol (e.g., NIFTY30JAN2526000CE)
        exchange: Exchange code (NFO, BFO)
        underlying_symbol: Underlying symbol (auto-detected if not provided)
        underlying_exchange: Underlying exchange (NSE_INDEX, BSE_INDEX, NSE, BSE)
        interest_rate: Risk-free interest rate (default: 0)

    Returns:
        dict: Greeks and other option data
    """
    client = get_client()

    # Auto-detect underlying from symbol
    if underlying_symbol is None:
        if "NIFTY" in symbol and "BANK" not in symbol and "FIN" not in symbol and "MIDCP" not in symbol:
            underlying_symbol = "NIFTY"
        elif "BANKNIFTY" in symbol:
            underlying_symbol = "BANKNIFTY"
        elif "FINNIFTY" in symbol:
            underlying_symbol = "FINNIFTY"
        elif "MIDCPNIFTY" in symbol:
            underlying_symbol = "MIDCPNIFTY"
        elif "SENSEX" in symbol:
            underlying_symbol = "SENSEX"
            underlying_exchange = "BSE_INDEX"
        else:
            # Stock option - extract symbol
            underlying_symbol = symbol[:symbol.find("25")]  # Rough extraction
            underlying_exchange = "NSE"

    print(f"\nCalculating Greeks for: {symbol}")
    print(f"  Exchange: {exchange}")
    print(f"  Underlying: {underlying_symbol} ({underlying_exchange})")

    try:
        response = client.optiongreeks(
            symbol=symbol,
            exchange=exchange,
            interest_rate=interest_rate,
            underlying_symbol=underlying_symbol,
            underlying_exchange=underlying_exchange
        )

        if response.get('status') == 'success':
            print(f"\n[SUCCESS] Greeks calculated!")
            print(f"\n  Contract Details:")
            print(f"    Symbol: {response.get('symbol')}")
            print(f"    Option Type: {response.get('option_type')}")
            print(f"    Strike: {response.get('strike')}")
            print(f"    Expiry: {response.get('expiry_date')}")
            print(f"    Days to Expiry: {response.get('days_to_expiry'):.2f}")

            print(f"\n  Prices:")
            print(f"    Spot Price: {response.get('spot_price')}")
            print(f"    Option Price: {response.get('option_price')}")
            print(f"    IV: {response.get('implied_volatility')}%")

            greeks = response.get('greeks', {})
            print(f"\n  Greeks:")
            print(f"    Delta: {greeks.get('delta', 'N/A'):.4f}")
            print(f"    Gamma: {greeks.get('gamma', 'N/A'):.6f}")
            print(f"    Theta: {greeks.get('theta', 'N/A'):.4f}")
            print(f"    Vega:  {greeks.get('vega', 'N/A'):.4f}")
            print(f"    Rho:   {greeks.get('rho', 'N/A'):.4f}")

            # Interpretation
            delta = greeks.get('delta', 0)
            theta = greeks.get('theta', 0)
            print(f"\n  Interpretation:")
            print(f"    Delta: For every 1 point move in underlying, option moves {abs(delta):.2f} points")
            print(f"    Theta: Option loses Rs {abs(theta):.2f} per day due to time decay")

        else:
            print(f"\n[ERROR] Greeks calculation failed: {response}")

        return response

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate Option Greeks using OpenAlgo API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Greeks Reference:
  DELTA - Direction sensitivity
    CE: 0.5 (ATM) → 1.0 (deep ITM) → 0.0 (deep OTM)
    PE: -0.5 (ATM) → -1.0 (deep ITM) → 0.0 (deep OTM)

  GAMMA - Delta acceleration
    Highest at ATM, near expiry
    Important for scalpers

  THETA - Time decay
    Always negative for long options
    Accelerates exponentially near expiry

  VEGA - Volatility sensitivity
    Higher for longer-dated options
    ATM options have highest vega

  RHO - Interest rate sensitivity
    Usually minimal impact in India

Examples:
  # NIFTY Call Greeks
  python greeks.py --symbol NIFTY30JAN2526000CE --exchange NFO

  # BANKNIFTY Put Greeks
  python greeks.py --symbol BANKNIFTY30JAN2555000PE --exchange NFO --underlying BANKNIFTY

  # Stock option Greeks
  python greeks.py --symbol RELIANCE30JAN251400CE --exchange NFO --underlying RELIANCE --underlying-exchange NSE
        """
    )

    parser.add_argument("--symbol", "-s", required=True, help="Option symbol")
    parser.add_argument("--exchange", "-e", default="NFO", choices=["NFO", "BFO"], help="Exchange")
    parser.add_argument("--underlying", "-u", help="Underlying symbol (auto-detected if not provided)")
    parser.add_argument("--underlying-exchange", default="NSE_INDEX",
                        choices=["NSE_INDEX", "BSE_INDEX", "NSE", "BSE"], help="Underlying exchange")
    parser.add_argument("--interest-rate", "-r", type=float, default=0.0, help="Risk-free rate (default: 0)")

    args = parser.parse_args()

    calculate_greeks(
        symbol=args.symbol,
        exchange=args.exchange,
        underlying_symbol=args.underlying,
        underlying_exchange=args.underlying_exchange,
        interest_rate=args.interest_rate
    )


if __name__ == "__main__":
    main()
