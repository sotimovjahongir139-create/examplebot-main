# Aiogram Bot Boilerplate

Production-ready aiogram boilerplate for building Telegram bots with a clean service/repository split.

## Prerequisites

- Python 3.12+
- A Telegram bot token

## Installation

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
```

### Windows (Command Prompt / PowerShell)

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
copy .env.example .env
```

Set `BOT_TOKEN` in `.env`, then run:

```bash
python main.py
```

## Database

- SQLite is the default for local development.
- Set `DATABASE_URL` to a PostgreSQL `asyncpg` URL for production.
- Startup migrations create SQLite tables automatically.
- Alembic is reserved for managed schema changes.

## Testing

```bash
pytest
```

## Commands

- `/start` create or load current user
- `/help` show usage hints

## Message Processing Flow

- Send any plain text message.
- Bot keeps original language and applies minimal grammar/clarity fixes only when needed.
- Bot assigns an internal sequential message ID for the current bot conversation context.
- Bot sends a spreadsheet-style table image containing:
  - original text
  - corrected text
  - message ID
  - date in `MM/DD/YYYY`
- Bot shows feedback buttons after it returns the processed result in bot chat.
- Feedback is stored, but next messages are accepted even without feedback.
- Account owner manually sends the prepared result to the intended real contact outside the bot.
- Bot does not automatically intercept or send third-party Telegram messages.
- Feedback collection in this MVP works only inside the bot chat (not from real clients after manual forwarding).

## Deployment

- `docker-compose.yml` is intended for local containerized development.
- `docker-compose.prod.yml` includes PostgreSQL and restart policies for production-style setups.
