from langchain_community.utilities import SQLDatabase
from app.context import Context
import os
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langchain import hub
from typing_extensions import Annotated
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

def main():
    context = Context()

    if not os.environ.get("LANGSMITH_API_KEY"):
        raise ValueError("Please set the LANGSMITH_API_KEY environment variable")
    
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    db = SQLDatabase.from_uri(f"sqlite:///{context._texas_land_survey_system_database_path}?mode=ro")

    def execute_query(state: State):
        """Execute SQL query."""
        execute_query_tool = QuerySQLDatabaseTool(db=db)
        return {"result": execute_query_tool.invoke(state["query"])}

    def write_query(state: State):
        """Generate SQL query to fetch information."""
        prompt = query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": state["question"],
            }
        )
        structured_llm = llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        return {"query": result["query"]}

    def generate_answer(state: State):
        """Answer question using retrieved information as context."""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["query"]}\n'
            f'SQL Result: {state["result"]}'
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}

    llm = init_chat_model("gpt-4o-mini", model_provider="openai")

    query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

    # assert len(query_prompt_template.messages) == 1
    # query_prompt_template.messages[0].pretty_print()

    # response = write_query({"question": "How many Counties are there?"})
    # print(response["query"])

    # response = execute_query({"query": response["query"]})
    # print(response["result"])

    graph_builder = StateGraph(State).add_sequence([write_query, execute_query, generate_answer])
    graph_builder.add_edge(START, "write_query")
    graph = graph_builder.compile()

    for step in graph.stream({"question": "How many counties are there?"}, stream_mode="updates"):
        print(step)
if __name__ == "__main__":
    main()