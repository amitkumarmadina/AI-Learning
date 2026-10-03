from typing import Annotated, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class OrderState(TypedDict):
    # Chat message history
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Order details
    dish_name: str
    required_quantity: int
    available_quantity: str  # Kept as string as specified in prompt
    
    # Status across nodes
    # e.g.: UNRELATED, ORDER_RECEIVED, CONFIRMED, PARTIAL, NOT_AVAILABLE,
    #       READY, COOK_FAILED, SERVE_FAILED, COMPLETED, APOLOGY
    status: str
    
    # Retry counters
    order_retry_attempts: int   # Starts at 3
    cook_retry_attempts: int    # Starts at 2
    serve_retry_attempts: int   # Starts at 2
    
    # Final outcome
    final_result: str           # "COMPLETED" or "FAILED" or "PENDING"
    
    # Current user input string for turn processing
    user_input: str
    
    # Deterministic mocking controls for testing
    mock_cook_success: Optional[bool]
    mock_serve_success: Optional[bool]
