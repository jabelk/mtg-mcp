# Lessons Learned: Spec-Driven Development

> Notes from building the Scryfall integration feature

---

## What We Did

1. **Wrote a spec first** (`01-spec-scryfall-integration.md`)
   - Defined WHAT we wanted, not HOW
   - Listed success criteria that are testable
   - Identified unknowns upfront (clarification questions)

2. **Resolved ambiguities before coding**
   - Double-faced cards: front face only
   - Error handling: consistent error types
   - Field mapping: keep existing 6 fields

3. **Wrote an implementation plan** (`02-plan-scryfall-integration.md`)
   - Made technical decisions explicit (httpx, field mapping)
   - Created error handling matrix
   - Listed test cases before writing code

4. **Implemented and tested**
   - Code matched the plan
   - All test cases from plan were verified

---

## Key Spec-Driven Principles

### 1. WHAT vs HOW

| Spec (WHAT) | Plan (HOW) |
|-------------|------------|
| "Returns card data" | "Use httpx for HTTP calls" |
| "Handles not-found gracefully" | "Catch 404, return error dict" |
| "Reasonable performance" | "10 second timeout" |

### 2. Testable Success Criteria

Bad: "The API should be fast"
Good: "Responses return within 3 seconds"

Bad: "Handle errors well"
Good: "Invalid card names return `{error: 'not_found', ...}`"

### 3. Scope Control

The "Out of Scope" section prevented us from adding:
- Caching (not needed for v1)
- Rate limiting (Scryfall handles this)
- Advanced search (would take 3x longer)

Without explicit scope, it's easy to keep adding "just one more thing."

### 4. Unknowns Are Okay

We started with 3 open questions. That's fine! The key is:
- Mark them clearly
- Resolve them before coding
- Document the decisions

---

## Side Quest: Python Environment

We also fixed a broken Python setup:

**Problem:**
- macOS system Python is 3.9.6
- `mcp` library requires 3.10+
- pyenv was configured but broken (incomplete installation)

**Solution:**
1. Cleaned up partial pyenv installation
2. Fixed `.zshrc` (commented broken lines, fixed Homebrew paths)
3. Installed `uv` for modern Python management

**Key `uv` commands learned:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv with specific Python (downloads if needed!)
uv venv --python 3.11

# Install dependencies
uv pip install -r requirements.txt
```

---

## Testing the MCP Server

### With Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mtg": {
      "command": "/Users/jabelk/dev/projects/ai/mtg-mcp/.venv/bin/python",
      "args": ["/Users/jabelk/dev/projects/ai/mtg-mcp/src/server.py"]
    }
  }
}
```

Then restart Claude Desktop and try: "Look up the Magic card Black Lotus"

### With Cursor

Add to Cursor settings (MCP section) or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mtg": {
      "command": "/Users/jabelk/dev/projects/ai/mtg-mcp/.venv/bin/python",
      "args": ["/Users/jabelk/dev/projects/ai/mtg-mcp/src/server.py"]
    }
  }
}
```

---

## Files Created/Modified

```
mtg-mcp/
├── docs/
│   ├── 01-spec-scryfall-integration.md    # NEW - Feature spec
│   ├── 02-plan-scryfall-integration.md    # NEW - Implementation plan
│   └── 03-lessons-learned.md              # NEW - This file
├── src/
│   ├── server.py                          # MODIFIED - Updated imports/error handling
│   └── tools/
│       └── card_lookup.py                 # MODIFIED - Real Scryfall API
└── requirements.txt                       # MODIFIED - Added httpx
```

---

## What's Next?

Ideas for future iterations (all out of scope for now):
- [ ] Add caching to reduce API calls
- [ ] Support double-faced card back faces
- [ ] Add `mtg.search` tool for advanced queries
- [ ] Add `mtg.random` tool for random card
- [ ] Rate limiting / retry logic
