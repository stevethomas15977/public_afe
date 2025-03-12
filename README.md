# An AI research assistant for buying/selling non-operating working-interests in oil/gas wells.

## 1. The business problem and who the customers/users are

<span style="font-size:1.5em;">
The business problem consists of an oil and gas drilling investment firm (customer), with a significant amount of money to put to work. The customer desires to participate in more deals but is limited to a small number of deal participation, due to the lack of qualified financial analysts and off-the-self financial analysis automation solutions.
<br><br>
Energy industry Thought Leaders have indicated the marketplace for buying and selling oil and gas well working interest is to grow significantly in 2025 and beyond. But this marketplace will still be very competitive and fast paced, so potential investors must perform fast Return on Investment analysis, most of the time within a day or two of the deal’s offering.
<br><br>
It is proposed to build a custom automation software solution that will enable faster Return on Investment analysis thus potentially increasing deal participation and putting more investment money to work.

</span>

## 2. How you worked with them to make sure that your solution meets their needs

<span style="font-size:1.5em;">
As a technology consultant, I coordinated and led recurring work sessions to discover/document/learn current processes and demonstrated working software, that I developed. All work sessions were recorded, transcribed and summarized by AI then emailed to each team member. These summaries provided quality feedback, with sentiment, that helped ensure that the solution was meeting the client’s needs.
<br><br>
A simple roadmap document (below) was created, as a communications tool, that identifies and prioritizes key roadmap tasks that could be automated.

</span>

![Roadmap](roadmap.png)

## 3. Demo the solution and explain how it addresses the business problem

<span style="font-size:1.5em;">
This demonstration will show how this solution automated several previously manual tasks, thus reclaiming up to 20 hours per deal, that was put to work on higher value tasks. Two of these automated tasks are: 
<br><br>
1. Reduce manual data entry, using OCR and AI to extract key attributes from the PDF and image files. The value-add here is the replacement of previous error prone copy-and-paste tasks of text from both PDFs and images into an Excel spreadsheet. The automated task now extracts the desired text feature and inserts them into a database to downstream processing.
<br><br>
2. Automation of deterministic tasks, such as “Offset Well Co-development Groups” and “Child Well Risk Gun Barrel Plot”. For example,
<br><br>
“Offset Well Co-development Groups” is a report that list groups well that will be used as a substitute for the projected future cash flows of the proposed well grouping and a key input to the Return on Investment calculation.
<br><br>
“Child Well Risk Gun Barrel Plot” is a Scatter Plot that indicates any surround well groups to the proposed well group that could potentially imped the future cash flows. Any identified risk is subtracted from the future cash flows calculation.
<br><br>


</span>

## 4. Show and explain the architecture, platform, technical tools, language used, e.g., RAG model, AWS Bedrock, LangChain, python (strong preference) including which libraries, etc.

<span style="font-size:1.5em;">
Please see the Github repository <a href="https://github.com/stevethomas15977/public_afe/tree/main/app">AFE Public</a> for a complete list of technologies.
<br><br>
The web application is built using python. The python libraries may be viewed via this <a href="https://github.com/stevethomas15977/public_afe/blob/main/app/Pipfile">Pipfile</a>. The UI is built with <a href="https://nicegui.io/">NiceGUI<a>, which is a python-base web framework. Database management is provided by SQLite. The <a href="https://github.com/stevethomas15977/public_afe/blob/main/app/workflow_manager.py">Workflow</a> is a custom home-grown implementation. Excel generation is provided by python library <a href="https://xlsxwriter.readthedocs.io/">XLSXWriter</a>. Current AI and OCR technologies include ChatGPT and Amazon Textract. These technologies are used to extract text from a PDF with a custom python library <a href="https://github.com/stevethomas15977/public_afe/blob/main/app/helpers/anakarko_afe_helper.py">PDFHelper</a>.
<br><br>
My goal here is to highlight my python programming skills and show how AI is used to automate previous manual tasks. If time permitting, I would like to explain my plan to refactor this version 1 solution into an Agentic ReAct-based LLM application using the orchestration and integration frameworks of <a href="https://academy.langchain.com/courses/take/intro-to-langgraph">LangGraph</a> and <a href="https://python.langchain.com/docs/tutorials/">LangChain</a>. Specifically for routing, memory management, tool calls and RAG. As well as asynchronous data wrangling implementation that ensures a well-architected RAG implementation. 
<br><br>
The goal of this refactoring is to create an AI Research Assistant specifically for Return on Investment analysis of proposed non-conventional oil/gas drilling operations budgets. The following knowledge bases and others could be used as implementation references: 
<br>
  <ul>
  <li><a href="https://github.com/langchain-ai/langchain-academy/blob/main/module-4/research-assistant.ipynb">Research Assistant</a></li>
  <li><a href="https://jxnl.co/writing/2024/06/05/predictions-for-the-future-of-rag">Predictions for the Future of RAG</a></li>
  <li><a href="https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/storm/storm.ipynb">Web Search (STORM)</a></li>
</ul>
  
 
  
</span>

## 5. Explain how the solution was deployed, maintained, and supported

