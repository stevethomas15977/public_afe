from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain import hub
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

import os
from app.context import Context


def main():
    try:
        context = Context()

        if not os.environ.get("LANGSMITH_API_KEY"):
            raise ValueError("Please set the LANGSMITH_API_KEY environment variable")
    
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("Please set the OPENAI_API_KEY environment variable")
        
        os.environ["LANGSMITH_PROJECT"] = "afe_offset_well_agent"

        offset_well_database = os.path.join(context.projects_path, "test", "logs", "offset-well-identification.db")
        
        if not os.path.exists(offset_well_database):
            raise ValueError(f"Database file {offset_well_database} does not exist")
        
        print(f"Using database file: {offset_well_database}")

        db = SQLDatabase.from_uri(f"sqlite:///{offset_well_database}")

        llm = init_chat_model("gpt-4o-mini", model_provider="openai")

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        tools = toolkit.get_tools()

        tools

        table_schema = """
            The following table schema provides descriptions of columns in the database to assist in query generation.

            Use the SQLite command 'db.get_table_info()' to get the schema of the table.

            Table: `offset-well-identification`: Contains information about oil wells.

            -'API' (TEXT): This is a unique identifier of the oil well
            -'Name' (TEXT): This is the unique name of the oil well 
            -'Co-dev' (TEXT): Indicates if the oil in within an Codevelopment group of other oil wells.
            -'Child' (TEXT): Indicates if the oil well is child of another oil well.
            -'PctCumOilGreaterThan7.5' (TEXT): Indicates if the oil wells cummulative output of oil per barrel is greater than 7.5 precent
            -'InOut' (TEXT): Yes or No indicator if additional analysis should be preformed on this oil well.
            -'Remarks' (TEXT): Additional description about the oil well.
            -'CumOil' (TEXT): Indicates the amount of monthly cummulate oil produced in barrels of oil
            -'CumOilBblPerFt' (TEXT): Indicates the amount the cummulate oil per barrel devided by the perforated interval in feet.
            -'PctOfGroupCumOilBblPerFt' (TEXT):
            -'Operator' (TEXT): 
            -'Interval' (TEXT):
            -'FirstProdDate' (TEXT): Indicates the first date that barrels of oil were extracted from the oil well.
            -'TotalVirticalDepthFeet' (TEXT): 
            -'LateralLength_FT' (TEXT): Indicates the lateral portion of the oil well or lateral lenght in feet.
            -'PerferatedInterval_FT' (TEXT): Very similiar to the LatervalLength_FT
            -'Effective_Perferated_Interval' (TEXT):
            -'ProppantIntensity_LBSPerferatedInvervalFT' (TEXT): 
            -'BottomHoleLatitude' (TEXT):
            -'BottomHoleLongitude' (TEXT):  
            -'RKB_Elevation' (TEXT): 
            -'TotalVirticalDepthSubSea' (TEXT):
            -'AverageLateralSpacingAtBHL' (TEXT):
            -'BoundHalfBound' (TEXT):
            -'AdjacentChild' (TEXT):
            -'Parents' (TEXT):
            -'Parent-1' (TEXT):
            -'Parent-1-First-Production-Date' (TEXT):
            -'Parent_1-Delta-First-Production-Months' (TEXT):
            -'Parent_1-Landing-Zone' (TEXT):
            -'Parent-2' (TEXT):
            -'Parent-2-First-Production-Date' (TEXT):
            -'Parent_2-Delta-First-Production-Months' (TEXT):
            -'Parent_2-Landing-Zone' (TEXT):
            -'Adjacent-2-West' (TEXT):
            -'Adjacent-2-Distance-West' (TEXT):
            -'Adjacent-2-Hypotenuse-Distance-West' (TEXT):
            -'Adjacent-1-East' (TEXT):
            -'Adjacent-1-Distance-East' (TEXT):
            -'Adjacent-1-Hypotenuse-Distance-East' (TEXT):
            -'Group-ID' (TEXT): 
            -'Group-Lateral-Spacing-at-BHL' (TEXT):
            -'Group-Hypotenuse-Spacing-at-BHL' (TEXT):

            Always generate SQL queries using this schema.
        """
        
        prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")

        custom_prompt_template = prompt_template + "\n\n" + table_schema

        system_message = custom_prompt_template.format(dialect="SQLite", 
                                                top_k=5)


        agent_executor = create_react_agent(llm, tools, prompt=system_message)

        question = "How many oil wells have an interval of 'WOLFCAMP A LOWER'?"

        for step in agent_executor.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
        ):
            step["messages"][-1].pretty_print()

    except Exception as e:

        print(e)

if __name__ == '__main__':
    main()