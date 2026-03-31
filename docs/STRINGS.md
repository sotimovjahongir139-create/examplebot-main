# Strings

## Add a String Key

1. Add a constant to `bot/strings/keys.py`.
2. Add translations for every supported language in `bot/strings/strings.py`.
3. Access the string with `get_text(KEY, lang=...)`.

## Add a Language

1. Add a new top-level language key to `STRINGS`.
2. Provide values for every existing string key.
3. Pass the language code into `get_text()`.

## Helper Rules

- `get_text()` falls back to the default language when a translation is missing.
- Keep interpolation placeholders aligned across languages.

