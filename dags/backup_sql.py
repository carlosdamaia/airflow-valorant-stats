from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime

@dag(
    start_date=datetime(2024, 12, 4),
    schedule="@hourly",
    catchup=False,
    tags=["backup", "update_repo"]
)

def backup_sql():
    
    wait_match_stats_end = ExternalTaskSensor(
        task_id='wait_match_stats_end',
        external_dag_id='match_stats',
        timeout=300,
        poke_interval=15,
        mode='poke'
    )
    
    backup_task = BashOperator(
        task_id='backup_task',
        bash_command=f"bash -c 'cd /usr/local/airflow/backups/script && ./copy_databases.sh'"
    )
            
    wait_match_stats_end >> backup_task
    
backup_sql()