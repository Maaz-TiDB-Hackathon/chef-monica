from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from typing_extensions import Literal
from search_with_filter_tool import SearchWithFilterTool
import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import OpenAIEmbeddings
from tidb import tidb_client
import crud
import json
memory = InMemorySaver()

@tool
def list_review_for_recipes(recipe_ids: list[int]) -> list[dict]:
    """
    Finds the reviews for recipes

    Args:
        recipe_ids (list[int]): The integer list of recipe ids.

    Returns:
        list[dict]: a list of review dictionaries
    """
    reviews = [
        {'rating': review.rating, 'text': review.review}
        for review in crud.get_reviews(recipe_ids=recipe_ids)
    ]
    return {
        "status": "success",
        "message": "Operation complete",
        "data": reviews
    }
    #return [{'type': 'text', 'text': } for review in crud.get_reviews(recipe_ids=recipe_ids)]

@tool
def find_food_item_in_usda_fdc(food_item: str) -> dict:
    """
    Finds the food item in the USDA FDC database.

    Args:
        food_item (str): The food item name.

    Returns:
        dict: a dictionary containing a list of dictionaries with fdc_id and description
    """
    food_items = crud.find_food_item_in_usda_fdc(food_item)
    return {
        "status": "success",
        "message": "Operation complete",
        "data": list(food_items)
    }

@tool
def find_nutrient_information_for_food_item(fdc_id: int) -> dict:
    """
    Finds the nutrient information for a food item(per 100g) given its fdc_id.

    Args:
        fdc_id (int): The food item fdc_id.

    Returns:
        dict: a dictionary containing a list of dictionaries with nutrient name, amount and unit
    """
    food_items = crud.find_nutrient_information_for_food_item(fdc_id)
    return {
        "status": "success",
        "message": "Operation complete",
        "data": list(food_items)
    }

# Augment the LLM with tools
tools = [SearchWithFilterTool(), list_review_for_recipes, find_food_item_in_usda_fdc, find_nutrient_information_for_food_item]
tools_by_name = {tool.name: tool for tool in tools}


llm = init_chat_model(st.secrets["LANGGRAPH_OPENAI_MODEL"])
llm_with_tools = llm.bind_tools(tools)

# Nodes
def llm_call(state: MessagesState):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    SystemMessage(
                        content="""
You are Chef Monica, a food expert providing information about recipes.
Be as helpful as possible and return as much information as possible.
Answer only the following types of questions as follows:
1. RECIPE SEARCH WITH FILTERS: Show summarized - name, description, aggregate rating, prep time, cook time, total time, calories.
2. SHOW MACROS: Show macros in a tabular format
3. SHOW DETAILED RECIPE: Show all information including image
4. SHOW NUTRITIONAL INFORMATION: Show all nutritional information of a food item in a single table along with dietary insights. Use find_food_item_in_usda_fdc followed by find_nutrient_information_for_food_item tool to get the nutritional information.
5. SUMMARIZE REVIEWS FOR RECIPES: Fetch reviews using list_review_for_recipes tool, analyse and show the summary along with the difficulty of cooking.
Do not answer any questions that do not relate to recipes.
You are not allowed to use any external knowledge or information.
Only use the information provided in the context.
"""
                    )
                ]
                + state["messages"]
            )
        ]
    }

def tool_node(state: dict):
    """Performs the tool call"""

    result = []
    with st.expander("🔨 Tool Call", expanded=False):
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            st.write(f"Called tool :blue[{tool_call["name"]}] with args :blue[{tool_call["args"]}]")
            observation = tool.invoke(tool_call["args"])
            # if tool_call["name"] == SearchWithFilterTool.name:
            st.write(f"Observation: ")
            st.json(observation)
            # else:
            #     st.write(f"Observation: {observation}")
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


# Conditional edge function to route to the tool node or end based upon whether the LLM made a tool call
def should_continue(state: MessagesState) -> Literal["environment", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "Action"
    # Otherwise, we stop (reply to the user)
    return END


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("environment", tool_node)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        # Name returned by should_continue : Name of next node to visit
        "Action": "environment",
        END: END,
    },
)
agent_builder.add_edge("environment", "llm_call")

# Compile the agent
agent = agent_builder.compile(checkpointer=memory)

# Show the agent
agent.get_graph().print_ascii()

def generate_response(input: str) -> str:
    config = {"configurable": {"thread_id": st.session_state.chat_id}}
    messages = [HumanMessage(content=input)]
    messages = agent.invoke({"messages": messages}, config)
    for m in messages["messages"]:
        m.pretty_print()
    return messages["messages"][-1].content

def clear_chat():
    memory.delete_thread(st.session_state.chat_id)