<span style="font-size:1.5em;">
The current version is a simple monolith web application running on AWS LightSail. LightSail is a very cost-effective compute solution for small to medium businesses. Compute components consist of a single load balancer for TLS termination and a target-group of EC2 instance running a python-based web application. See diagram below “AFE Analysis (v1.0).
<br><br>
The solution is deployed using <a href="https://github.com/stevethomas15977/public_afe/blob/main/.github/workflows/main.yaml">Github Actions</a>, <a href="https://github.com/stevethomas15977/public_afe/tree/main/terraform">Terraform</a>, and Linux BASH cloud-init scripting.
<br><br>
Maintain and support is included in a separate SLA engagement. Generally, new releases and bug fixes follow an agile release cycle. Critical bugs are resolved ASAP.

</span>

![Workflow Diagram](workflow_diagram_v1.png "AFE Analysis (v1.0)")

![Context Diagram](context_diagram_v1.png "AFE Analysis (v1.0)")

### Run within WLS Ubuntu 24.04 LTS and VS Code:
```
cd /app
python3 -m venv venv
. venv/bin/activate
pip install pipenv
pipenv sync

sh -c "cat > app/.env" <<EOG
PYTHONPATH="$PYTHONPATH:models:helpers:services:database"
VERSION="1.8"
HTTP_PORT="$HTTP_PORT"
PRIVATE_IPV4="$PRIVATE_IPV4"
ENV="$ENV"
APP="$APP"
APP_ROOT="$APP_ROOT"
AFE_PATH=$AFE_PATH
APP_PATH="$APP_PATH"
PROJECTS_PATH="$PROJECTS_PATH"
GEOJSON_PATH="$AFE_PATH/$S3_FOLDER_NAME"
CODEVELOPMENT_FIRST_PRODUCTION_DATE_DAYS_THRESHOLD=180
MAX_DISTANCE_THRESHOLD=8000
HORIZONTAL_DISTANCE_THRESHOLD=1600
VERTICAL_DISTANCE_THRESHOLD=500
LATERAL_LENGTH_THRESHOLD=.8
HYPOTENUSE_DISTANCE_THRESHOLD=1800
DEPTH_DISTANCE_THRESHOLD=1000
PCT_GROUP_CUM_OIL_GREATER_THAN_THRESHOLD=7.5
TEXAS_LAND_SURVEY_SYSTEM_DATABASE="texas_land_survey_system.db"
NEW_MEXICO_LAND_SURVEY_SYSTEM_DATABASE="new_mexico_land_survey_system_with_states.db"
NM_SECTION_COLUMN="FRSTDIVLAB"
TX_ABSTRACT_COLUMN="ABSTRACT_L"
USERNAME="$APP_USERNAME"
APP_SECRET="$APP_SECRET"
S3_BUCKET_NAME="$S3_BUCKET_NAME"
GEOJSON_PATH="$GEOJSON_PATH"
AFE_PROD_DNS="localhost"
APP="offset-well-identification"
PLSS_BUCKET="afe-plss"
LANGCHAIN_API_KEY="$LANGCHAIN_API_KEY"
LANGCHAIN_TRACING_V2="true"
OPENAI_API_KEY="$OPENAI_API_KEY"
AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION"
AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
EOG
```

##### See the .vscode/launch.json and run "Debug Main" configuration.

## Definitions

#### Working Interest (US)
An ownership interest in an oil & gas lease giving the working interest owner the authority to explore for, drill, and produce oil and gas from the leased property. The working interest owner benefits from the resulting production subject to payment of royalties and associated costs of exploring, drilling, leasing, and producing oil and gas.

### Carried Interest (Oil and Gas) (US)
In the oil and gas context, a carried interest is a fractional oil and gas interest that is not required to pay for drilling or operational expenses for a limited time (carry period). These expenses are paid by the other working interest owners (called co-tenants) of the property. Depending on the terms of the carried interest, the carry may apply only to the owner's share of costs incurred in drilling or continue through subsequent costs incurred in well completion.
Until a well has paid out, carried interest owners do not normally receive income from the well but thereafter receive an agreed percentage share of its subsequent production.

### Well Completion (US)
In the upstream oil and gas industry, the actions performed after a well is drilled to enable it to produce oil and gas.
Well completion may include:
Installing casing, tubing, packers, or other equipment in the wellbore to isolate producing geologic formations and allow production from the target depths.
Perforating the casing to allow oil and gas to enter the well.
Stimulating the well with acids or other fluids to allow oil and gas to more easily flow into the well.
Hydraulic fracturing, or injection of fluids at high pressure to cause fractures in the formation and release oil and gas from the formation into the well.
After these activities, the operator flows back the well to recover the fluids used to stimulate or fracture the well and commences production of oil and gas. The operator may also test the well to determine oil production and gas production rates, well pressures, gas-oil ratio, and other information.
Completion may also refer to the process of perforating, stimulating, and equipping an injection well or disposal well to inject fluids into a formation.

### After Payout (US)
Sometimes called at payout, the point after all the costs of exploring, drilling, producing, equipping, completing, and operating have been recouped from the sale of production from an oil or gas well. Payout is often a defined term in farmouts, joint operating agreements, and other agreements relating to oil and gas exploration.
