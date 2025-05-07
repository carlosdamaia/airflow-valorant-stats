PG_USER="postgres"
PG_HOST="localhost"
PG_PORT="5432"
BACKUP_DIR="/backups/databases"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Diretório $BACKUP_DIR não encontrado!"
    exit 1
fi

for FILE in "$BACKUP_DIR"/*.sql; do
    if [ -f "$FILE" ]; then
        DB_NAME=$(basename "$FILE" .sql)

        echo "Restaurando o arquivo $FILE para o banco de dados $DB_NAME..."

        createdb -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" "$DB_NAME" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "Aviso: O banco de dados $DB_NAME já existe ou houve um erro ao criá-lo."
        fi

        psql -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" -d "$DB_NAME" -f "$FILE"
        if [ $? -eq 0 ]; then
            echo "Restauração do banco $DB_NAME concluída com sucesso!"
        else
            echo "Erro ao restaurar o banco $DB_NAME a partir de $FILE!"
        fi
    else
        echo "Nenhum arquivo .sql encontrado no diretório $BACKUP_DIR!"
    fi
done

echo "Restauração concluída!"