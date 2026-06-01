from datetime import datetime, timedelta

from database import get_daily_breakdown, get_user_ratings, get_weekly_stats

_WEEKDAY_NAMES: dict[str, str] = {
    "0": "Yakshanba",
    "1": "Dushanba",
    "2": "Seshanba",
    "3": "Chorshanba",
    "4": "Payshanba",
    "5": "Juma",
    "6": "Shanba",
}


async def build_user_dashboard_text(user_id: int) -> str:
    try:
        rows = await get_user_ratings(user_id)
    except Exception:
        return "📊 Sizning baholash statistikangiz\n\nXatolik yuz berdi."

    if not rows:
        return "📊 Sizning baholash statistikangiz\n\nHali baho bermagansiz."

    total = len(rows)
    avg = sum(r["rating"] for r in rows) / total

    lines = [
        "📊 Sizning baholash statistikangiz",
        "",
        f"⭐ O'rtacha baho: {avg:.1f} / 5.0",
        f"📝 Jami baholar: {total} ta",
        "",
        "📈 So'nggi baholar:",
    ]

    for r in rows[:10]:
        try:
            dt = datetime.strptime(r["rated_at"], "%Y-%m-%d %H:%M:%S")
            dt_str = dt.strftime("%d.%m.%Y")
        except (ValueError, TypeError):
            dt_str = str(r["rated_at"])[:10]
        lines.append(f"- [{dt_str}] ⭐{r['rating']}")

    return "\n".join(lines)


async def build_dashboard_text() -> str:
    try:
        rows = await get_weekly_stats()
        daily = await get_daily_breakdown()
    except Exception:
        return "📊 Haftalik hisobot\n\nXatolik yuz berdi."

    now = datetime.now()
    week_start = now - timedelta(days=6)
    date_range = f"{week_start.strftime('%d.%m')} – {now.strftime('%d.%m')}"

    if not rows:
        return f"📊 Haftalik hisobot ({date_range})\n\nMa'lumot yo'q."

    total = len(rows)
    avg = sum(r["rating"] for r in rows) / total
    positive = sum(1 for r in rows if r["rating"] >= 4)
    medium = sum(1 for r in rows if r["rating"] == 3)
    negative = sum(1 for r in rows if r["rating"] <= 2)

    lines = [
        f"📊 Haftalik hisobot ({date_range})",
        "",
        f"⭐ O'rtacha baho: {avg:.1f} / 5.0",
        f"📝 Jami baholar: {total} ta",
    ]

    if daily:
        busiest = max(daily, key=lambda x: x["count"])
        day_name = _WEEKDAY_NAMES.get(busiest["weekday_num"], busiest["day"])
        lines.append(f"📅 Eng faol kun: {day_name} ({busiest['count']} ta)")

    lines += ["", "📈 Kunlik taqsimot:"]

    max_count = max((d["count"] for d in daily), default=1)
    for d in daily:
        day_name = _WEEKDAY_NAMES.get(d["weekday_num"], d["day"])
        bar_len = int(d["count"] / max_count * 8)
        bar = "█" * bar_len + "░" * (8 - bar_len)
        lines.append(f"{day_name:<12} {bar}  {d['count']} ta | o'rtacha: {d['avg_rating']:.1f}")

    pct_pos = int(positive / total * 100)
    pct_med = int(medium / total * 100)
    pct_neg = int(negative / total * 100)

    lines += [
        "",
        f"😊 Ijobiy (4–5 ⭐): {positive} ta ({pct_pos}%)",
        f"😐 O'rta  (3 ⭐):   {medium} ta ({pct_med}%)",
        f"😟 Salbiy (1–2 ⭐): {negative} ta ({pct_neg}%)",
    ]

    return "\n".join(lines)
