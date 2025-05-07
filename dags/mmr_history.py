from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from datetime import datetime
from include.mmr_history.tasks import _get_mmr_history, _filter_dataframe, _db_insert
from include.helpers.functions import _test_database_conn

@dag(
    start_date=datetime(2024, 11, 24),
    schedule="@hourly",
    catchup=False,
    tags=["valorant"]
)

def mmr_history():
            
    get_mmr_history = PythonOperator(
        task_id='get_mmr_history',
        python_callable=_get_mmr_history
    )
    
    filter_dataframe = PythonOperator(
        task_id='filter_dataframe',
        python_callable=_filter_dataframe,
        op_kwargs={
            'mmr_history': '{{ task_instance.xcom_pull(task_ids="get_mmr_history") }}'
        }
    )
    
    test_database_conn = PythonOperator(
        task_id='test_database_conn',
        python_callable=_test_database_conn
    )
    
    db_insert = PythonOperator(
        task_id='db_insert',
        python_callable=_db_insert,
        op_kwargs={
            'df': '{{ task_instance.xcom_pull(task_ids="filter_dataframe") }}'
        }
    )

    get_mmr_history >> filter_dataframe >> test_database_conn >> db_insert

mmr_history()