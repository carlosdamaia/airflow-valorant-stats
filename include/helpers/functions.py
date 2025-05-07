import ast
import logging
import pandas as pd
from sqlalchemy import MetaData, insert, Table, text
from include.helpers.airflow_var import (
    CREATE_MATCH_STATS_QUERY, CURSOR, DTYPE_MMR_HISTORY, ENGINE, MMR_COLUMNS,
    MMR_COLUMNS_RENAMED, PUUID, REGION, TABLE_MATCH_STATS, TABLE_MMR_HISTORY,
    COL_MATCH_MMR, BUCKET_NAME
)
from include.helpers.utils import api_hook, api_response, get_headers, try_put_object
from airflow.models import Variable
from datetime import datetime

def url_mmr_history():
    endpoint = Variable.get('endpoint_get_mmr_history')
    api = api_hook()
    url = f'{api.host}{endpoint}'.format(region=REGION, puuid=PUUID)
    headers = get_headers()
    response = api_response(url, headers)
    
    return response

def url_match(match_id):
    endpoint = Variable.get('endpoint_get_match_stats')
    api = api_hook()
    url = f'{api.host}{endpoint}'.format(region=REGION, match_id=match_id)
    headers = get_headers()
    response = api_response(url, headers)

    return response
    
def filter_mmr_columns(mmr_history):
    bruto_mmr_history = mmr_bruto_to_df(mmr_history)
    df_filtered = rename_mmr_columns(bruto_mmr_history)
    df = format_date(df_filtered, 'date')

    return df

def mmr_bruto_to_df(mmr_history):
    if 'data' in mmr_history:
        bruto_mmr_history = pd.json_normalize(mmr_history['data'])

        return bruto_mmr_history

def rename_mmr_columns(bruto_mmr_history):
    df_mmr = bruto_mmr_history[MMR_COLUMNS].rename(columns=MMR_COLUMNS_RENAMED)

    return df_mmr

def format_date(df, date_col):
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')

    return df

def _test_database_conn():
    try:
        with ENGINE.connect() as connection:
            return 'Conexão bem sucedida!'
    except Exception as e:
        raise ValueError(f'Falha na conexão com o banco de dados: {e}')
    
def select_everything_from(table_name):
    query = f'SELECT * FROM {table_name}'
    return query

def insert_missing_ids(dataframe, ids_list):
    insert_stmt = create_insert_stmt(TABLE_MMR_HISTORY)

    for _, linha in dataframe.iterrows():
            
        linha_dict = linha.to_dict()

        if linha_dict['match_id'] not in ids_list:
            
            logging.info(f'ID {linha_dict['match_id']} adicionado ao banco de dados')
            
            CURSOR.execute(insert_stmt.values(**linha_dict))

        else:
            
            logging.info(f'Já possui o ID {linha_dict['match_id']} no banco de dados')
            
    CURSOR.close()

def insert_missing_matches(dataframe):
    insert_stmt = create_insert_stmt(TABLE_MATCH_STATS)

    for _, linha in dataframe.iterrows():
        
        linha_dict = linha.to_dict()
        
        try:
            CURSOR.execute(insert_stmt.values(**linha_dict))
            logging.info(f'Dados da partida {linha_dict['match_id']} inseridos no banco de dados.')
        except Exception as e:
            raise ValueError(f'Erro ao inserir os dados da partida no banco de dados: {e}')
        
def create_insert_stmt(table_name):
    metadata = MetaData()
    meta_table = Table(table_name, metadata, autoload_with=ENGINE)
    insert_stmt = insert(meta_table)

    return insert_stmt

def create_table_match_stats():
    sql = text(CREATE_MATCH_STATS_QUERY)
    try:
        ENGINE.execute(sql)
        return f'Tabela {TABLE_MATCH_STATS} criada.'
    except Exception as e:
        raise ValueError(f'A tabela {TABLE_MATCH_STATS} não pôde ser criada!')

def to_list(value):
    value = ast.literal_eval(value)

    return value

def missing_ids_list(mmr_ids, match_stats_id):
    mmr_ids = to_list(mmr_ids)
    match_stats_id = to_list(match_stats_id)
    missing_ids = []

    for item in mmr_ids:
        if item not in match_stats_id:
            missing_ids.append(item)
            logging.info(f'Adicionando {item} na lista...')
    
    return missing_ids

def add_df_column(dataframe, column_name, column_value):
    dataframe.insert(
        len(dataframe.columns),
        column_name,
        column_value
    )

def sum_total_rounds(dataframe):
    total_rounds = int(dataframe['rounds_won'].iloc[0]) + int(dataframe['rounds_lost'].iloc[0])
    return total_rounds

def add_total_rounds(dataframe):
    total_rounds = sum_total_rounds(dataframe)
    add_df_column(dataframe, 'total_rounds', total_rounds)

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

def create_table_mmr_history(dataframe):
    dataframe.to_sql(
        TABLE_MMR_HISTORY,
        ENGINE,
        if_exists='fail',
        index=False,
        dtype=DTYPE_MMR_HISTORY
    )
    
def save_json_stats(missing_ids):
    stats_json = []

    for item in missing_ids:
        api_response = url_match(item)
        stats_json.append(api_response)
        
    file_path = try_put_object(stats_json, BUCKET_NAME, 'stats.json')
    
    return file_path