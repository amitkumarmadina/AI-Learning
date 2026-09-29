import os
import json
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# Load environment variables
load_dotenv()

# Initialize clients
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ─── Tool Functions ───────────────────────────────────────────────

def web_search(query: str) -> str:
    """Search the web using Tavily and return the answer."""
    result = tavily.search(query=query, max_results=3)
    # Combine the content from all results into a single string
    combined = "\n\n".join(
        f"Source: {r['url']}\n{r['content']}" for r in result.get("results", [])
    )
    return combined if combined else "No results found."


def calculate(expression: str) -> str:
    """Evaluate a mathematical expression string and return the result."""
    try:
        # Only allow safe math operations
        allowed_names = {"__builtins__": {}}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


# ─── Tools Schema (OpenAI-compatible format) ─────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information on any topic. Use this when the user asks a question that requires up-to-date or factual information from the internet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression and return the result. Use this for arithmetic, algebra, or any math calculation. The expression should be a valid Python math expression like '2*2', '100/4', '2**10', etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate, e.g. '2+2', '15*3', '2**8'."
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Map tool names to their Python functions
available_functions = {
    "web_search": web_search,
    "calculate": calculate,
}


# ─── Agent Logic ──────────────────────────────────────────────────

def run_agent(user_query: str):
    """
    Send the user query to the LLM. The LLM decides which tool to call (or none).
    If a tool is called, execute it and send the result back to the LLM for a final answer.
    """
    print(f"\n{'='*60}")
    print(f"User Query: {user_query}")
    print(f"{'='*60}")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant with access to two tools: "
                "web_search (for looking up information on the internet) and "
                "calculate (for evaluating math expressions). "
                "Decide which tool to use based on the user's query, or respond directly if no tool is needed."
            )
        },
        {
            "role": "user",
            "content": user_query
        }
    ]

    # Step 1: Send query to LLM with tools
    response = groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message

    # Step 2: Check if the LLM wants to call a tool
    if response_message.tool_calls:
        # Add the assistant's response (with tool calls) to messages
        messages.append(response_message)

        # Process each tool call
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"\n🔧 Tool Called : {function_name}")
            print(f"📥 Arguments  : {function_args}")

            # Execute the tool function
            function_to_call = available_functions[function_name]
            tool_result = function_to_call(**function_args)

            print(f"📤 Tool Result : {tool_result[:200]}...")  # Print first 200 chars

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result,
            })

        # Step 3: Send tool results back to LLM for final answer
        final_response = groq.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
        )

        final_answer = final_response.choices[0].message.content
    else:
        # No tool call — LLM answered directly
        final_answer = response_message.content

    print(f"\n{'─'*60}")
    print(f"🤖 Final Answer:\n{final_answer}")
    print(f"{'─'*60}")

    return final_answer


# ─── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    user_input = input("\nEnter your query: ")
    run_agent(user_input)
