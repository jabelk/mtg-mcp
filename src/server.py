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

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from tools.card_lookup import lookup as mtg_lookup, CardLookupError

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

mcp = FastMCP("mcp-mtg-week1")


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


@mcp.tool()
async def health_check() -> dict:
    """Return server version, current time (UTC), and learning streak days."""
    now = datetime.now(timezone.utc).isoformat()
    days = _load_streak()
    # Nudge the counter once per run (simple Day-1 behavior)
    _save_streak(days + 1)
    payload = {"version": APP_VERSION, "now": now, "streak_days": days + 1}
    logger.info("health.check -> %s", payload)
    return payload


@mcp.tool()
async def mtg_card_lookup(name: str) -> dict:
    """Fuzzy-lookup a Magic card by name using Scryfall API."""
    start = datetime.now(timezone.utc)
    try:
        result = await mtg_lookup(name=name)
        logger.info("mtg.card_lookup name=%r -> ok", name)
        return result
    except CardLookupError as e:
        logger.warning("mtg.card_lookup name=%r -> %s: %s", name, e.error_type, e)
        return {
            "error": e.error_type,
            "message": str(e),
            "query": e.query
        }
    finally:
        end = datetime.now(timezone.utc)
        elapsed_ms = int((end - start).total_seconds() * 1000)
        logger.info("mtg.card_lookup elapsed_ms=%d", elapsed_ms)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
