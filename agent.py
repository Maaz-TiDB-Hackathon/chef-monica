from llm import llm
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from search_with_filter_tool import SearchWithFilterTool
# Create a set of tools
tools = [
    SearchWithFilterTool()
]

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create the agent
agent_prompt = PromptTemplate(input_variables=["input", "chat_history", "agent_scratchpad"], 
                              template="""
You are Chef Monica, a food expert providing information about recipes.
Be as helpful as possible and return as much information as possible.
Do not answer any questions that do not relate to recipes.
Display images of recipes when available. 
You are not allowed to use any external knowledge or information.
Only use the information provided in the context.

History of conversation so far:
{chat_history}

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: I already know the answer
Final Answer: [your response here]
```

Begin!

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
    )

# chat_agent = RunnableWithMessageHistory(
#     agent_executor,
#     DBChatMessageHistory,
#     input_messages_key="input",
#     history_messages_key="chat_history",
# )

# Create a handler to call the agent
def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    chat_history = memory.load_memory_variables({}).get("chat_history","")
    response = agent_executor.invoke({"input": user_input, "chat_history": chat_history})
        # Save turn to memory
    memory.save_context({"input": user_input}, {"output": response['output']})
    return response['output']

def clear_chat():
    memory.clear()