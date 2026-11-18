# loki-logging-demo

Учебный проект: централизованное логирование FastAPI-приложения в **Loki** с визуализацией в **Grafana**.

## Стек
- `loki` — хранилище логов (порт 3100)
- `grafana` — визуализация (порт 3000, admin/admin)
- `app` — FastAPI-приложение, отправляет логи в Loki через HTTP API `/loki/api/v1/push`

## Запуск
```bash
docker compose up -d
docker ps   # все три контейнера должны быть в статусе Up
```

## Проверка
1. Grafana: http://<IP>:3000 (admin/admin, пароль меняется при первом входе)
2. Connections → Data sources → Loki (URL: `http://loki:3100` — общая docker-сеть)
3. Дашборд **My App Logs**: таблица логов `{app="my_app"}` + pie chart
   `sum by (level) (count_over_time({app="my_app"}[5m]))`
4. Приложение: http://<IP>:8095/ — каждый запрос пишет лог; фоновая задача генерирует логи каждые 10 секунд

## Ключевая функция
`send_log_to_loki()` в `app/main.py`: POST JSON с полями `streams[].stream`
(метки: app, level) и `streams[].values` (пары [timestamp_ns, message]).
