echo "Alterando permissões das pastas ./data/ e ./backups/"
chmod -R 777 ./backups/

echo "Criando diretório para backups do banco de dados"
mkdir -p ./backups/databases/

PG_USER="postgres"
PG_HOST="localhost"
PG_PORT="5432"
DB_NAME="valorant_stats"
CONTAINER_NAME="postgres"
PG_PASSWORD="postgres"

echo "Verificando container do PostgreSQL..."
CONTAINER_ID=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.ID}}")

if [ -n "$CONTAINER_ID" ]; then
    echo "Container encontrado: $COTAINER_ID"

    echo "Verificando se o banco de dados '$DB_NAME' já existe dentro do container..."

    docker exec -e PGPASSWORD="$PG_PASSWORD" "$CONTAINER_ID" \
        psql -U "$PG_USER" -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" \
        | grep -q 1

    if [ $? -eq 0 ]; then
        echo "O banco de dados '$DB_NAME' já existe."
    else
        echo "Criando o banco de dados '$DB_NAME' dentro do container..."

        docker exec -e PGPASSWORD="$PG_PASSWORD" "$CONTAINER_ID" \
            createdb -U "$PG_USER" "$DB_NAME"

        if [ $? -eq 0 ]; then
            echo "Banco de dados '$DB_NAME' criado com sucesso!"
        else
            echo "Erro ao criar o banco de dados '$DB_NAME'."
        fi
    fi
else
    echo "Erro: Container do banco de dados não encontrado."
    exit 1
fi

echo "Montando imagem de process_data"
./include/images/process_data/build.sh

echo "Tornando o script 'absolute_path.sh' executável"
chmod +x backups/script/absolute_path.sh

echo "Verificando permissões antes de executar absolute_path.sh..."
if [ -x backups/script/absolute_path.sh ]; then
    backups/script/absolute_path.sh
    echo "absolute_path.sh executado com sucesso!"
else
    echo "Erro: absolute_path.sh não tem permissão de execução."
    exit 1
fi
echo "Operação finalizada"