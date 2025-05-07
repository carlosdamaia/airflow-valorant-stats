from utils.helper import read_minio_json, add_total_rounds, format_date, mmr_col
from utils.constants import (
    COL_METADATA, RENAMED_COL_METADATA, NAME, FILTERED_JSON_PATH,
    COL_PLAYER, RENAMED_COL_PLAYER, COL_PLAYER_TEAM, RENAMED_COL_PLAYER_TEAM
)
import pandas as pd

if __name__ == '__main__':
    
    def app():
                                
        data_file = read_minio_json()
        
        df = pd.DataFrame()
        
        for item in data_file:
            
            data = item['data']
            
            metadata = (
                pd.json_normalize(data)
                [COL_METADATA]
                .rename(columns=RENAMED_COL_METADATA)
            )
            
            player = (
                pd.json_normalize(data['players'])
                .query(f"name == '{NAME}'")
                [COL_PLAYER]
                .rename(columns=RENAMED_COL_PLAYER)
            )
            
            player_team_name = player['team'].iloc[0]

            player_team = (
                pd.json_normalize(data['teams'])
                .query(f"team_id == '{player_team_name}'")
                [COL_PLAYER_TEAM]
                .rename(columns=RENAMED_COL_PLAYER_TEAM)
            )

            metadata, player, player_team  = [
                df.reset_index(drop=True) for df in [
                    metadata, 
                    player, 
                    player_team
                ]
            ]

            match_stats = (
                metadata.join(player)
                .join(player_team)
            )
            
            add_total_rounds(match_stats)
    
            match_mmr = mmr_col(match_stats)

            match_stats = (
                match_stats.join(match_mmr)
                .pipe(format_date, 'date')
            )
            
            df = pd.concat([df, match_stats], ignore_index=True)
            
        df.to_json(FILTERED_JSON_PATH, orient='records', indent=4, force_ascii=False)
    
    app()
