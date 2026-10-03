import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from day30.agent import build_order_graph
from day30.menu import MENU
from day30.state import OrderState


def interactive_chat():
    print("\n" + "="*60)
    print("  WELCOME TO LANGGRAPH RESTAURANT ORDER SYSTEM  ")
    print("="*60)
    print("Our Current Menu & Availability:")
    for dish, qty in MENU.items():
        print(f"  * {dish.title()}: {qty} available")
    print("-" * 60)
    print("Type your message (or 'exit' / 'quit' to stop).\n")

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
        "mock_cook_success": None,   # Live mode: uses 60/40 probability
        "mock_serve_success": None
    }

    turn = 1
    while True:
        try:
            user_text = input(f"\n[Turn {turn}] You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if not user_text:
            continue
        if user_text.lower() in ["exit", "quit", "q"]:
            print("Thank you for visiting! Goodbye!")
            break

        state["user_input"] = user_text
        state = graph.invoke(state)

        # Print latest AI responses
        ai_messages = [m.content for m in state["messages"] if m.type == "ai"]
        if ai_messages:
            print(f"\nAgent: {ai_messages[-1]}")

        print(f"   [Status: {state.get('status')} | Retries Left -> Order: {state.get('order_retry_attempts')}, Cook: {state.get('cook_retry_attempts')}, Serve: {state.get('serve_retry_attempts')}]")

        if state.get("final_result") in ["COMPLETED", "FAILED"]:
            print(f"\nSession ended with outcome: {state.get('final_result')}")
            break

        turn += 1


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ["--test", "-t", "test"]:
        from day30.test_runner import run_test_case_1, run_test_case_2, run_test_case_3
        print("Running automated test scenarios...")
        run_test_case_1()
        run_test_case_2()
        run_test_case_3()
    else:
        interactive_chat()


if __name__ == "__main__":
    main()
