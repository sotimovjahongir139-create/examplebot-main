import re
from dataclasses import dataclass
from datetime import date
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import repos

_MULTISPACE_RE = re.compile(r"[ \t]{2,}")
_NUMERIC_RE = re.compile(r"^\d+(?:[.,]\d+)?$")
_DIGIT_CAPTURE_RE = re.compile(r"\d+(?:[.,]\d+)?")
_CALC_LINE_RE = re.compile(
    r"^\s*(?:\d+\s*[.)-]?\s*)?(\d+(?:[.,]\d+)?)\s*[xX*хХ×]\s*(\d+(?:[.,]\d+)?)\s*=\s*(\d+(?:[.,]\d+)?)\s*$"
)
_CALC_FRAGMENT_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[xX*хХ×]\s*(\d+(?:[.,]\d+)?)\s*=\s*(\d+(?:[.,]\d+)?)")
_SUMMARY_PATTERNS: tuple[tuple[str, str], ...] = (
    ("jami", "jami"),
    ("berilgan pul", "berildi"),
    ("berildi", "berildi"),
    ("eski qarz", "eski"),
    ("eski", "eski"),
    ("yangi qarz", "yangi"),
    ("yangi", "yangi"),
)


@dataclass(frozen=True)
class ProcessedMessageResult:
    db_record_id: int
    contact_id: int
    message_id: int
    language_code: str
    original_text: str
    corrected_text: str
    send_date_mmddyyyy: str
    table_image_bytes: bytes


@dataclass(frozen=True)
class BusinessRow:
    model: str
    rang: str
    soni: str
    narxi: str
    summa: str


@dataclass(frozen=True)
class ParsedBusinessTable:
    title: str
    rows: list[BusinessRow]
    summary_rows: list[BusinessRow]


def correct_text(text: str) -> str:
    # Keep corrections minimal to preserve symbols, punctuation, and meaning.
    cleaned_lines = []
    for line in text.splitlines():
        normalized = _MULTISPACE_RE.sub(" ", line.strip())
        if normalized:
            cleaned_lines.append(normalized)
    return "\n".join(cleaned_lines)


def _split_line_tokens(line: str) -> list[str]:
    if "|" in line:
        return [part.strip() for part in line.split("|") if part.strip()]
    if "\t" in line:
        return [part.strip() for part in line.split("\t") if part.strip()]
    return [part.strip() for part in line.split(" ") if part.strip()]


def _looks_like_header_line(line: str) -> bool:
    lowered = line.lower()
    return (
        ("product" in lowered and "qty" in lowered and "total" in lowered)
        or ("model" in lowered and "rang" in lowered and "soni" in lowered and "narxi" in lowered and "summa" in lowered)
        or ("mahsulot" in lowered and "narxi" in lowered and "soni" in lowered and "jami" in lowered)
    )


def _extract_summary_value(text: str) -> str:
    numbers = _DIGIT_CAPTURE_RE.findall(text)
    return numbers[-1] if numbers else ""


def _parse_summary_row(line: str) -> BusinessRow | None:
    lowered = line.lower().strip()
    normalized = lowered.replace(":", " ").strip()
    for source, label in _SUMMARY_PATTERNS:
        if normalized == source or normalized.startswith(f"{source} "):
            return BusinessRow(model=label, rang="", soni="", narxi="", summa=_extract_summary_value(line))
    return None


def _strip_product_prefix(line: str) -> str:
    content = line.strip()
    lowered = content.lower()
    if lowered.startswith("tovar:"):
        content = content.split(":", 1)[1].strip()
    content = re.sub(r"^\d+\s*[.)]\s*", "", content)
    return content.strip()


def _parse_product_line(line: str) -> BusinessRow | None:
    content = _strip_product_prefix(line)
    if not content or "=" in content:
        return None
    tokens = _split_line_tokens(content)
    if len(tokens) < 2:
        return None
    if all(_NUMERIC_RE.match(token) for token in tokens):
        return None
    rang = tokens[-1]
    if _NUMERIC_RE.match(rang):
        return None
    if any(marker in rang for marker in ("=", "x", "X", "*")):
        return None
    model = " ".join(tokens[:-1]).strip()
    if not model:
        return None
    return BusinessRow(model=model, rang=rang, soni="", narxi="", summa="")


