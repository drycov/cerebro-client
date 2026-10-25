# cerebro-client

Shared **Cerebro API** client for the ops platform. No product DB, no SQLite/Postgres.

Profile map: https://github.com/drycov#-ops-platform-ecosystem

## Install

```bash
pip install "cerebro-client @ https://github.com/drycov/cerebro-client/archive/main.zip"
```

## Usage

```python
from cerebro_client import CerebroClient, CerebroConfig, normalize_networks, channel_in_networks

config = CerebroConfig(base_url="https://cerebro.example", username="u", password="p")
client = CerebroClient(config)
await client.authenticate()
payload = await client.search_channels(offset=0, limit=100)
```

Product repos (`cms`, `equipment-bot`) own **upsert into their inventory**. This package owns HTTP + channel parsing helpers only.
