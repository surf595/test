# pdm_bot — psychodynamic Telegram RAG assistant

`pdm_bot` — психодинамически ориентированный Telegram-ассистент, который отвечает с опорой на локальную библиотеку профессиональных материалов.

Ключевой фокус продукта:
- прояснение понятий;
- source-grounded ответы по корпусу документов;
- супервизионно-осторожный стиль рассуждений;
- разделение фактов, гипотез и интерпретаций.

> Важно: ассистент не заменяет психотерапию, клиническую диагностику и решение специалиста.

## Архитектура

### Основные компоненты
- **Telegram transport layer**: `pdm_bot/app/telegram_handlers.py`.
- **Service layer**:
  - `pdm_bot/app/services/conversation_service.py`
  - `pdm_bot/app/services/retrieval_service.py`
  - `pdm_bot/app/services/indexing_service.py`
  - `pdm_bot/app/services/user_settings_service.py`
- **Data layer**: `pdm_bot/app/db.py` (SQLite: users/messages/sync/jobs/document_index).
- **Retrieval layer**: `pdm_bot/app/retrieval.py` (Qdrant + hybrid scoring).
- **Indexing layer**: `pdm_bot/app/indexing.py` + `pdm_bot/app/documents.py`.
- **LLM layer**: `pdm_bot/app/llm.py` (OpenAI embeddings/chat).
- **Bootstrap**: `pdm_bot/app/main.py`.

### Поток запроса
1. Пользователь пишет сообщение в Telegram.
2. `handle_message` делегирует orchestration в `conversation_service`.
3. Выполняется retrieval (Qdrant + keyword score), строится context block.
4. Формируется психодинамический system prompt.
5. LLM генерирует ответ.
6. Ответ и история сохраняются в SQLite, пользователю отправляется сообщение (частями при необходимости).

## Требования
- Python 3.10+
- Qdrant (локально или удалённо)
- OpenAI API key
- `python-telegram-bot`, `openai`, `qdrant-client`, `python-dotenv`, `python-docx`, `pypdf`

## Установка
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install python-telegram-bot qdrant-client openai python-dotenv python-docx pypdf
```

## Конфигурация
```bash
cp .env.example .env
```

Обязательные переменные:
- `TELEGRAM_TOKEN`
- `OPENAI_API_KEY`

Остальные параметры (Qdrant, индексация, context limits) — в `.env.example`.

## Локальная библиотека (`docs/`)
- Поддерживаемые форматы: `.txt`, `.md`, `.pdf`, `.docx`.
- Индексация инкрементальная: учитываются `sha1` и `mtime`.
- PDF chunk-ы сохраняют ссылки на страницы (`page_start`/`page_end`).

## Запуск
```bash
python -m pdm_bot.app.main
```

## Команды Telegram
- Базовые: `/start`, `/help`, `/diagnose`, `/tone`, `/depth`, `/mode`, `/stats`
- Индексация: `/reindex`, `/index_status`
- Операционные: `/health`, `/collections`, `/jobs`, `/config`, `/debug`, `/sources`

> Owner-only guard сохранён для чувствительных команд (`/reindex`, `/health`, `/collections`, `/debug`).

## Диагностика и типичные проблемы
1. **`TELEGRAM_TOKEN не найден`** — проверьте `.env` и переменные окружения.
2. **Qdrant недоступен** — проверьте `QDRANT_HOST`, `QDRANT_PORT`, статус сервиса.
3. **Ошибка OpenAI** — проверьте `OPENAI_API_KEY` и сетевой доступ.
4. **Пустой retrieval** — проверьте, что библиотека проиндексирована (`/reindex`, `/index_status`).

Команда `/health` показывает агрегированный runtime-статус (`.env`, токены, docs, Qdrant) и результат автосинхронизации.

## Проверки
```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python -m compileall pdm_bot
node --check app.js
```
