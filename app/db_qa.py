from helpers import (create_tool_node_with_fallback, 
                     handle_tool_error)
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

import os

def main():

    @tool
    def db_query_tool(query: str) -> str:
        """
        Execute a SQL query against the database and get back the result.
        If the query is not correct, an error message will be returned.
        If an error is returned, rewrite the query, check the query, and try again.
        """
        result = db.run_no_throw(query)
        if not result:
            return "Error: Query failed. Please rewrite your query and try again."
        return result

    try:
        os.environ["LANGSMITH_PROJECT"] = "db_qa.py"

        db_path = os.path.join(os.path.dirname(__file__), "database", "Chinook.db")
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

        toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(model="gpt-4o-mini"))
        tools = toolkit.get_tools()

        query_check_system = """You are a SQL expert with a strong attention to detail.
        Double check the SQLite query for common mistakes, including:
        - Using NOT IN with NULL values
        - Using UNION when UNION ALL should have been used
        - Using BETWEEN for exclusive ranges
        - Data type mismatch in predicates
        - Properly quoting identifiers
        - Using the correct number of arguments for functions
        - Casting to the correct data type
        - Using the proper columns for joins

        If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

        You will call the appropriate tool to execute the query after running this check."""

        query_check_prompt = ChatPromptTemplate.from_messages(
            [("system", query_check_system), ("placeholder", "{messages}")]
        )
        query_check = query_check_prompt | ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(
            [db_query_tool], tool_choice="required"
        )

        response = query_check.invoke({"messages": [("user", "SELECT * FROM Artist LIMIT 10;")]})

        print(response) 
        
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()