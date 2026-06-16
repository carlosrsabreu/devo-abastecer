# ⛽️ Devo Abastecer (_beta_)

> [!IMPORTANT]
>
> [![⛽️ Update Gas Prices from DRETT](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/update_gas_prices.yml/badge.svg?branch=main)](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/update_gas_prices.yml) [![📈 Publish History Plot](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/plot_history.yml/badge.svg)](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/plot_history.yml) [![💅 Format Codebase](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/format_codebase.yml/badge.svg?branch=main)](https://github.com/carlosrsabreu/devo-abastecer/actions/workflows/format_codebase.yml)

🇵🇹 Informação acessível com os preços dos combustíveis na Madeira, publicada semanalmente no Twitter recorrendo a um bot.<br> 🇬🇧 Up-to-date fuel prices in Madeira, conveniently updated weekly on Twitter via our automated bot.

## Fuel price history

![Gas History](history/gas_history.png)

## Functionality Overview

This project automates the end-to-end lifecycle of fuel price monitoring in Madeira. The system is designed for reliability, using GitHub Actions as a serverless orchestrator to handle extraction, archival, and multi-channel publication.

### Workflow

```mermaid
sequenceDiagram
    autonumber
    participant 🤖 GitHub Action
    participant 🐍 Orchestrator (update_gas_prices.py)
    participant 📄 JORAM (PDF Archive)
    participant 🗄️ Database (CSV/JSON)
    participant 📢 Social Media (X/BSky/FB)
    participant 📈 Visualization (plot_history.py)

    Note over 🤖 GitHub Action: 📅 Weekly update trigger
    🤖 GitHub Action ->> 🐍 Orchestrator (update_gas_prices.py): 🚀 Start update process
    🐍 Orchestrator (update_gas_prices.py) ->> 📄 JORAM (PDF Archive): 🔍 Extract latest fuel prices
    📄 JORAM (PDF Archive) -->> 🐍 Orchestrator (update_gas_prices.py): 🏷️ New price data

    alt 🆕 New Prices Found
        🐍 Orchestrator (update_gas_prices.py) ->> 🗄️ Database (CSV/JSON): 🏛️ Archive record (add_history.py)
        🐍 Orchestrator (update_gas_prices.py) ->> 📢 Social Media (X/BSky/FB): 📬 Post to platforms
        🐍 Orchestrator (update_gas_prices.py) ->> 🤖 GitHub Action: 💾 Commit updated history files
    else 💤 Data already exists
        🐍 Orchestrator (update_gas_prices.py) -->> 🤖 GitHub Action: 🔚 End workflow
    end

    Note over 🤖 GitHub Action: 📈 Monthly visualization trigger
    🤖 GitHub Action ->> 📈 Visualization (plot_history.py): 🎨 Generate trend chart
    📈 Visualization (plot_history.py) ->> 🗄️ Database (CSV/JSON): 📖 Read historical data
    📈 Visualization (plot_history.py) ->> 📈 Visualization (plot_history.py): 🖼️ Render gas_history.png
    📈 Visualization (plot_history.py) ->> 🤖 GitHub Action: 📎 Commit updated plot
```

## Pairing: GetXAPI MCP server (optional alternative backend)

Users who already adopt this project sometimes ask about routing read-heavy operations (tweet search, profile lookup, follower lists) to a different X/Twitter backend during testing or for specific workflows. The [GetXAPI MCP server](https://github.com/getxapi/getxapi-mcp) (MIT licensed, open source) implements the same read tools and can be paired with this project without changing existing behavior.

Two integration patterns:

1. **Side-by-side in your AI client.** Keep this project for its primary workflow and add the GetXAPI MCP server when you need a different backend for read operations. Each tool name maps to whichever backend the user has configured.

2. **Code-level toggle.** For a worked reference of an optional alternative backend behind a single env variable, see the [pattern merged into GenAIwithMS/twitter-mcp](https://github.com/GenAIwithMS/twitter-mcp/pull/3).

Tool compatibility (subset that pairs cleanly with this project's read path):

- `search_tweets`
- `get_user_profile`
- `get_user_followers`
- `get_tweet_by_id`

Repository: https://github.com/getxapi/getxapi-mcp

This pairing is fully optional. No behavior change for existing users of this project.

