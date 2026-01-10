"""
Card lookup tool - queries Scryfall API for Magic: The Gathering cards.

Day-2 implementation: Real Scryfall API integration.
See docs/01-spec-scryfall-integration.md for requirements.
See docs/02-plan-scryfall-integration.md for implementation details.
"""

import httpx
from dataclasses import dataclass
from typing import Literal


SCRYFALL_API = "https://api.scryfall.com/cards/named"


@dataclass
class CardLookupError(Exception):
    """Error during card lookup."""
    error_type: Literal["not_found", "service_unavailable"]
    query: str
    message: str

    def __str__(self) -> str:
        return self.message


async def lookup(name: str) -> dict:
    """
    Look up a Magic card by name using Scryfall's fuzzy search.

    Args:
        name: Card name (fuzzy matching supported)

    Returns:
        dict with keys: name, type_line, oracle_text, mana_value, image_small, rulings_uri

    Raises:
        CardLookupError: If card not found or service unavailable
    """
    if not isinstance(name, str) or not name.strip():
        raise CardLookupError(
            error_type="not_found",
            query=str(name),
            message="Card name cannot be empty"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                SCRYFALL_API,
                params={"fuzzy": name.strip()}
            )
    except httpx.RequestError as e:
        # Network error, timeout, etc.
        raise CardLookupError(
            error_type="service_unavailable",
            query=name,
            message=f"Could not reach Scryfall API: {e}"
        )

    # Handle HTTP errors
    if response.status_code == 404:
        raise CardLookupError(
            error_type="not_found",
            query=name,
            message="Card not found. Check spelling or try a different name."
        )

    if response.status_code >= 400:
        raise CardLookupError(
            error_type="service_unavailable",
            query=name,
            message=f"Scryfall API error: {response.status_code}"
        )

    card = response.json()

    # Handle double-faced cards (werewolves, MDFCs, etc.)
    # These have card_faces array instead of top-level fields
    # Decision: Use front face only (see docs/01-spec-scryfall-integration.md)
    if "card_faces" in card:
        face = card["card_faces"][0]
        oracle_text = face.get("oracle_text", "")
        type_line = face.get("type_line", card.get("type_line", ""))
        # Double-faced cards have image_uris on each face
        image_small = face.get("image_uris", {}).get("small", "")
    else:
        oracle_text = card.get("oracle_text", "")
        type_line = card.get("type_line", "")
        image_small = card.get("image_uris", {}).get("small", "")

    return {
        "name": card.get("name", ""),
        "type_line": type_line,
        "oracle_text": oracle_text,
        "mana_value": card.get("cmc", 0),
        "image_small": image_small,
        "rulings_uri": card.get("rulings_uri", "")
    }
