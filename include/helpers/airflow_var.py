from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID, INTEGER, DATE, TEXT
from airflow.models import Variable
import os

RAW_JSON_PATH = Variable.get('raw_json_path')
FILTERED_JSON_PATH = Variable.get('filtered_json_path')
DB_URL = Variable.get('DB_URL')
DB_URL_DOCKER = Variable.get('DB_URL_dockeroperator')
REGION = Variable.get("region")
NAME = Variable.get("name")
TAG = Variable.get("tag")
PUUID = Variable.get("puuid")
BUCKET_NAME = 'stats'
TABLE_MMR_HISTORY = Variable.get('table_mmr_history')
TABLE_MATCH_STATS = Variable.get('table_match_stats')
ENGINE = create_engine(DB_URL)
CURSOR = ENGINE.connect()
FOLDER_ID = os.getenv("FOLDER_ID")
RETENTION_FOLDER_ID = os.getenv("RETENTION_FOLDER_ID")
LOCAL_FOLDER = Variable.get("LOCAL_FOLDER")

MMR_COLUMNS = [
    'match_id',
    'ranking_in_tier',
    'mmr_change_to_last_game',
    'date',
    'images.small'
]

MMR_COLUMNS_RENAMED = {
    'ranking_in_tier': 'current_mmr', 
    'mmr_change_to_last_game': 'mmr_change', 
    'images.small': 'elo_img'
}

DTYPE_MMR_HISTORY = {
    'match_id': UUID(as_uuid=True),
    'current_mmr': INTEGER,
    'mmr_change': INTEGER,
    'date': DATE,
    'elo_img': TEXT
}

CREATE_MATCH_STATS_QUERY = f'''
    CREATE TABLE IF NOT EXISTS {TABLE_MATCH_STATS} (
        match_id UUID PRIMARY KEY,
        map TEXT,
        date DATE,
        completed BOOLEAN,
        season TEXT,
        team TEXT,
        agent TEXT,
        score INT,
        kills INT,
        deaths INT,
        assists INT,
        hs INT,
        bodyshots INT,
        legshots INT,
        damage_dealt INT,
        damage_received INT,
        elo TEXT,
        level INT,
        won BOOLEAN,
        rounds_won INT,
        rounds_lost INT,
        total_rounds INT,
        current_mmr INT,
        mmr_change INT,
        elo_img TEXT
    )
'''

COL_MATCH_MMR = [
    'current_mmr', 
    'mmr_change', 
    'elo_img'
]