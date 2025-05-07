import requests
from airflow.hooks.base import BaseHook
import pandas as pd
from include.helpers.airflow_var import ENGINE, BUCKET_NAME
from sqlalchemy import inspect
from minio import Minio
import json
from io import BytesIO

def _get_minio_client():
    minio = BaseHook.get_connection('minio')
    
    client = Minio(
        endpoint=minio.extra_dejson['endpoint_url'].split('//')[1],
        access_key=minio.login,
        secret_key=minio.password,
        secure=False
    )
    
    return client

def create_bucket(bucket_name):
    client = _get_minio_client()
    
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        
def try_put_object(file, bucket_name, json_name):
    client = _get_minio_client()
    
    create_bucket(bucket_name)
    
    try:
        data = json.dumps(file, ensure_ascii=False, indent=4).encode('utf8')
        data_stream = BytesIO(data)
        
        minio_object = client.put_object(
            data=data_stream,
            bucket_name=bucket_name,
            object_name=json_name,
            length=len(data)
        )
        
        file_path = f'{minio_object.bucket_name}/{minio_object.object_name}'
        
        return file_path
    
    except Exception as e:
        raise ValueError('Erro ao salvar arquivo na bucket') from e

def api_hook():
    api = BaseHook.get_connection('henrikdev_api')
    return api

def get_headers():
    api = api_hook()
    headers = api.extra_dejson['headers']
    
    return headers

def format_json(json_data):
    if has_single_quotes(json_data):
        json_data = replace_quotes(json_data)
        
        return json_data
    
def has_single_quotes(json_data):
    if "'" in json_data:   
        return True
    
def has_errors(json_data):
    if "errors" in json_data:
        return False

def replace_quotes(json_data):
    if isinstance(json_data, str):
        json_data = json_data.replace("'", '"')
        json_data = json.loads(json_data)
        return json_data

def df_to_json(df):
    json_data = df.to_json(orient='records')

    return json_data

def json_to_df(json_data):
    df = pd.read_json(json_data, orient='records')

    return df

def read_minio_json(file_path):
    file_name = file_path.split("/")[1]
    client = _get_minio_client()
    
    try:
        minio_object = client.get_object(BUCKET_NAME, file_name)
        data = minio_object.read().decode('utf-8')
        json_data = json.loads(data)
        
        return json_data
    except Exception as e:
        raise ValueError(f'Arquivo não encontrado') from e

def api_response(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        
        return response_json
    
    except requests.exceptions.RequestException as e:       
        raise ValueError('Erro ao tentar obter resposta da API') from e
    

def create_ids_list(table_name):
    query = select_id_column_from(table_name)
    df_table = pd.read_sql_query(query, ENGINE)
    ids_list = fill_id_list(df_table)
    
    return ids_list

def select_id_column_from(table_name):
    query = f'SELECT "match_id" FROM {table_name}'
    
    return query

def fill_id_list(df):
    column_id = df['match_id']
    ids_list = []

    for item in column_id:
        ids_list.append(str(item))

    return ids_list

def table_exists(table_name):
    inspector = inspect(ENGINE)
    return table_name in inspector.get_table_names()

def list_is_empty(lista):
    if isinstance(lista, list):
        if len(lista) > 0:
            return False
        else:
            return True

def save_empty_file():
    create_bucket(BUCKET_NAME)
    try_put_object('', BUCKET_NAME, 'stats.json')