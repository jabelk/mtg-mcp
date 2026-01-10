# README.md

## Week 1 — Hobby Track: `mtg.card_lookup`

This is a minimal **MCP** server in Python that exposes two tools:

- `health.check` — returns version, current time, and a simple learning streak counter stored in `streak.json`.
- `mtg.card_lookup` — **Day 1** returns a fake response (proves wiring). On **Day 2**, switch to Scryfall API.

### Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install mcp uvloop (optional on Windows)

# Run the server over stdio (default)
python src/server.py
```

> If your client expects a command, point it at `python src/server.py`.

### Files
```
/mcp-mtg-week1
  ├─ src/
  │   ├─ server.py            # MCP server entry point
  │   └─ tools/
  │       ├─ __init__.py
  │       └─ card_lookup.py   # tool implementation (fake → real)
  ├─ logs/
  └─ streak.json              # created on first run
```

### Day 2 switch (Scryfall)
- Replace the fake result in `card_lookup.lookup()` with a real HTTP call to Scryfall's named endpoint:
  - `https://api.scryfall.com/cards/named?fuzzy=<name>`
- Keep the same return schema.

---

# src/server.py

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

try:
    import uvloop  # type: ignore
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except Exception:
    pass

from mcp.server import Server
from mcp.types import TextContent

from tools.card_lookup import lookup as mtg_lookup, FakeCardLookupError

APP_VERSION = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
STREAK_FILE = BASE_DIR / "streak.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "week1.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp-mtg-week1")

server = Server("mcp-mtg-week1")


def _load_streak() -> int:
    if STREAK_FILE.exists():
        try:
            data = json.loads(STREAK_FILE.read_text())
            return int(data.get("streak_days", 0))
        except Exception:
            return 0
    return 0


def _save_streak(days: int) -> None:
    STREAK_FILE.write_text(json.dumps({"streak_days": days}, indent=2))


@server.tool()
async def health_check() -> dict:
    """Return server version, current time (UTC), and learning streak days."""
    now = datetime.now(timezone.utc).isoformat()
    days = _load_streak()
    # Nudge the counter once per run (simple Day-1 behavior)
    _save_streak(days + 1)
    payload = {"version": APP_VERSION, "now": now, "streak_days": days + 1}
    logger.info("health.check -> %s", payload)
    return payload


@server.tool()
async def mtg_card_lookup(name: str) -> dict:
    """Fuzzy-lookup a Magic card by name. Day-1: fake response to prove wiring."""
    start = datetime.now(timezone.utc)
    try:
        result = await mtg_lookup(name=name)
        logger.info("mtg.card_lookup name=%r -> ok", name)
        return result
    except FakeCardLookupError as e:
        logger.warning("mtg.card_lookup name=%r -> not_found: %s", name, e)
        return {
            "error": "not_found",
            "message": str(e),
            "suggestion": "Try a different name or check spelling."
        }
    finally:
        end = datetime.now(timezone.utc)
        elapsed_ms = int((end - start).total_seconds() * 1000)
        logger.info("mtg.card_lookup elapsed_ms=%d", elapsed_ms)


async def amain() -> None:
    # Default transport: stdio
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(amain())


# src/tools/__init__.py

# Intentionally empty; makes tools a package.


# src/tools/card_lookup.py

import asyncio
from dataclasses import dataclass


@dataclass
class FakeCardLookupError(Exception):
    query: str
    def __str__(self) -> str:
        return f"No fake match for query: {self.query}"


async def lookup(name: str) -> dict:
    """
    Day-1 fake implementation.
    - Accepts any name containing 'atraxa' (case-insensitive) and returns a fixed object.
    - Otherwise raises FakeCardLookupError so the server can return a friendly error.

    Day-2: replace this with a real HTTP call to Scryfall's `named?fuzzy=...` endpoint.
    """
    if not isinstance(name, str) or not name.strip():
        raise FakeCardLookupError(query=name)

    await asyncio.sleep(0.05)  # small delay to exercise logging

    if "atraxa" in name.lower():
        return {
            "name": "Atraxa, Grand Unifier",
            "type_line": "Legendary Creature — Phyrexian Angel",
            "oracle_text": (
                "Flying, vigilance, deathtouch, lifelink — When Atraxa, Grand Unifier "
                "enters the battlefield, reveal the top ten cards of your library. For each "
                "card type, you may put a card of that type from among them into your hand."
            ),
            "mana_value": 7,
            "image_small": "https://cards.scryfall.io/small/front/5/9/59....jpg",
            "rulings_uri": "https://api.scryfall.com/cards/xxxx/rulings"
        }

    raise FakeCardLookupError(query=name)
