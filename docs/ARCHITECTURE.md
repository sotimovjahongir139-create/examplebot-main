# Architecture

## Folder Map

- `bot/core/`: bot startup, shutdown, dispatcher, router registration.
- `bot/handlers/`: Telegram update entrypoints only.
- `bot/services/`: business logic without Telegram dependencies.
- `bot/db/`: connection setup, models, repos, startup migrations, Alembic environment.
- `bot/middlewares/`: per-update cross-cutting behavior such as DB session injection.
- `bot/strings/`: string keys, translations, and `get_text()`.
- `bot/ui/`: inline and reply keyboard builders.
- `bot/utils/`: shared support utilities such as logging.
- `tests/`: unit, handler, and integration coverage.
- `docs/`: architecture and AI-facing project guidance.

## Layer Rules

- `handlers -> services -> repos -> models`
- `handlers -> strings`
- `handlers -> ui`
- `core -> middlewares`
- `core -> handlers`

No reverse dependencies should be introduced.

## Data Flow

1. Telegram sends an update to the dispatcher.
2. Middleware injects an async DB session into handler data.
3. A handler validates the update shape and calls a service.
4. The service loads or writes data through repo functions.
5. The handler reads localized text through `get_text()`.
6. The handler sends a Telegram response, optionally with UI helpers.

