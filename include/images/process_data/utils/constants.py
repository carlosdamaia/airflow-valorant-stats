from sqlalchemy import create_engine
import os

MINIO_CLIENT = os.getenv("minio_client")
RAW_JSON_PATH = os.getenv('raw_json_path')
FILTERED_JSON_PATH = os.getenv('filtered_json_path')
NAME = os.getenv('name')
TABLE_MMR_HISTORY = os.getenv('table_mmr_history')
DB_URL = os.getenv('db_url')
ENGINE = create_engine(DB_URL)

COL_METADATA = [    
    "metadata.match_id",
    "metadata.map.name",
    "metadata.started_at",
    "metadata.is_completed",
    "metadata.season.short"
]

RENAMED_COL_METADATA = {
    "metadata.match_id": "match_id",
    "metadata.map.name": "map",
    "metadata.started_at": "date",
    "metadata.is_completed": "completed",
    "metadata.season.short": "season"
}

COL_PLAYER = [
    'team_id',
    'agent.name',
    'stats.score',
    'stats.kills',
    'stats.deaths',
    'stats.assists',
    'stats.headshots',
    'stats.bodyshots',
    'stats.legshots',
    'stats.damage.dealt',
    'stats.damage.received',
    'tier.name',
    'account_level'
]

RENAMED_COL_PLAYER = {
    'team_id': 'team',
    'agent.name': 'agent',
    'stats.score': 'score',
    'stats.kills': 'kills',
    'stats.deaths': 'deaths',
    'stats.assists': 'assists',
    'stats.headshots': 'hs',
    'stats.bodyshots': 'bodyshots',
    'stats.legshots': 'legshots',
    'stats.damage.dealt': 'damage_dealt',
    'stats.damage.received': 'damage_received',
    'tier.name': 'elo',
    'account_level': 'level'
}

COL_PLAYER_TEAM = [
    'won',
    'rounds.won',
    'rounds.lost'
]

RENAMED_COL_PLAYER_TEAM = {
    'won': 'won',
    'rounds.won': 'rounds_won',
    'rounds.lost': 'rounds_lost'
}

COL_MATCH_MMR = [
    'current_mmr', 
    'mmr_change', 
    'elo_img'
]

FILE_PATH = 'stats/stats.json'
BUCKET_NAME = 'stats'