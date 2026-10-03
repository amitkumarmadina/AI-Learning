import random
from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph

from day30.menu import MENU
from day30.state import OrderState
from day30.llm import parse_order_with_llm


def llm_node(state: OrderState) -> dict:
    """Processes user input, extracts dish/quantity, or rejects unrelated queries."""
    user_input = state.get("user_input", "")
    current_dish = state.get("dish_name", "")
    avail_qty = state.get("available_quantity", "")

    # Add human message to history
    new_messages = [HumanMessage(content=user_input)]

    extraction = parse_order_with_llm(user_input, current_dish, avail_qty)

    if not extraction.is_food_related:
        msg = extraction.unrelated_response or "I am an AI for food ordering and not a general purpose LLM."
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "status": "UNRELATED"
        }

    # If user confirmed partial order
    if extraction.is_confirming_partial:
        confirmed_qty = int(avail_qty) if avail_qty.isdigit() else 1
        msg = f"Proceeding with your confirmed order of {confirmed_qty} {current_dish}."
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "required_quantity": confirmed_qty,
            "status": "CONFIRMED"
        }

    # New food order
    dish = (extraction.dish_name or "").lower().strip()
    qty = extraction.quantity or 1
    msg = f"Received order for {qty} {dish}. Verifying with kitchen menu..."
    new_messages.append(AIMessage(content=msg))

    return {
        "messages": new_messages,
        "dish_name": dish,
        "required_quantity": qty,
        "status": "ORDER_RECEIVED"
    }


def order_confirm_node(state: OrderState) -> dict:
    """Checks the menu and decides if full, partial, or not available."""
    dish = state.get("dish_name", "").lower().strip()
    req_qty = state.get("required_quantity", 0)
    current_retries = state.get("order_retry_attempts", 3)

    new_messages = []
    
    if dish not in MENU or MENU[dish] <= 0:
        avail_str = "0"
        new_retries = max(0, current_retries - 1)
        status = "NOT_AVAILABLE"
        msg = (
            f"Sorry, '{dish}' is not available in our menu (0 available). "
            f"Remaining order retry attempts: {new_retries}."
        )
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "available_quantity": avail_str,
            "status": status,
            "order_retry_attempts": new_retries
        }

    avail_int = MENU[dish]
    avail_str = str(avail_int)

    if req_qty > avail_int:
        new_retries = max(0, current_retries - 1)
        status = "PARTIAL"
        msg = (
            f"We only have {avail_str} {dish} available (you requested {req_qty}). "
            f"Would you like to proceed with {avail_str} {dish} or place a different order? "
            f"Remaining order retry attempts: {new_retries}."
        )
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "available_quantity": avail_str,
            "status": status,
            "order_retry_attempts": new_retries
        }

    # Full order available
    status = "CONFIRMED"
    msg = f"Order confirmed: {req_qty} {dish} is fully available. Sending to cook!"
    new_messages.append(AIMessage(content=msg))
    return {
        "messages": new_messages,
        "available_quantity": avail_str,
        "status": status
    }


def cook_node(state: OrderState) -> dict:
    """Cooks the dish. 60% chance success, 40% failure unless mocked."""
    dish = state.get("dish_name", "dish")
    mock_success = state.get("mock_cook_success")

    if mock_success is not None:
        success = mock_success
    else:
        # 60% chance of success (random() < 0.6)
        success = random.random() < 0.60

    new_messages = []
    current_retries = state.get("cook_retry_attempts", 2)

    if success:
        status = "READY"
        msg = f"Cooking successful! Your {dish} is READY."
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "status": status
        }
    else:
        new_retries = max(0, current_retries - 1)
        if new_retries > 0:
            status = "COOK_RETRY"
            msg = f"Cooking failed for {dish}. Retrying cook... ({new_retries} cook attempts remaining)."
        else:
            status = "COOK_FAILED_EXHAUSTED"
            msg = f"Cooking failed for {dish} and all cook retry attempts are exhausted."
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "status": status,
            "cook_retry_attempts": new_retries
        }


