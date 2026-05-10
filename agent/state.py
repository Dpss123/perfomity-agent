"""
Shared state object passed between all LangGraph nodes.
Each node reads from state and writes its output back.
"""

from typing import TypedDict, Optional


class AgentState(TypedDict):
    # Input
    brief: str

    # Node outputs (filled in order)
    research:     Optional[dict]
    strategy:     Optional[dict]
    store_assets: Optional[dict]
    shopify:      Optional[dict]

    # Errors
    errors: list[str]
