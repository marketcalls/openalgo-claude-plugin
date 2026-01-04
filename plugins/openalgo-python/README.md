# OpenAlgo Python Plugin for Claude Code

Complete OpenAlgo Python SDK integration for algorithmic trading. Build trading strategies, options strategies, real-time dashboards, and full-stack trading applications. Supports 25+ Indian brokers with a unified API.

## Skills Included (6)

### 1. trading-core
Core trading operations - place orders, smart orders, basket orders, split orders, and order management.

```bash
python scripts/place_order.py --symbol RELIANCE --exchange NSE --action BUY --quantity 1 --product MIS
```

### 2. options-trading
Options strategies - single leg orders, multi-leg strategies (Iron Condor, Straddle, Strangle, Spreads), Greeks calculation.

```bash
python scripts/iron_condor.py --underlying NIFTY --expiry 30JAN25 --quantity 75
```

### 3. market-data
Market data retrieval - real-time quotes, historical OHLCV, market depth, option chains, WebSocket streaming.

```bash
python scripts/stream.py --symbols NIFTY,BANKNIFTY --exchange NSE_INDEX --mode ltp
```

### 4. visualization
Data visualization - candlestick charts, options payoff diagrams, P&L dashboards, Streamlit apps.

```bash
python scripts/candlestick.py --symbol SBIN --exchange NSE --interval 5m --days 5
```

### 5. portfolio
Portfolio management - funds, positions, holdings, order book, trade book, margin calculator.

```bash
python scripts/portfolio.py --summary
```

### 6. technical-indicators
Technical analysis with TA-Lib - moving averages, RSI, MACD, Bollinger Bands, Stochastic, candlestick patterns, and strategy signals.

```bash
python scripts/indicators.py --symbol SBIN --exchange NSE --interval 5m --days 5
python scripts/signals.py --symbol NIFTY --exchange NSE_INDEX --strategy all
python scripts/scanner.py --watchlist nifty50 --pattern bullish
```

## Installation

```bash
# Install OpenAlgo SDK
pip install openalgo

# Set environment variables
export OPENALGO_API_KEY="your_api_key"
export OPENALGO_HOST="http://127.0.0.1:5000"
```

## Quick Start

```python
from openalgo import api

client = api(
    api_key='your_api_key',
    host='http://127.0.0.1:5000'
)

# Place a market order
response = client.placeorder(
    strategy="MyStrategy",
    symbol="RELIANCE",
    action="BUY",
    exchange="NSE",
    price_type="MARKET",
    product="MIS",
    quantity=1
)

print(response)
# {'orderid': '250408000989443', 'status': 'success'}
```

## Symbol Format

| Type | Format | Example |
|------|--------|---------|
| Equity | `SYMBOL` | `RELIANCE` |
| Future | `SYMBOL[DDMMMYY]FUT` | `NIFTY30JAN25FUT` |
| Option | `SYMBOL[DDMMMYY][STRIKE][CE/PE]` | `NIFTY30JAN2526000CE` |

## Exchanges

- `NSE` - NSE Equity
- `BSE` - BSE Equity
- `NFO` - NSE Futures & Options
- `BFO` - BSE Futures & Options
- `CDS` - NSE Currency Derivatives
- `MCX` - MCX Commodity
- `NSE_INDEX` - NSE Indices
- `BSE_INDEX` - BSE Indices

## Paper Trading

Always test strategies in analyzer mode first:

```python
# Enable paper trading
client.analyzertoggle(mode=True)

# Place test orders (won't execute)
response = client.placeorder(...)

# Check analyzer status
status = client.analyzerstatus()
```

## Requirements

- Python 3.8+
- openalgo >= 1.0.45
- httpx
- pandas
- numpy
- plotly (for visualization)
- streamlit (for dashboards)
- TA-Lib (for technical indicators)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Links

- [OpenAlgo Documentation](https://docs.openalgo.in)
- [OpenAlgo GitHub](https://github.com/marketcalls/openalgo)
- [PyPI Package](https://pypi.org/project/openalgo/)
