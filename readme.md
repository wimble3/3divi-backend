# Video processing

### Структура проекта

1. **app/**: содержит api, management-команды, медиафайлы, файлы миграций, графическую оболочку swagger
2. **libs/**: для сторонних библиотек, для удобства вынесены за пределы app
3. **localstack/**: локальное хранилище s3
4. **local.conf** файл содержит конфигурируемые переменные, которые начитываются в **setting.py** файле
5. ***.Dockerfile** файлы
6. **manage.py** файл учавствует в management-командах, регистрирует cli blueprints
7. **docker-compose.local.yaml** файл
8. **other** ignore-файлы, конфигурационные файлы


### Локальный запуск
1. **Команда**: docker compose -f docker-compose.local.yml up -d --build
2. **Команда**: docker login, если потребуется
3. **Повторить** первый шаг *если был сделан второй*
4. **Логи** смотреть через services PyCharm или командой: docker logs --follow <container_name>
5. **API doc** будет доступен по адресу http://localhost:5000/api/docs/
6. **Swagger yaml** будет доступен по адресу http://localhost:5000/api/swagger/
7. **pgadmin** будет доступен по адресу http://localhost:5052/ || Логины и пароли не спрятаны, их можно увидеть в контейнере