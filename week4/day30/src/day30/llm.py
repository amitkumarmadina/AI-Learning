import os
import json
import re
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class OrderExtraction(BaseModel):
    is_food_related: bool = Field(description="True if user is asking for food, ordering, or confirming food. False if completely unrelated.")
    is_confirming_partial: bool = Field(default=False, description="True if the user is saying yes/agreeing to accept the partial available quantity.")
    dish_name: Optional[str] = Field(default=None, description="The name of the food item ordered in lowercase, e.g. pasta, burger, pizza, chowmin.")
    quantity: Optional[int] = Field(default=None, description="The integer quantity of the dish requested.")
    unrelated_response: Optional[str] = Field(default=None, description="Message to user if query is unrelated to food ordering.")


def get_llm():
    """Initializes LLM based on environment variables."""
    google_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if google_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                api_key=google_key,
                temperature=0.0
            )
        except Exception:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                api_key=google_key,
                temperature=0.0
            )
            
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=0.0
        )
        
    return None


def parse_order_with_llm(user_input: str, state_dish: str = "", state_available_qty: str = "") -> OrderExtraction:
    """Parses user input using LLM or fallback deterministic extractor."""
    llm = get_llm()
    if llm:
        try:
            structured_llm = llm.with_structured_output(OrderExtraction)
            prompt = (
                f"You are a restaurant order intake AI. Analyze the following user input: '{user_input}'.\n"
                f"Current context: Previous dish='{state_dish}', Available quantity='{state_available_qty}'.\n\n"
                "Rules:\n"
                "1. If user input is unrelated to food ordering (e.g. general knowledge, chit-chat, weather, math, jokes), "
                "set is_food_related=False, and set unrelated_response='I am an AI for food ordering and not a general purpose LLM.'\n"
                "2. If user agrees/confirms taking the partial quantity (e.g. 'yes', 'ok', 'go ahead', 'confirm', 'take available'), "
                "set is_food_related=True, is_confirming_partial=True.\n"
                "3. If user is placing an order (e.g. '10 pasta', 'i want 2 burgers', 'give me 30 pizza'), "
                "set is_food_related=True, extract dish_name (normalized lowercase) and quantity (integer).\n"
            )
            result = structured_llm.invoke(prompt)
            if isinstance(result, OrderExtraction):
                return result
        except Exception as e:
            # Fall back to heuristic rule-based extraction
            pass

    # Heuristic / deterministic fallback parser (guarantees tests run reliably)
    lower = user_input.strip().lower()

    # Check for confirmation of partial order
    if lower in ["yes", "y", "ok", "okay", "confirm", "go ahead", "sure", "proceed"]:
        return OrderExtraction(
            is_food_related=True,
            is_confirming_partial=True,
            dish_name=state_dish or None,
            quantity=int(state_available_qty) if state_available_qty.isdigit() else 1
        )

    # Check known menu items or food words
    known_dishes = ["burger", "burgers", "pizza", "pizzas", "chowmin", "chowmein", "pasta", "pastas"]
    matched_dish = None
    for d in known_dishes:
        if d in lower:
            # normalize plural
            if d.endswith("s"):
                matched_dish = d[:-1]
            elif d == "chowmein":
                matched_dish = "chowmin"
            else:
                matched_dish = d
            break

    if not matched_dish and not any(w in lower for w in ["order", "food", "dish", "eat"]):
        return OrderExtraction(
            is_food_related=False,
            unrelated_response="I am an AI for food ordering and not a general purpose LLM."
        )

    # Extract quantity
    qty = 1
    nums = re.findall(r"\b\d+\b", lower)
    if nums:
        qty = int(nums[0])

    return OrderExtraction(
        is_food_related=True,
        is_confirming_partial=False,
        dish_name=matched_dish or "unknown",
        quantity=qty
    )
