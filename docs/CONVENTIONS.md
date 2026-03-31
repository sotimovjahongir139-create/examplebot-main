# Conventions

## Naming

- Files use short, flat, descriptive names.
- Service names should be domain-based when the project grows.
- String keys are constants from `bot/strings/keys.py`.

## Async

- All DB access is async.
- Handlers and services are async.
- Avoid sync wrappers around async work.

## Error Handling

- Let unexpected exceptions surface to logging during early development.
- Add domain-specific handling in services when business rules require it.

## Text and UI

- Use `get_text()` for every user-facing string.
- Build keyboards in `bot/ui/`, never inside handlers.

## Routers

- Define a router per handler module.
- Register routers centrally in `bot/handlers/__init__.py`.

