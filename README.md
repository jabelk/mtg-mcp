# mtg-mcp

A minimal Model Context Protocol server in Python that exposes Magic: The Gathering card lookups (and a health check) to any MCP-compatible LLM client.

> **Companion to the blog post:** [Model Context Protocol Tutorial: Build Your First Server](https://sierracodeco.com/blog/mcp-tutorial-build-your-first-server/)
>
> The post walks through this repo end-to-end: what MCP is, how the two tools work, the Day-1-fake → Day-2-real Scryfall progression, and how to wire it up to Claude Desktop.

---

## What it does

Two tools, exposed by one Python process over MCP stdio:

- **`health.check`** — returns the server version, current UTC time, and a simple "learning streak" counter persisted to `streak.json`. The simplest possible tool. No external dependencies.
- **`mtg.card_lookup`** — takes a card name and returns the card's type line, oracle text, mana value, and image URL. Calls the [Scryfall fuzzy-named endpoint](https://scryfall.com/docs/api/cards/named).

The contract on `mtg.card_lookup` was designed first; the implementation went through a deliberate fake → real progression. See [`docs/01-spec-scryfall-integration.md`](./docs/01-spec-scryfall-integration.md) for the full spec-driven write-up.

---

## Quick start

```bash
git clone https://github.com/jabelk/mtg-mcp.git
cd mtg-mcp
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python src/server.py
```

The server runs over stdio by default and will block waiting for an MCP client to connect. That is correct — point your client at the command `python src/server.py` (with absolute paths) to start calling the tools.

Python 3.11 or newer is recommended. `uvloop` is optional and skipped automatically on Windows.

---

## Wiring it to Claude Desktop

Add an entry to your `claude_desktop_config.json`:

| OS | Path |
|----|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "mtg": {
      "command": "/absolute/path/to/mtg-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/mtg-mcp/src/server.py"]
    }
  }
}
```

Use absolute paths for both the interpreter and the script; Claude Desktop launches the server itself, so a `~` or relative path will not resolve. Quit Claude Desktop fully and reopen after saving.

---

## Repository layout

```text
mtg-mcp/
├── src/
│   ├── server.py            # MCP server entry point — registers the two tools
│   └── tools/
│       ├── __init__.py
│       └── card_lookup.py   # Scryfall integration (Day-2 real implementation)
├── docs/
│   ├── 01-spec-scryfall-integration.md   # spec for the Day-1 → Day-2 swap
│   ├── 02-plan-scryfall-integration.md   # implementation plan
│   └── 03-lessons-learned.md             # retrospective
├── requirements.txt
├── LICENSE
└── README.md
```

The `logs/` directory and `streak.json` are created at runtime.

---

## Day 1 → Day 2: how this repo evolved

The first version of `mtg.card_lookup` returned a hardcoded fake response (matching only the name `Atraxa`). The point of starting with a fake was to prove the wiring — that the MCP client could find the tool, call it, and parse the response shape — before debugging any HTTP layer.

Once the wiring was confirmed, the same function was swapped to call Scryfall. The function signature, the input schema, and the return shape did not change. The contract held. That progression is the whole point of the companion blog post; the spec for the swap lives at [`docs/01-spec-scryfall-integration.md`](./docs/01-spec-scryfall-integration.md), the plan at [`docs/02-plan-scryfall-integration.md`](./docs/02-plan-scryfall-integration.md), and the retrospective at [`docs/03-lessons-learned.md`](./docs/03-lessons-learned.md).

---

## Dependencies

```text
mcp        # the official MCP Python SDK
uvloop     # faster event loop (skipped on Windows)
httpx      # HTTP client for the Scryfall call
```

Versions are not pinned in this repo. If you need reproducibility, pin against your install.

---

## License

[MIT](./LICENSE) — Copyright (c) 2026 Jason Belk.

---

## Further reading

- The companion post: [Model Context Protocol Tutorial: Build Your First Server](https://sierracodeco.com/blog/mcp-tutorial-build-your-first-server/)
- Official MCP docs: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- Anthropic's MCP launch announcement: [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol)
- Scryfall API: [scryfall.com/docs/api](https://scryfall.com/docs/api)
