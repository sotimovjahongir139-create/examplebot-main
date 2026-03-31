# Project Overview

This MVP is a Telegram message-preparation assistant.  
The account owner sends draft text directly to the bot. The bot analyzes the draft, applies minimal corrections only when needed, and returns a spreadsheet-style table image for manual use.

The account owner then manually sends the prepared result to the intended real contact outside the bot.

Important: the bot does not intercept personal outgoing Telegram chats and does not automatically send processed messages to third-party contacts.

## Purpose

Build a reusable, generic assistant that improves draft message quality while preserving meaning and critical details.  
The MVP should be safe, predictable, and implementation-accurate for local bot-chat workflows.

## Core Features

- Accept exact draft text entered by the account owner in the bot chat.
- Analyze and correct grammar, spelling, wording, and clarity only when needed.
- Preserve original meaning.
- Preserve names, quantities, prices, model names, colors, and identifiers unless clearly incorrect.
- Keep the same original language.
- Generate a spreadsheet-style table image.
- Assign an internal sequential ID for each processed bot request.
- Include processing date in `MM/DD/YYYY` format.
- Show feedback buttons after the bot returns the processed result in the bot chat.
- Store feedback selected in the bot chat.
- Allow next message processing even when feedback is skipped.
- Keep logic generic and reusable, without hardcoding a private user role or fixed recipient list.

## Input

- Draft text typed by the account owner in the bot chat.
- Bot chat context.
- Account owner identifier.
- Processing timestamp.

## Processing

1. Capture the exact draft text from the bot chat input.
2. Analyze text quality and apply minimal corrections only when needed.
3. Preserve meaning and factual details unless clearly incorrect.
4. Preserve the original language.
5. Assign an internal sequential message ID for the current bot conversation context.
6. Format the processing date as `MM/DD/YYYY`.
7. Build a spreadsheet-style table image using fixed Uzbek columns:
   - `№`
   - `Mahsulot`
   - `Narxi`
   - `Soni`
   - `Jami`
   and include internal message ID + date.
8. Return the processed result in the same bot chat.
9. Show feedback buttons in the bot chat after returning the result.
10. Store feedback if selected.
11. Continue accepting new drafts regardless of feedback submission status.

## Output

- Stored original draft text.
- Stored corrected text.
- Internal sequential ID for the processed request.
- Date in `MM/DD/YYYY`.
- Spreadsheet-style table image returned in bot chat.
- Feedback buttons shown in bot chat only.
- Stored feedback record when user selects feedback in bot chat.

## MVP Workflow Clarification

- The account owner sends draft text to the bot.
- The bot returns a prepared result.
- The account owner manually sends that result to the real contact outside the bot.

Not in MVP:

- No automatic interception of outgoing personal Telegram messages.
- No automatic sending to third-party contacts.
- No contact-view delivery tracking.
- No client-side feedback collection after manual forwarding.

## Acceptance Criteria

1. The account owner can send draft text directly to the bot.
2. The bot processes the exact user-written draft text.
3. Corrections are applied only when needed.
4. Original meaning is preserved.
5. Names, quantities, prices, model names, colors, and identifiers are preserved unless clearly incorrect.
6. Original language is preserved.
7. The bot generates a spreadsheet-style table image.
8. The image/result includes an internal sequential message ID.
9. The image/result - Include the bot processing date in `MM/DD/YYYY` format.
10. Feedback buttons are shown after the bot returns the processed result in bot chat.
11. Selected feedback is stored only from bot-chat interaction.
12. New messages are still processed when feedback is skipped.
13. Documentation and behavior do not claim automatic third-party message interception.
14. Documentation and behavior do not claim automatic third-party message sending.
15. Documentation and behavior do not claim feedback collection from real clients after manual forwarding.
16. The workflow is generic and reusable, not hardcoded for a single private group.
