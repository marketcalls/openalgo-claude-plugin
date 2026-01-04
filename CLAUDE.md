# OpenAlgo Marketplace - Claude Code Plugin Marketplace

This repository is a Claude Code plugin marketplace that distributes the `openalgo-python` plugin to developers building algorithmic trading applications, trading strategies, real-time dashboards, and data visualization tools.

## Repository Structure

```
openalgo_marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog (lists available plugins)
└── plugins/
    └── openalgo-python/          # The actual plugin
        ├── .claude-plugin/
        │   └── plugin.json       # Plugin metadata
        ├── skills/
        │   ├── trading-core/     # Order placement, smart orders, basket orders
        │   ├── options-trading/  # Options strategies, multi-leg orders, Greeks
        │   ├── market-data/      # Quotes, history, streaming, option chains
        │   ├── visualization/    # Charts, payoff diagrams, dashboards
        │   └── portfolio/        # Funds, positions, holdings, margin
        ├── README.md             # Plugin documentation
        └── LICENSE               # AGPL-3.0 License
```

## Philosophy: Unified Trading API for Indian Markets

**Make algorithmic trading accessible through a single API across 25+ brokers—no broker-specific code required.**

When working on this repository, follow these principles:

1. **Understand** → Grasp the OpenAlgo SDK capabilities and symbol standardization
2. **Plan** → Design trading strategies, dashboards, or applications
3. **Implement** → Build using the unified API patterns
4. **Test** → Use Analyzer mode for paper trading before going live
5. **Document** → Update skills and examples as new patterns emerge

## Working with This Repository

### Adding a New Skill

1. Create skill directory: `plugins/openalgo-python/skills/new-skill/`
2. Add skill structure:
   ```
   skills/new-skill/
   ├── SKILL.md           # Skill definition with frontmatter (name, description)
   ├── scripts/           # Python helper scripts
   └── requirements.txt   # Python dependencies
   ```
3. Update plugin.json description with new skill count
4. Update marketplace.json description with new skill count
5. Update README.md with skill documentation
6. Test with `claude skill new-skill`

### Skill File Format (SKILL.md)

```markdown
---
name: skill-name
description: Brief description of what the skill does
---

# Skill Title

Detailed documentation...

## Environment Setup
...

## Quick Start Scripts
...

## Core API Methods
...
```

### Updating the openalgo-python Plugin

When skills or features are added/removed, follow this checklist:

#### 1. Count all components accurately

```bash
# Count skills
ls -d plugins/openalgo-python/skills/*/ 2>/dev/null | wc -l
```

#### 2. Update ALL description strings with correct counts

The description appears in multiple places and must match everywhere:

- [ ] `plugins/openalgo-python/.claude-plugin/plugin.json` → `description` field
- [ ] `.claude-plugin/marketplace.json` → plugin `description` field
- [ ] `plugins/openalgo-python/README.md` → intro paragraph

Format: `"Includes X skill(s)."`

#### 3. Update version numbers

When adding new functionality, bump the version in:

- [ ] `plugins/openalgo-python/.claude-plugin/plugin.json` → `version`
- [ ] `.claude-plugin/marketplace.json` → plugin `version`

#### 4. Validate JSON files

```bash
cat .claude-plugin/marketplace.json | jq .
cat plugins/openalgo-python/.claude-plugin/plugin.json | jq .
```

## OpenAlgo SDK Reference

### Installation

```bash
pip install openalgo
```

### Initialization

```python
from openalgo import api

# REST API only
client = api(
    api_key='your_api_key',
    host='http://127.0.0.1:5000'
)

# With WebSocket streaming
client = api(
    api_key='your_api_key',
    host='http://127.0.0.1:5000',
    ws_url='ws://127.0.0.1:8765',
    verbose=True
)
```

### Symbol Format Standards

| Type | Format | Example |
|------|--------|---------|
| Equity | `SYMBOL` | `RELIANCE`, `INFY` |
| Future | `[SYMBOL][DDMMMYY]FUT` | `NIFTY30JAN25FUT` |
| Option | `[SYMBOL][DDMMMYY][STRIKE][CE/PE]` | `NIFTY30JAN2526000CE` |

### Exchange Codes

| Code | Description |
|------|-------------|
| `NSE` | NSE Equity |
| `BSE` | BSE Equity |
| `NFO` | NSE F&O |
| `BFO` | BSE F&O |
| `CDS` | NSE Currency |
| `BCD` | BSE Currency |
| `MCX` | MCX Commodity |
| `NSE_INDEX` | NSE Indices |
| `BSE_INDEX` | BSE Indices |

### Order Constants

| Category | Options |
|----------|---------|
| Product | `CNC`, `NRML`, `MIS` |
| Price Type | `MARKET`, `LIMIT`, `SL`, `SL-M` |
| Action | `BUY`, `SELL` |

### Options Offset System

| Offset | Meaning |
|--------|---------|
| `ATM` | At The Money |
| `ITM1`-`ITM10` | In The Money (1-10 strikes) |
| `OTM1`-`OTM10` | Out of The Money (1-10 strikes) |

## Testing Changes

### Test Locally

1. Install the marketplace locally:
   ```bash
   claude /plugin marketplace add /path/to/openalgo_marketplace
   ```

2. Install the plugin:
   ```bash
   claude /plugin install openalgo-python
   ```

3. Test the skills:
   ```bash
   claude "place a market order to buy 1 share of RELIANCE"
   claude "create an iron condor on NIFTY expiring 30JAN25"
   ```

### Use Analyzer Mode (Paper Trading)

Always test strategies in analyzer mode first:

```python
# Enable paper trading
client.analyzertoggle(mode=True)

# Place test orders (won't execute)
response = client.placeorder(...)

# Disable paper trading for live
client.analyzertoggle(mode=False)
```

## Common Patterns

### Building Trading Strategies

1. **Trend Following**: Use moving averages from historical data
2. **Mean Reversion**: Monitor deviations from VWAP
3. **Options Selling**: Weekly strangle/iron condor for theta decay
4. **Event Trading**: Straddle before earnings/announcements

### Building Dashboards

1. Use Streamlit for quick prototypes
2. WebSocket streaming for real-time data
3. Plotly for interactive charts
4. Portfolio tracking with positionbook/holdings

### Error Handling

Always check response status:

```python
response = client.placeorder(...)

if response.get('status') == 'success':
    print(f"Order placed: {response['orderid']}")
else:
    print(f"Error: {response}")
```

## Resources

- [OpenAlgo Documentation](https://docs.openalgo.in)
- [OpenAlgo GitHub](https://github.com/marketcalls/openalgo)
- [Claude Code Plugin Documentation](https://docs.claude.com/en/docs/claude-code/plugins)
- [Plugin Marketplace Documentation](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)

## Key Learnings

_This section captures important learnings as we work on this repository._

### 2025-01-04: Initial marketplace structure created

Created the OpenAlgo Claude Code marketplace with 5 comprehensive skills:

1. **trading-core**: Order management, smart orders, basket orders, split orders
2. **options-trading**: Options strategies, multi-leg orders, Greeks calculation
3. **market-data**: Quotes, historical data, WebSocket streaming, option chains
4. **visualization**: Candlestick charts, payoff diagrams, Streamlit dashboards
5. **portfolio**: Funds, positions, holdings, margin calculation

**Learning:** The OpenAlgo SDK provides a unified API across 25+ Indian brokers. The plugin should emphasize the standardized symbol format and offset system for options trading, as these are the key differentiators that simplify multi-broker development.
