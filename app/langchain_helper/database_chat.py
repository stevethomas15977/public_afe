#!/usr/bin/env python3
from langchain_openai import ChatOpenAI
from langchain_helper.log_callback_handler import NiceGuiLogElementCallbackHandler
from nicegui import ui, app
import os
from context import Context
from pandas import isna, read_excel
from sqlite3 import Connection
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from typing_extensions import TypedDict, Annotated
from langchain.chat_models import init_chat_model

context = None
db = None
query_prompt_template = None
llm = None

def columns():
    return {
        'API_UWI': 'API', 
        'WellName': 'Name', 
        'Co-dev': 'Co-dev',
        'Child': 'Child',
        'Pct cum oil greater than 7.5': 'PctCumOilGreaterThan7.5',
        'In/Out': 'InOut',
        'Remarks': 'Remarks',
        'Cum Oil': 'CumOil',
        'Cum Oil bbl per ft': 'CumOilBblPerFt',
        'Pct of Group Cum Oil bbl per ft': 'PctOfGroupCumOilBblPerFt',
        'ENVOperator': 'Operator', 
        'ENVInterval': 'Interval', 
        'FirstProdDate': 'FirstProdDate', 
        'TVD_FT': 'TotalVirticalDepthFeet', 
        'LateralLength_FT': 'LateralLength_FT',
        'PerfInterval_FT': 'PerferatedInterval_FT', 
        'Effective_Perf_Interval': 'Effective_Perferated_Interval',
        'ProppantIntensity_LBSPerFT': 'ProppantIntensity_LBSPerferatedInvervalFT', 
        'BH_Lat': 'BottomHoleLatitude',
        'BH_Long': 'BottomHoleLongitude',  
        'RKB_Elev': 'RKB_Elevation', 
        'TVD_SS': 'TotalVirticalDepthSubSea',
        'Average-Lateral-Spacing-at-BHL': 'AverageLateralSpacingAtBHL',
        'Bound-Half-Bound': 'BoundHalfBound',
        'Adjacent-Child': 'AdjacentChild',
        'Parents': 'Parents',
        'Parent-1': 'Parent-1',
        'Parent-1-First-Production-Date': 'Parent-1-First-Production-Date',
        'Parent_1-Delta-First-Production-Months': 'Parent_1-Delta-First-Production-Months',
        'Parent_1-Landing-Zone': 'Parent_1-Landing-Zone',
        'Parent-2': 'Parent-2',
        'Parent-2-First-Production-Date': 'Parent-2-First-Production-Date',
        'Parent_2-Delta-First-Production-Months': 'Parent_2-Delta-First-Production-Months',
        'Parent_2-Landing-Zone': 'Parent_2-Landing-Zone',
        'Adjacent-2-West': 'Adjacent-2-West',
        'Adjacent-2-Distance-West': 'Adjacent-2-Distance-West',
        'Adjacent-2-Hypotenuse-Distance-West': 'Adjacent-2-Hypotenuse-Distance-West',
        'Adjacent-1-East': 'Adjacent-1-East',
        'Adjacent-1-Distance-East': 'Adjacent-1-Distance-East',
        'Adjacent-1-Hypotenuse-Distance-East': 'Adjacent-1-Hypotenuse-Distance-East',
        'Group-ID': 'Group-ID', 
        'Group-Lateral-Spacing-at-BHL': 'Group-Lateral-Spacing-at-BHL',
        'Group-Hypotenuse-Spacing-at-BHL': 'Group-Hypotenuse-Spacing-at-BHL'
    }

