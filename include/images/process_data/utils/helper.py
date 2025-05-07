import ast
import json
import pandas as pd
from utils.constants import TABLE_MMR_HISTORY, COL_MATCH_MMR, ENGINE, BUCKET_NAME, FILE_PATH, MINIO_CLIENT
import logging
import os
from minio import Minio

def _get_minio_client():
    
    client = Minio(
        endpoint=os.getenv("MINIO_ENDPOINT"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        secure=False
    )
    
    return client

def to_list(value):
    value = ast.literal_eval(value)

    return value

def list_is_empty(lista):
    if isinstance(lista, list):
        if len(lista) > 0:
            return False
        else:
            return True
        
def open_json(path):
    with open (path, 'r', encoding='utf-8') as file:
        data_file = json.load(file)
        return data_file
    
def read_minio_json():
    file_name = FILE_PATH.split("/")[1]
    client = _get_minio_client()
    logging.info(f'Client Type: {type(client)}')
    
    try:
        minio_object = client.get_object(BUCKET_NAME, file_name)
        data = minio_object.read().decode('utf-8')
        json_data = json.loads(data)
        
        return json_data
    except Exception as e:
        raise ValueError(f'Arquivo não encontrado') from e
    
def add_total_rounds(dataframe):
    total_rounds = sum_total_rounds(dataframe)
    add_df_column(dataframe, 'total_rounds', total_rounds)
    
def sum_total_rounds(dataframe):
    total_rounds = int(dataframe['rounds_won'].iloc[0]) + int(dataframe['rounds_lost'].iloc[0])
    return total_rounds

def add_df_column(dataframe, column_name, column_value):
    dataframe.insert(
        len(dataframe.columns),
        column_name,
        column_value
    )
    
def format_date(df, date_col):
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')

    return df

def mmr_col(df_match_stats):
    match_id = get_first_row_value(df_match_stats, 'match_id')
    df_mmr = table_to_df_where(TABLE_MMR_HISTORY, 'match_id', match_id)
    match_mmr = (
        df_mmr[COL_MATCH_MMR]
        .reset_index(drop=True)
    )
    return match_mmr

def get_first_row_value(dataframe, column_name):
    value = dataframe[column_name].loc[0]
    return value

def table_to_df_where(table_name, column, value):
    dataframe = pd.read_sql_query(
        select_everything_from_where(table_name, column, value), ENGINE
    )
    return dataframe

def select_everything_from_where(table_name, column, value):
    query = f"SELECT * FROM {table_name} where {column} = '{value}'"
    return query