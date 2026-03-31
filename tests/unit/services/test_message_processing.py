import pytest

from bot.services.message_processing import (
    correct_text,
    ensure_visible_fallback_table,
    parse_business_table,
    process_owner_message,
)


def test_correct_text_keeps_symbols_and_minimally_normalizes() -> None:
    assert correct_text("hello,world") == "hello,world"
    assert correct_text("  item  A   10  pcs ") == "item A 10 pcs"


def test_parse_business_table_builds_rows_from_repeated_lines() -> None:
    parsed = parse_business_table(
        "Sana: 15.03.2026\n"
        "Tovar: 1-PVX 229110 qora\n"
        "2-PVX 0323 qora\n"
        "1. 450x2=900\n"
        "2. 250x2=500\n"
        "Jami: 1400\n"
        "Eski qarz: 6430\n"
        "Tovar: 1400\n"
        "Berilgan pul: 0\n"
        "Yangi qarz: 7830"
    )

    assert parsed.title == "Sana: 15.03.2026"
    assert parsed.rows[0].model == "1-PVX 229110"
    assert parsed.rows[0].rang == "qora"
    assert parsed.rows[0].soni == "450"
    assert parsed.rows[0].narxi == "2"
    assert parsed.rows[0].summa == "900"
    assert parsed.rows[1].model == "2-PVX 0323"
    assert parsed.rows[1].rang == "qora"
    assert parsed.rows[1].soni == "250"
    assert parsed.rows[1].narxi == "2"
    assert parsed.rows[1].summa == "500"
    assert parsed.summary_rows[0].model == "jami"
    assert parsed.summary_rows[0].summa == "1400"
    assert parsed.summary_rows[1].model == "berildi"
    assert parsed.summary_rows[1].summa == "0"
    assert parsed.summary_rows[2].model == "eski"
    assert parsed.summary_rows[2].summa == "6430"
    assert parsed.summary_rows[3].model == "yangi"
    assert parsed.summary_rows[3].summa == "7830"
    assert all("x=" not in row.rang.lower() for row in parsed.rows)
    assert all(row.narxi == "" for row in parsed.summary_rows)


def test_parser_does_not_create_empty_model_for_extra_calc_lines() -> None:
    parsed = parse_business_table(
        "Tovar: 1-PVX 229110 qora\n"
        "1. 450x2=900\n"
        "2. 250x2=500\n"
        "Eski qarz: 6430"
    )

    assert len(parsed.rows) == 1
    assert parsed.rows[0].model == "1-PVX 229110"
    assert parsed.rows[0].rang == "qora"
    assert parsed.rows[0].soni == "450"
    assert parsed.rows[0].narxi == "2"
    assert parsed.rows[0].summa == "900"
    assert parsed.summary_rows[2].model == "eski"
    assert parsed.summary_rows[2].summa == "6430"


def test_fallback_table_for_simple_short_text() -> None:
    parsed = parse_business_table("Start")
    parsed = ensure_visible_fallback_table(parsed, "Start")

    assert parsed.title == "Start"
    assert parsed.rows[0].model == "Start"
    assert parsed.rows[0].rang == ""
    assert parsed.rows[0].soni == ""
    assert parsed.rows[0].narxi == ""
    assert parsed.rows[0].summa == ""
    assert [row.model for row in parsed.summary_rows] == ["jami", "berildi", "eski", "yangi"]


@pytest.mark.asyncio
async def test_process_owner_message_increments_counter_per_contact(db_session) -> None:
    first = await process_owner_message(
        session=db_session,
        owner_telegram_id=1,
        contact_id=500,
        original_text="hello,world",
        language_code="en",
    )
    second = await process_owner_message(
        session=db_session,
        owner_telegram_id=1,
        contact_id=500,
        original_text="second text",
        language_code="en",
    )
    other_contact = await process_owner_message(
        session=db_session,
        owner_telegram_id=1,
        contact_id=999,
        original_text="another contact",
        language_code="en",
    )

    assert first.message_id == 1
    assert second.message_id == 2
    assert other_contact.message_id == 1
