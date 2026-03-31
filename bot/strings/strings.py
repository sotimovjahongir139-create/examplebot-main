from bot.strings.keys import (
    FEEDBACK_ERROR,
    FEEDBACK_NEGATIVE,
    FEEDBACK_POSITIVE,
    FEEDBACK_PROMPT,
    FEEDBACK_SAVED,
    HELP,
    HELP_BUTTON,
    PROCESSING_DONE,
    START_BUTTON,
    UNKNOWN_COMMAND,
    WELCOME,
)

STRINGS = {
    "en": {
        WELCOME: "Welcome, {name}! Send any text and I will improve wording only when needed.",
        HELP: (
            "Send your message exactly as you want it delivered. "
            "I will preserve meaning, keep the same language, generate a table image, "
            "and return it for manual sending."
        ),
        UNKNOWN_COMMAND: "Unknown command. Use /help or send plain text to process.",
        START_BUTTON: "Start",
        HELP_BUTTON: "Help",
        PROCESSING_DONE: "Qayta ishlangan xabar ID {message_id} \u2014 {date}",
        FEEDBACK_PROMPT: "Ushbu xabarni baholang:",
        FEEDBACK_POSITIVE: "\U0001F44D",
        FEEDBACK_NEGATIVE: "\U0001F44E",
        FEEDBACK_SAVED: "Fikr saqlandi. Keyingi xabarni yuborishingiz mumkin.",
        FEEDBACK_ERROR: "Bu xabar uchun fikrni saqlab bo'lmadi.",
    },
    "uz": {
        WELCOME: "Xush kelibsiz, {name}! Istalgan matn yuboring, faqat kerak bo'lsa tuzataman.",
        HELP: (
            "Xabarni aynan qanday bo'lsa shunday yuboring. "
            "Ma'noni saqlayman, tilni o'zgartirmayman, jadval uslubidagi rasm yarataman "
            "va uni qo'lda yuborish uchun qaytaraman."
        ),
        UNKNOWN_COMMAND: "Noma'lum buyruq. /help dan foydalaning yoki oddiy matn yuboring.",
        START_BUTTON: "Boshlash",
        HELP_BUTTON: "Yordam",
        PROCESSING_DONE: "Qayta ishlangan xabar ID {message_id} \u2014 {date}",
        FEEDBACK_PROMPT: "Ushbu xabarni baholang:",
        FEEDBACK_POSITIVE: "\U0001F44D",
        FEEDBACK_NEGATIVE: "\U0001F44E",
        FEEDBACK_SAVED: "Fikr saqlandi. Keyingi xabarni yuborishingiz mumkin.",
        FEEDBACK_ERROR: "Bu xabar uchun fikrni saqlab bo'lmadi.",
    },
}