def _parse_calculation_row(line: str) -> tuple[str, str, str] | None:
    match = _CALC_LINE_RE.match(line)
    if match:
        return match.group(1), match.group(2), match.group(3)
    # Fallback for noisy lines that still contain a valid expression.
    fragment = _CALC_FRAGMENT_RE.search(line)
    if fragment:
        return fragment.group(1), fragment.group(2), fragment.group(3)
    return None


def parse_business_table(text: str) -> ParsedBusinessTable:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ParsedBusinessTable(
            title="Prepared Message",
            rows=[BusinessRow(model="Prepared Message", rang="", soni="", narxi="", summa="")],
            summary_rows=[
                BusinessRow(model="jami", rang="", soni="", narxi="", summa=""),
                BusinessRow(model="berildi", rang="", soni="", narxi="", summa=""),
                BusinessRow(model="eski", rang="", soni="", narxi="", summa=""),
                BusinessRow(model="yangi", rang="", soni="", narxi="", summa=""),
            ],
        )

    product_rows: list[BusinessRow] = []
    calc_rows: list[tuple[str, str, str]] = []
    parsed_summaries: dict[str, BusinessRow] = {}
    title_candidates: list[str] = []
    parsed_input_date: str | None = None

    for line in lines:
        # Skip header-like raw lines from user text.
        if _looks_like_header_line(line):
            continue
        if line.lower().startswith("sana:"):
            parsed_input_date = line.strip()
            continue
        summary_row = _parse_summary_row(line)
        if summary_row is not None:
            parsed_summaries[summary_row.model] = summary_row
            continue
        calc = _parse_calculation_row(line)
        if calc is not None:
            calc_rows.append(calc)
            continue
        row = _parse_product_line(line)
        if row is not None:
            product_rows.append(row)
            continue
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered in {"tovar", "tovar:", "mahsulot", "mahsulot:"}:
            title_candidates.append(line)
            continue
        # Ignore "Tovar: 1400" or other pure-number entries that should not pollute model/rang.
        tail = _strip_product_prefix(line)
        tail_tokens = _split_line_tokens(tail)
        if tail_tokens and all(_NUMERIC_RE.match(token) for token in tail_tokens):
            continue
        title_candidates.append(line)

    parsed_rows: list[BusinessRow] = []
    # Prefer product-anchored rows to avoid empty model cells when extra calculation lines exist.
    row_count = len(product_rows) if product_rows else len(calc_rows)
    for idx in range(row_count):
        product = product_rows[idx] if idx < len(product_rows) else BusinessRow(model="", rang="", soni="", narxi="", summa="")
        soni, narxi, summa = calc_rows[idx] if idx < len(calc_rows) else ("", "", "")
        parsed_rows.append(BusinessRow(model=product.model, rang=product.rang, soni=soni, narxi=narxi, summa=summa))

    if parsed_input_date:
        title = parsed_input_date
    elif title_candidates:
        title = title_candidates[0]
    elif parsed_rows:
        title = parsed_rows[0].model
    else:
        title = lines[0]

    if not parsed_rows:
        parsed_rows = [BusinessRow(model=lines[0], rang="", soni="", narxi="", summa="")]

    summary_rows = []
    for label in ("jami", "berildi", "eski", "yangi"):
        summary_rows.append(parsed_summaries.get(label, BusinessRow(model=label, rang="", soni="", narxi="", summa="")))

    return ParsedBusinessTable(title=title, rows=parsed_rows, summary_rows=summary_rows)


def ensure_visible_fallback_table(parsed: ParsedBusinessTable, fallback_text: str) -> ParsedBusinessTable:
    safe_title = (parsed.title or fallback_text or "Prepared Message").strip()[:120]
    rows = list(parsed.rows)
    summary_rows = list(parsed.summary_rows)

    if not rows:
        rows = [BusinessRow(model=(fallback_text or "Prepared Message"), rang="", soni="", narxi="", summa="")]

    has_visible_text = any((row.model or row.rang or row.soni or row.narxi or row.summa).strip() for row in rows)
    if not has_visible_text:
        rows = [BusinessRow(model=(fallback_text or "Prepared Message"), rang="", soni="", narxi="", summa="")]

    if not summary_rows:
        summary_rows = [
            BusinessRow(model="jami", rang="", soni="", narxi="", summa=""),
            BusinessRow(model="berildi", rang="", soni="", narxi="", summa=""),
            BusinessRow(model="eski", rang="", soni="", narxi="", summa=""),
            BusinessRow(model="yangi", rang="", soni="", narxi="", summa=""),
        ]

    return ParsedBusinessTable(title=safe_title, rows=rows, summary_rows=summary_rows)


