# AFE Aanalysis
## THe business problem
### Determining Return on Investment for non-traditional (Hydralyic Fracing) oil/gas exploration is complex and 
the business problem and who the customers/users are
how you worked with them to make sure that your solution meets their needs
demo the solution and explain how it addresses the business problem
show and explain the architecture, platform, technical tools, language used, e.g., RAG model, AWS Bedrock, Langchain, python (strong preference) including which libraries, etc.
explain how the solution was deployed, maintained, and supported

## Python environment setup
```
cd /app
python3 -m venv venv
. venv/bin/activate
pip install pipenv
pipenv sync

sh -c "cat > $APP_PATH/.env" <<EOG
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
USERNAME="afe-admin"
APP_SECRET="$APP_SECRET"
S3_BUCKET_NAME="$S3_BUCKET_NAME"
GEOJSON_PATH="$GEOJSON_PATH"
AFE_PROD_DNS="localhost"
APP="offset-well-identification"
PLSS_BUCKET="afe-plss"
LANGCHAIN_API_KEY="$LANGCHAIN_API_KEY"
LANGCHAIN_TRACING_V2="true"
OPENAI_API_KEY="$OPENAI_API_KEY"
EOG
```
