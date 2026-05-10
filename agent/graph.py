"""
LangGraph Pipeline — Lumière Store Builder Agent
=================================================
Defines the StateGraph with 4 nodes:
  research → strategy → content → shopify
"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.research_node import research_node
from agent.nodes.strategy_node import strategy_node
from agent.nodes.content_node import content_node
from agent.nodes.shopify_node import shopify_node


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("research", research_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("content",  content_node)
    graph.add_node("shopify",  shopify_node)

    # Define edges — sequential pipeline
    graph.set_entry_point("research")
    graph.add_edge("research", "strategy")
    graph.add_edge("strategy", "content")
    graph.add_edge("content",  "shopify")
    graph.add_edge("shopify",  END)

    return graph.compile()
