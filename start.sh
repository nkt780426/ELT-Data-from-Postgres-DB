# Làm cho dự án đơn giản hơn, không cần phải docker-compose up init-airflow -d mỗi lần nữa
docker compose up init-airflow

sleep 5

docker compose up -d

sleep 5

cd airbyte

if [ -f "docker-compose.yml" ]; then
    docker compose up -d
else
    ./run-ab-platform.sh
fi