# OpenAlgo Marketplace

Official Claude Code plugin marketplace for [OpenAlgo](https://openalgo.in) - the unified algorithmic trading platform for Indian markets.

## About OpenAlgo

OpenAlgo provides a single API to connect with 25+ Indian brokers including Zerodha, Angel One, Upstox, Fyers, Dhan, and many more. Write your trading strategy once, deploy it with any broker.

## Available Plugins

### openalgo-python

Complete OpenAlgo Python SDK integration for algorithmic trading. Includes 5 skills:

| Skill | Description |
|-------|-------------|
| **trading-core** | Order placement, smart orders, basket orders, split orders |
| **options-trading** | Options strategies (Iron Condor, Straddle, Spreads), Greeks calculation |
| **market-data** | Real-time quotes, historical data, WebSocket streaming, option chains |
| **visualization** | Candlestick charts, payoff diagrams, Streamlit dashboards |
| **portfolio** | Funds, positions, holdings, margin calculator |

## Installation

### 1. Add the Marketplace

```bash
claude /plugin marketplace add https://github.com/marketcalls/openalgo_marketplace
```

### 2. Install the Plugin

```bash
claude /plugin install openalgo-python
```

### 3. Set Environment Variables

```bash
# Linux/macOS
export OPENALGO_API_KEY="your_api_key_here"
export OPENALGO_HOST="http://127.0.0.1:5000"

# Windows
setx OPENALGO_API_KEY "your_api_key_here"
setx OPENALGO_HOST "http://127.0.0.1:5000"
```

## Quick Start

### Place an Order

```
claude "buy 1 share of RELIANCE at market price"
```

### Create Options Strategy

```
claude "create an iron condor on NIFTY expiring 30JAN25 with 75 quantity"
```

### Get Market Data

```
claude "get the current price of NIFTY and BANKNIFTY"
```

### Build a Dashboard

```
claude "create a Streamlit dashboard showing my portfolio positions and P&L"
```

## Features

### Unified Symbol Format

OpenAlgo standardizes symbols across all brokers:

| Type | Format | Example |
|------|--------|---------|
| Equity | `SYMBOL` | `RELIANCE`, `TCS` |
| Future | `SYMBOL[DDMMMYY]FUT` | `NIFTY30JAN25FUT` |
| Option | `SYMBOL[DDMMMYY][STRIKE][CE/PE]` | `NIFTY30JAN2526000CE` |

### Supported Exchanges

- **NSE** - National Stock Exchange (Equity)
- **BSE** - Bombay Stock Exchange (Equity)
- **NFO** - NSE Futures & Options
- **BFO** - BSE Futures & Options
- **CDS** - NSE Currency Derivatives
- **BCD** - BSE Currency Derivatives
- **MCX** - Multi Commodity Exchange
- **NSE_INDEX** - NSE Indices (NIFTY, BANKNIFTY)
- **BSE_INDEX** - BSE Indices (SENSEX, BANKEX)

### Options Offset System

Select strikes relative to ATM:

| Offset | Meaning |
|--------|---------|
| `ATM` | At The Money |
| `ITM1`-`ITM10` | In The Money |
| `OTM1`-`OTM10` | Out of The Money |

### Real-time Streaming

WebSocket support for live data:

```python
from openalgo import api

client = api(
    api_key='your_key',
    host='http://127.0.0.1:5000',
    ws_url='ws://127.0.0.1:8765'
)

client.connect()
client.subscribe_ltp([
    {"exchange": "NSE_INDEX", "symbol": "NIFTY"},
    {"exchange": "NSE", "symbol": "RELIANCE"}
], on_data_received=lambda data: print(data))
```

## Documentation

- [OpenAlgo Documentation](https://docs.openalgo.in)
- [API Reference](https://docs.openalgo.in/api-documentation/v1)
- [Python SDK](https://pypi.org/project/openalgo/)

## Supported Brokers

OpenAlgo supports 25+ Indian brokers including:

- Zerodha (Kite)
- Angel One
- Upstox
- Fyers
- Dhan
- 5Paisa
- ICICI Direct
- Kotak Securities
- IIFL Securities
- Motilal Oswal
- And many more...

## Contributing

Contributions are welcome! Please read the [CLAUDE.md](CLAUDE.md) for development guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [OpenAlgo Website](https://openalgo.in)
- [OpenAlgo GitHub](https://github.com/marketcalls/openalgo)
- [Claude Code Plugins](https://docs.claude.com/en/docs/claude-code/plugins)
