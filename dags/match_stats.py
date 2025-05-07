import os
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator
from datetime import datetime
from include.match_stats.tasks import _check_if_empty, _make_mmr_history_list, _make_stats_ids_list, _make_missing_ids_list, _save_json, _insert_df, _delete_tmp
from include.helpers.functions import _test_database_conn
from include.helpers.airflow_var import (
    NAME, RAW_JSON_PATH, FILTERED_JSON_PATH, 
    TABLE_MMR_HISTORY, DB_URL_DOCKER
)
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from dotenv import load_dotenv
import os

load_dotenv()

minio_conn = BaseHook.get_connection('minio')

data_path = os.getenv("DATA_PATH")

@dag(
    start_date=datetime(2024, 11, 24),
    schedule="@hourly",
    catchup=False,
    tags=["valorant"]
)

def match_stats():
    
    wait_mmr_history_end = ExternalTaskSensor(
        task_id='wait_mmr_history_end',
        external_dag_id='mmr_history',
        external_task_id='db_insert',
        timeout=600,
        poke_interval=15,
        mode='poke'
    )
    
    test_database_conn = PythonOperator(
        task_id='test_database_conn',
        python_callable=_test_database_conn
    )
    
    make_mmr_history_list = PythonOperator(
        task_id='make_mmr_history_list',
        python_callable=_make_mmr_history_list
    )

    make_stats_ids_list = PythonOperator(
        task_id='make_stats_ids_list',
        python_callable=_make_stats_ids_list
    )

    make_missing_ids_list = PythonOperator(
        task_id='make_missing_ids_list',
        python_callable=_make_missing_ids_list,
        op_kwargs={
            'mmr_ids': '{{ ti.xcom_pull(task_ids="make_mmr_history_list") }}',
            'match_stats_id': '{{ ti.xcom_pull(task_ids="make_stats_ids_list") }}'
        }
    )
    
    check_if_empty = PythonOperator(
        task_id='check_if_empty',
        python_callable=_check_if_empty,
        op_kwargs={
            'missing_ids': '{{ ti.xcom_pull(task_ids="make_missing_ids_list") }}'
        }
    )
    
    @task.branch(task_id='branch_if')
    def _branch_if(ti=None):
        ids_empty = ti.xcom_pull(task_ids="check_if_empty")
        if ids_empty:
            return None
        else:
            return 'save_json'
    
    save_json = PythonOperator(
        task_id='save_json',
        python_callable=_save_json,
        op_kwargs={
            'missing_ids': '{{ ti.xcom_pull(task_ids="make_missing_ids_list") }}'
        }
    )
            
    process_data = DockerOperator(
        task_id='process_data',
        image='process_data:latest',
        command='python3 process_data.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='host',
        auto_remove='success',
        xcom_all=True,
        retrieve_output=True,
        retrieve_output_path='/tmp/script.out',
        mount_tmp_dir=False,
        mounts=[
            Mount(
                type='bind',
                source=f'{data_path}',
                target='/app/tmp'
            )
        ],
        environment={
            'name': NAME,
            'raw_json_path': RAW_JSON_PATH,
            'filtered_json_path': FILTERED_JSON_PATH,
            'table_mmr_history': TABLE_MMR_HISTORY,
            'db_url': DB_URL_DOCKER,
            'MINIO_ENDPOINT': '127.0.0.1:9000',
            'MINIO_ACCESS_KEY': minio_conn.login,
            'MINIO_SECRET_KEY': minio_conn.password,
        },
        user="0"
    )
    
    insert_df = PythonOperator(
        task_id='insert_df',
        python_callable=_insert_df,
        op_kwargs={
            'file_path': '{{ ti.xcom_pull(task_ids="save_json") }}'
        }
    )
    
    delete_tmp = PythonOperator(
        task_id='delete_tmp',
        python_callable=_delete_tmp,
    )
    
    branch_if = _branch_if()
    
    (
        wait_mmr_history_end >> test_database_conn >> make_mmr_history_list >> make_stats_ids_list >> 
        make_missing_ids_list >> check_if_empty >> branch_if >> save_json >> process_data >> insert_df >> delete_tmp
    )
    
match_stats()