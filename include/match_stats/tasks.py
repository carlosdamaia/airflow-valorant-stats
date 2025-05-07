import os
import logging
from include.helpers.airflow_var import (
    TABLE_MMR_HISTORY,
    TABLE_MATCH_STATS,
    FILTERED_JSON_PATH
)
from include.helpers.functions import (
    create_table_match_stats,
    to_list,
    missing_ids_list,
    insert_missing_matches,
    save_json_stats
)
from include.helpers.utils import (
    create_ids_list,
    table_exists,
    list_is_empty,
    save_empty_file,
    json_to_df
)
import shutil

def _make_mmr_history_list():
	if table_exists(TABLE_MMR_HISTORY):
     
		try:
			mmr_ids = create_ids_list(TABLE_MMR_HISTORY)
			return mmr_ids

		except Exception as e:
			raise ValueError(f'Erro ao criar uma lista de IDS da tabela {TABLE_MMR_HISTORY}: {e}')

	else:
		raise ValueError(f'A tabela {TABLE_MMR_HISTORY} não foi encontrada!')

def _make_stats_ids_list():
	if not table_exists(TABLE_MATCH_STATS):
		logging.info(f'Criando a tabela {TABLE_MATCH_STATS}')
		create_table_match_stats()

	try:
		match_stats_id = create_ids_list(TABLE_MATCH_STATS)
		return match_stats_id

	except Exception as e:
		raise ValueError(f'Erro ao criar uma lista de IDs da tabela {TABLE_MATCH_STATS}: {e}')

def _make_missing_ids_list(mmr_ids, match_stats_id):
	missing_ids = missing_ids_list(mmr_ids, match_stats_id)
	
	return missing_ids

def _check_if_empty(missing_ids):
	missing_ids = to_list(missing_ids)

	if list_is_empty(missing_ids):
		save_empty_file()
		ids_empty = True
		return bool(ids_empty)
	else:
		ids_empty = False
		return bool(ids_empty)

def _save_json(missing_ids):
	missing_ids = to_list(missing_ids)
	json_stats = save_json_stats(missing_ids)
 
	return json_stats

def _insert_df():
    dataframe = json_to_df(FILTERED_JSON_PATH)
    insert_missing_matches(dataframe)

    return f'Insert na tabela finalizado com sucesso.'

def _delete_tmp():
	tmp_path = FILTERED_JSON_PATH.split("/")[0]
	if os.path.exists(tmp_path):
		try:
			shutil.rmtree(tmp_path)
			return True
		except OSError as e:
			logging.error(f"Erro: {e.filename} - {e.strerror}")
	else:
		return False