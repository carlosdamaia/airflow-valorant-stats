import logging
from include.helpers.airflow_var import TABLE_MMR_HISTORY
from include.helpers.functions import (
    create_table_mmr_history,
    url_mmr_history,
    filter_mmr_columns,
    insert_missing_ids
)
from include.helpers.utils import (
    create_ids_list, 
    table_exists,
    format_json,
    df_to_json,
    json_to_df
)

def _get_mmr_history():
    mmr_history = url_mmr_history()
    
    return mmr_history
    
def _filter_dataframe(mmr_history):
    json_data = format_json(mmr_history)

    try:
        df = filter_mmr_columns(json_data)
        df = df_to_json(df)

        return df
    
    except Exception as e:
        raise ValueError(f'Erro ao converter ou filtrar para DataFrame') from e
    
def _db_insert(df):
    df = json_to_df(df)

    if table_exists(TABLE_MMR_HISTORY):
        ids_list = create_ids_list(TABLE_MMR_HISTORY)

        try:
            insert_missing_ids(df, ids_list)

            return f'IDs inseridos no banco de dados'
        except Exception as e:
            raise ValueError('Erro ao tentar inserir dados no banco de dados') from e

    else:
        try:
            logging.info(f'Tabela {TABLE_MMR_HISTORY} não existente no banco de dados')
            logging.info('Criando a tabela...')

            create_table_mmr_history(df)
            
            return f'A tabela {TABLE_MMR_HISTORY} foi criada e os dados foram inseridos.'
        except Exception as e:
            raise ValueError('A tabela não pôde ser criada no banco de dados: {e}')