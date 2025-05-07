BACKUP_DIR="/usr/local/airflow/backups/databases"

PG_USER="postgres"
PG_HOST="postgres"
PG_PORT="5432"
PGPASSWORD="postgres"
DATABASES=("valorant_stats" "postgres")

for DB in "${DATABASES[@]}"; do
    echo "Realizando backup do banco de dados: $DB"
    export PGPASSWORD="$PGPASSWORD" && pg_dump -U $PG_USER -h $PG_HOST -p $PG_PORT $DB > $BACKUP_DIR/${DB}.sql
    if [ $? -eq 0 ]; then
        echo "Backup do banco $DB realizado com sucesso!"
    else
        echo "Erro ao realizar backup do banco $DB!"
    fi
done

echo "Backup concluído em $BACKUP_DIR"