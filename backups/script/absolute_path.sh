FULL_PATH=$(pwd)
DATA_PATH="$FULL_PATH/tmp"
DAGS_PATH="$FULL_PATH/dags"

if [ ! -d "$DAGS_PATH" ]; then
    echo "A pasta 'dags' não foi encontrada."
fi

ENV_FILE="$DAGS_PATH/.env"

if grep -q "^DATA_PATH=" "$ENV_FILE" 2>/dev/null; then
    sed -i "s|^DATA_PATH=.*|DATA_PATH=$DATA_PATH|" "$ENV_FILE"
else
    echo "DATA_PATH=$DATA_PATH" >> "$ENV_FILE"
fi

echo "O caminho absoluto salvo no arquivo $ENV_FILE"