def serve_node(state: OrderState) -> dict:
    """Serves the dish. Pass or fail with retry attempts."""
    mock_success = state.get("mock_serve_success")
    if mock_success is not None:
        success = mock_success
    else:
        success = random.random() < 0.70

    new_messages = []
    current_serve_retries = state.get("serve_retry_attempts", 2)
    cook_retries = state.get("cook_retry_attempts", 2)

    if success:
        status = "SERVE_SUCCESS"
        msg = "Dish served successfully!"
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "status": status
        }
    else:
        new_serve_retries = max(0, current_serve_retries - 1)
        # Check if serve retry can re-invoke cook or if exhausted
        if new_serve_retries <= 0 or cook_retries <= 0:
            status = "SERVE_FAILED_EXHAUSTED"
            msg = "Serving failed and retry limits reached."
        else:
            status = "SERVE_FAILED_RETRY_COOK"
            msg = f"Serving failed! Calling cook again to prepare fresh dish ({new_serve_retries} serve retries left)."
        
        new_messages.append(AIMessage(content=msg))
        return {
            "messages": new_messages,
            "status": status,
            "serve_retry_attempts": new_serve_retries
        }


def complete_order_node(state: OrderState) -> dict:
    """Issues final order complete message."""
    new_messages = [AIMessage(content="Your order is complete! Thank you for dining with us.")]
    return {
        "messages": new_messages,
        "status": "COMPLETED",
        "final_result": "COMPLETED"
    }


def apology_node(state: OrderState) -> dict:
    """Issues apology when retries are exhausted or order cannot be completed."""
    new_messages = [AIMessage(content="We sincerely apologize, but we are unable to complete your order. Thank you for your patience.")]
    return {
        "messages": new_messages,
        "status": "FAILED",
        "final_result": "FAILED"
    }


# Routing Functions
def route_after_llm(state: OrderState) -> Literal["order_confirm", "END"]:
    status = state.get("status")
    if status == "CONFIRMED":
        # User confirmed partial order, go straight to cook
        return "cook"
    elif status == "ORDER_RECEIVED":
        return "order_confirm"
    # Unrelated queries stay in turn / end current step
    return "END"


def route_after_order_confirm(state: OrderState) -> Literal["cook", "apology", "END"]:
    status = state.get("status")
    order_retries = state.get("order_retry_attempts", 0)

    if status == "CONFIRMED":
        return "cook"
    elif order_retries <= 0:
        return "apology"
    else:
        # Prompt user to retry or confirm partial
        return "END"


def route_after_cook(state: OrderState) -> Literal["serve", "cook", "apology"]:
    status = state.get("status")
    if status == "READY":
        return "serve"
    elif status == "COOK_RETRY":
        return "cook"
    else:
        return "apology"


def route_after_serve(state: OrderState) -> Literal["complete_order", "cook", "apology"]:
    status = state.get("status")
    if status == "SERVE_SUCCESS":
        return "complete_order"
    elif status == "SERVE_FAILED_RETRY_COOK":
        return "cook"
    else:
        return "apology"


def build_order_graph():
    """Builds and compiles the restaurant order management LangGraph."""
    workflow = StateGraph(OrderState)

    # Add all nodes
    workflow.add_node("llm", llm_node)
    workflow.add_node("order_confirm", order_confirm_node)
    workflow.add_node("cook", cook_node)
    workflow.add_node("serve", serve_node)
    workflow.add_node("complete_order", complete_order_node)
    workflow.add_node("apology", apology_node)

    # Set entry point
    workflow.set_entry_point("llm")

    # Add conditional edges
    workflow.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "order_confirm": "order_confirm",
            "cook": "cook",
            "END": END
        }
    )

    workflow.add_conditional_edges(
        "order_confirm",
        route_after_order_confirm,
        {
            "cook": "cook",
            "apology": "apology",
            "END": END
        }
    )

    workflow.add_conditional_edges(
        "cook",
        route_after_cook,
        {
            "serve": "serve",
            "cook": "cook",
            "apology": "apology"
        }
    )

    workflow.add_conditional_edges(
        "serve",
        route_after_serve,
        {
            "complete_order": "complete_order",
            "cook": "cook",
            "apology": "apology"
        }
    )

    workflow.add_edge("complete_order", END)
    workflow.add_edge("apology", END)

    return workflow.compile()
