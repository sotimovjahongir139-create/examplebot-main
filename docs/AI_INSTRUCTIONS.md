# AI Instructions

This repository is a reusable aiogram bot boilerplate for team reuse.

## Non-Negotiable Rules

- Keep the existing folder structure unless explicitly approved.
- Handlers stay thin: receive Telegram updates, call services, send responses.
- Services contain business logic and must not depend on Telegram objects.
- All database queries belong in `bot/db/repos.py`.
- All user-facing strings belong in `bot/strings/`.
- Keyboards belong in `bot/ui/`.
- Configuration comes from `bot/config.py`.
- Prefer flat, pragmatic structures over extra abstraction.

## Feature Flow

When adding a feature, move in this order:

1. Add or update the SQLAlchemy model.
2. Add repo functions in `bot/db/repos.py`.
3. Add service logic in `bot/services/`.
4. Add string keys and translations in `bot/strings/`.
5. Add UI builders in `bot/ui/` if needed.
6. Add handler logic in `bot/handlers/`.
7. Add tests for services, handlers, and integration behavior.

## Boundaries

- Do not hardcode text in handlers or services.
- Do not inline keyboards in handlers.
- Do not put raw SQL in services.
- Do not add runtime AI features unless explicitly requested.
