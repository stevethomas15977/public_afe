# An IT solution for assisting oil/gas professionals with the assessment of proposed drilling opportunities.

![Compute Context Diagram](workflow_diagram_v1.png "Compute (v1.0)")
Simplified context diagram.

![Compute Context Diagram](context_diagram_v1.png "Compute (v1.0)")
In addition to running locally, the solution is currently configured for deployment on AWS Lightsail via Terraform.

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



