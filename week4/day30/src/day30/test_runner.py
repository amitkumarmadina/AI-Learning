"""
Deterministic Test Runner for Restaurant Order Management LangGraph Agent
Tests the 3 specific scenarios specified in prompt.md.
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from day30.agent import build_order_graph
from day30.state import OrderState


def print_turn_log(turn_num: int, user_input: str, state: OrderState):
    print(f"\n--- [Turn {turn_num}] User: '{user_input}' ---")
    latest_ai_msg = [m.content for m in state["messages"] if m.type == "ai"]
    if latest_ai_msg:
        print(f"Agent Response:\n  {latest_ai_msg[-1]}")
    print(f"State Snapshot -> Status: {state.get('status')} | Dish: {state.get('dish_name')} | Qty: {state.get('required_quantity')} | Avail: {state.get('available_quantity')}")
    print(f"Counters       -> Order Retries: {state.get('order_retry_attempts')} | Cook Retries: {state.get('cook_retry_attempts')} | Serve Retries: {state.get('serve_retry_attempts')}")
    print(f"Final Result   -> {state.get('final_result')}")


def run_test_case_1():
    print("\n" + "="*80)
    print("TEST CASE 1: Unrelated questions (x2) -> Partial order -> Fully available dish -> Cooking fail & retry fail -> Apology & END")
    print("="*80)

    graph = build_order_graph()
    state: OrderState = {
        "messages": [],
        "dish_name": "",
        "required_quantity": 0,
        "available_quantity": "",
        "status": "INIT",
        "order_retry_attempts": 3,
        "cook_retry_attempts": 2,
        "serve_retry_attempts": 2,
        "final_result": "PENDING",
        "user_input": "",
        "mock_cook_success": False,   # Deterministically fail cook to test retry & apology
        "mock_serve_success": True
    }

    # Step 1: Unrelated query 1
    state["user_input"] = "What is the capital of France?"
    state = graph.invoke(state)
    print_turn_log(1, state["user_input"], state)
    assert state["status"] == "UNRELATED", f"Expected UNRELATED, got {state['status']}"

    # Step 2: Unrelated query 2
    state["user_input"] = "Tell me a joke about computers"
    state = graph.invoke(state)
    print_turn_log(2, state["user_input"], state)
    assert state["status"] == "UNRELATED", f"Expected UNRELATED, got {state['status']}"

    # Step 3: Partial order (10 pasta, only 6 available)
    state["user_input"] = "I want 10 pasta"
    state = graph.invoke(state)
    print_turn_log(3, state["user_input"], state)
    assert state["status"] == "PARTIAL", f"Expected PARTIAL, got {state['status']}"
    assert state["available_quantity"] == "6", f"Expected available '6', got {state['available_quantity']}"
    assert state["order_retry_attempts"] == 2, f"Expected 2 retries, got {state['order_retry_attempts']}"

    # Step 4: Fully available order (5 burger, 10 available) with cook failure
    state["user_input"] = "Give me 5 burger instead"
    state = graph.invoke(state)
    print_turn_log(4, state["user_input"], state)

    assert state["final_result"] == "FAILED", f"Expected FAILED final_result, got {state.get('final_result')}"
    print("\n[PASS] TEST CASE 1 PASSED: Apology issued and reached END state after cook retries exhausted.")


def run_test_case_2():
    print("\n" + "="*80)
    print("TEST CASE 2: User orders 30 pizza repeatedly until retry attempts exhaust -> Fail & END")
    print("="*80)

    graph = build_order_graph()
    state: OrderState = {
        "messages": [],
        "dish_name": "",
        "required_quantity": 0,
        "available_quantity": "",
        "status": "INIT",
        "order_retry_attempts": 3,
        "cook_retry_attempts": 2,
        "serve_retry_attempts": 2,
        "final_result": "PENDING",
        "user_input": "",
        "mock_cook_success": True,
        "mock_serve_success": True
    }

    # Attempt 1: 30 pizza (only 5 in menu)
    state["user_input"] = "I want 30 pizza"
    state = graph.invoke(state)
    print_turn_log(1, state["user_input"], state)
    assert state["status"] == "PARTIAL"
    assert state["order_retry_attempts"] == 2

    # Attempt 2: 30 pizza again
    state["user_input"] = "No, I strictly want 30 pizza"
    state = graph.invoke(state)
    print_turn_log(2, state["user_input"], state)
    assert state["status"] == "PARTIAL"
    assert state["order_retry_attempts"] == 1

    # Attempt 3: 30 pizza again -> exhausts retries
    state["user_input"] = "Give me 30 pizza please"
    state = graph.invoke(state)
    print_turn_log(3, state["user_input"], state)
    assert state["order_retry_attempts"] == 0
    assert state["final_result"] == "FAILED", f"Expected FAILED, got {state['final_result']}"

    print("\n[PASS] TEST CASE 2 PASSED: 3 retry attempts exhausted and order failed with apology.")


def run_test_case_3():
    print("\n" + "="*80)
    print("TEST CASE 3: User orders 10 pasta -> Confirms available 6 -> Cook succeeds -> Serve succeeds -> Completed")
    print("="*80)

    graph = build_order_graph()
    state: OrderState = {
        "messages": [],
        "dish_name": "",
        "required_quantity": 0,
        "available_quantity": "",
        "status": "INIT",
        "order_retry_attempts": 3,
        "cook_retry_attempts": 2,
        "serve_retry_attempts": 2,
        "final_result": "PENDING",
        "user_input": "",
        "mock_cook_success": True,   # Deterministic success
        "mock_serve_success": True   # Deterministic success
    }

    # Step 1: Order 10 pasta (6 available in menu)
    state["user_input"] = "I would like 10 pasta please"
    state = graph.invoke(state)
    print_turn_log(1, state["user_input"], state)
    assert state["status"] == "PARTIAL"
    assert state["available_quantity"] == "6"

    # Step 2: User confirms accepting available 6 pasta
    state["user_input"] = "Yes, please proceed with the available 6 pasta"
    state = graph.invoke(state)
    print_turn_log(2, state["user_input"], state)

    assert state["status"] == "COMPLETED", f"Expected COMPLETED, got {state['status']}"
    assert state["final_result"] == "COMPLETED", f"Expected COMPLETED final_result, got {state['final_result']}"

    print("\n[PASS] TEST CASE 3 PASSED: Order was confirmed with available quantity, cooked, served, and completed successfully.")


if __name__ == "__main__":
    print("\n[START] RESTAURANT AGENT TEST SUITE...")
    run_test_case_1()
    run_test_case_2()
    run_test_case_3()
    print("\n" + "="*80)
    print("[ALL PASSED] ALL 3 TEST SCENARIOS PASSED SUCCESSFULLY!")
    print("="*80 + "\n")