def dtype ():
    return {
        'API': 'TEXT', 
        'Name': 'TEXT', 
        'Co-dev': 'TEXT',
        'Child': 'TEXT',
        'PctCumOilGreaterThan7.5': 'TEXT',
        'InOut': 'TEXT',
        'Remarks': 'TEXT',
        'CumOil': 'TEXT',
        'CumOilBblPerFt': 'TEXT',
        'PctOfGroupCumOilBblPerFt': 'TEXT',
        'Operator': 'TEXT', 
        'Interval': 'TEXT', 
        'FirstProdDate': 'TEXT', 
        'TotalVirticalDepthFeet': 'TEXT', 
        'LateralLength_FT': 'TEXT',
        'PerferatedInterval_FT': 'TEXT', 
        'Effective_Perferated_Interval': 'TEXT',
        'ProppantIntensity_LBSPerferatedInvervalFT': 'TEXT', 
        'BottomHoleLatitude': 'TEXT',
        'BottomHoleLongitude': 'TEXT',  
        'RKB_Elevation': 'TEXT', 
        'TotalVirticalDepthSubSea': 'TEXT',
        'AverageLateralSpacingAtBHL': 'TEXT',
        'BoundHalfBound': 'TEXT',
        'AdjacentChild': 'TEXT',
        'Parents': 'TEXT',
        'Parent-1': 'TEXT',
        'Parent-1-First-Production-Date': 'TEXT',
        'Parent_1-Delta-First-Production-Months': 'TEXT',
        'Parent_1-Landing-Zone': 'TEXT',
        'Parent-2': 'TEXT',
        'Parent-2-First-Production-Date': 'TEXT',
        'Parent_2-Delta-First-Production-Months': 'TEXT',
        'Parent_2-Landing-Zone': 'TEXT',
        'Adjacent-2-West': 'TEXT',
        'Adjacent-2-Distance-West': 'TEXT',
        'Adjacent-2-Hypotenuse-Distance-West': 'TEXT',
        'Adjacent-1-East': 'TEXT',
        'Adjacent-1-Distance-East': 'TEXT',
        'Adjacent-1-Hypotenuse-Distance-East': 'TEXT',
        'Group-ID': 'TEXT', 
        'Group-Lateral-Spacing-at-BHL': 'TEXT',
        'Group-Hypotenuse-Spacing-at-BHL': 'TEXT'
    }

class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

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

def on_startup():
    try:
        context = Context()
        excel_path = os.path.join(context.projects_path, "test", "test-offset-well-identification-1.8.xlsx")
        df = read_excel(excel_path, engine='openpyxl', header=0)
        df = df.rename(columns=columns())
        db_path = os.path.join(context.projects_path, "test", "logs", "offset-well-identification.db")
        connection = Connection(db_path)
        df.to_sql('offset-well-identification', connection, if_exists='replace', index=False, dtype=dtype())
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}?mode=ro")
        query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
        llm = init_chat_model("gpt-4o-mini", model_provider="openai")




    except Exception as e:
        print(e)

app.on_startup(lambda: on_startup())

@ui.page('/')
async def main():
    llm = ChatOpenAI()

    async def send() -> None:
        question = text.value
        text.value = ''

        with message_container:
            ui.chat_message(text=question, name='You', sent=True)
            response_message = ui.chat_message(name='Bot', sent=False)
            spinner = ui.spinner(type='dots')

        response = ''
        async for chunk in llm.astream(question, config={'callbacks': [NiceGuiLogElementCallbackHandler(log)]}):
            response += chunk.content
            response_message.clear()
            with response_message:
                ui.html(response)
            ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
        message_container.remove(spinner)

    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')

    # the queries below are used to expand the contend down to the footer (content can then use flex-grow to expand)
    ui.query('.q-page').classes('flex')
    ui.query('.nicegui-content').classes('w-full')

    with ui.tabs().classes('w-full') as tabs:
        chat_tab = ui.tab('Chat')
        logs_tab = ui.tab('Logs')
    with ui.tab_panels(tabs, value=chat_tab).classes('w-full max-w-2xl mx-auto flex-grow items-stretch'):
        message_container = ui.tab_panel(chat_tab).classes('items-stretch')
        with ui.tab_panel(logs_tab):
            log = ui.log().classes('w-full h-full')

    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        with ui.row().classes('w-full no-wrap items-center'):
            placeholder = 'message' if os.getenv("OPENAI_API_KEY") != 'not-set' else \
                'Please provide your OPENAI key in the Python script first!'
            text = ui.input(placeholder=placeholder).props('rounded outlined input-class=mx-3') \
                .classes('w-full self-center').on('keydown.enter', send)
        ui.markdown('simple chat app built with [NiceGUI](https://nicegui.io)') \
            .classes('text-xs self-end mr-8 m-[-1em] text-primary')


ui.run(title='Chat with GPT-3 (example)')