def _load_font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "segoeui.ttf", "tahoma.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_business_table_image(
    parsed: ParsedBusinessTable,
    message_id: int,
    date_mmddyyyy: str,
) -> bytes:
    title_font = _load_font(28)
    header_font = _load_font(20)
    cell_font = _load_font(20)
    meta_font = _load_font(18)

    cols = ["Model", "Rang", "Soni", "Narxi", "Summa"]
    col_w = [300, 210, 120, 140, 160]
    row_h = 52
    left = 36
    top_title = 26
    table_top = 110
    table_width = sum(col_w)
    width = left + table_width + 36
    all_rows = list(parsed.rows) + list(parsed.summary_rows)
    rows_count = 1 + len(all_rows)
    table_height = rows_count * row_h
    height = table_top + table_height + 54

    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Small ID label at top-left.
    draw.text((left, 6), f"id - {message_id}", fill=(0, 0, 0), font=meta_font)
    draw.text((left, top_title), parsed.title, fill=(0, 0, 0), font=title_font)

    x_positions = [left]
    for w in col_w:
        x_positions.append(x_positions[-1] + w)

    # Grid lines.
    for i in range(rows_count + 1):
        y = table_top + (i * row_h)
        draw.line((x_positions[0], y, x_positions[-1], y), fill=(0, 0, 0), width=1)
    for x in x_positions:
        draw.line((x, table_top, x, table_top + table_height), fill=(0, 0, 0), width=1)

    # Header row.
    for c_i, col_name in enumerate(cols):
        draw.text((x_positions[c_i] + 8, table_top + 14), col_name, fill=(0, 0, 0), font=header_font)

    # Data rows.
    for r_i, row in enumerate(all_rows, start=1):
        y = table_top + (r_i * row_h) + 14
        values = [row.model, row.rang, row.soni, row.narxi, row.summa]
        for c_i, value in enumerate(values):
            max_chars = max(1, (col_w[c_i] - 16) // 10)
            clipped = value if len(value) <= max_chars else f"{value[: max_chars - 3]}..."
            draw.text((x_positions[c_i] + 8, y), clipped, fill=(0, 0, 0), font=cell_font)

    # Date at bottom-right.
    date_bbox = draw.textbbox((0, 0), date_mmddyyyy, font=meta_font)
    date_width = date_bbox[2] - date_bbox[0]
    draw.text((x_positions[-1] - date_width, table_top + table_height + 12), date_mmddyyyy, fill=(0, 0, 0), font=meta_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


async def process_owner_message(
    session: AsyncSession,
    owner_telegram_id: int,
    contact_id: int,
    original_text: str,
    language_code: str,
) -> ProcessedMessageResult:
    counter = await repos.get_contact_counter(session, contact_id)
    if counter is None:
        counter = await repos.create_contact_counter(session, contact_id)

    current_message_id = counter.next_message_id
    counter.next_message_id += 1

    corrected_text = correct_text(original_text)
    send_date = date.today()
    record = await repos.create_processed_message(
        session=session,
        contact_id=contact_id,
        owner_telegram_id=owner_telegram_id,
        message_id=current_message_id,
        language_code=language_code,
        original_text=original_text,
        corrected_text=corrected_text,
        send_date=send_date,
    )
    await session.commit()

    send_date_mmddyyyy = send_date.strftime("%m/%d/%Y")
    parsed = parse_business_table(corrected_text)
    parsed = ensure_visible_fallback_table(parsed, corrected_text or original_text)
    image_bytes = render_business_table_image(parsed, current_message_id, send_date_mmddyyyy)
    return ProcessedMessageResult(
        db_record_id=record.id,
        contact_id=contact_id,
        message_id=current_message_id,
        language_code=language_code,
        original_text=original_text,
        corrected_text=corrected_text,
        send_date_mmddyyyy=send_date_mmddyyyy,
        table_image_bytes=image_bytes,
    )


async def store_feedback(
    session: AsyncSession,
    processed_message_pk: int,
    user_telegram_id: int,
    feedback_value: str,
) -> bool:
    processed_message = await repos.get_processed_message_by_pk(
        session=session,
        processed_message_pk=processed_message_pk,
    )
    if processed_message is None:
        return False

    await repos.create_feedback(
        session=session,
        processed_message_id=processed_message_pk,
        user_telegram_id=user_telegram_id,
        feedback_value=feedback_value,
    )
    await session.commit()
    return True
