# public_afe
This repo is for showcasing the AFE work to the public.

## Python environment setup
'''
# Set up the virtual environment and install dependencies
python3 -m venv venv
. venv/bin/activate
pip install pipenv
pipenv sync

sh -c "cat > $APP_PATH/.env" <<EOG
        PYTHONPATH="$PYTHONPATH:models:helpers:services:database"
        VERSION="1.8"
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
        NEW_MEXICO_LAND_SURVEY_SYSTEM_DATABASE="new_mexico_land_survey_system.db"
        NM_SECTION_COLUMN="FRSTDIVLAB"
        TX_ABSTRACT_COLUMN="ABSTRACT_L"
        USERNAME="afe-admin"
        APP_SECRET=$APP_SECRET
        S3_BUCKET_NAME="$S3_BUCKET_NAME"
        GEOJSON_PATH="$GEOJSON_PATH"
        EOG

'''
