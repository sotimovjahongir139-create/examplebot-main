import aiosqlite
from datetime import datetime, timedelta

DB_PATH = "ratings.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                username TEXT,
                first_name TEXT,
                rating INTEGER,
                rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                week_number INTEGER,
                year INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pending_ratings (
                token TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def create_pending_rating(token: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO pending_ratings (token) VALUES (?)",
            (token,),
        )
        await db.commit()


async def get_pending_rating(token: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM pending_ratings WHERE token = ?",
            (token,),
        )
        row = await cursor.fetchone()
    return dict(row) if row else None


async def mark_rating_used(token: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE pending_ratings SET used = 1 WHERE token = ?",
            (token,),
        )
        await db.commit()


async def save_rating(
    user_id: int,
    username: str | None,
    first_name: str | None,
    rating: int,
) -> None:
    now = datetime.now()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO ratings (user_id, username, first_name, rating, week_number, year)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (str(user_id), username or "", first_name or "", rating, now.isocalendar()[1], now.year),
        )
        await db.commit()


async def get_weekly_stats() -> list[dict]:
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM ratings WHERE rated_at >= ? ORDER BY rated_at",
            (cutoff,),
        )
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_user_ratings(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM ratings WHERE user_id = ? ORDER BY rated_at DESC LIMIT 20",
            (str(user_id),),
        )
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_monthly_stats(year: int, month: int) -> dict:
    y_str = str(year)
    m_str = f"{month:02d}"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT COUNT(DISTINCT user_id) AS unique_users FROM ratings"
            " WHERE strftime('%Y', rated_at) = ? AND strftime('%m', rated_at) = ?",
            (y_str, m_str),
        )
        row = await cur.fetchone()
        unique_users: int = dict(row)["unique_users"] if row else 0

        cur2 = await db.execute(
            "SELECT rating, COUNT(*) AS cnt FROM ratings"
            " WHERE strftime('%Y', rated_at) = ? AND strftime('%m', rated_at) = ?"
            " GROUP BY rating ORDER BY rating DESC",
            (y_str, m_str),
        )
        breakdown = [dict(r) for r in await cur2.fetchall()]

    total = sum(r["cnt"] for r in breakdown)
    avg = sum(r["rating"] * r["cnt"] for r in breakdown) / total if total else 0.0
    return {"unique_users": unique_users, "breakdown": breakdown, "total": total, "avg": avg}


async def get_monthly_raters(year: int, month: int) -> dict[int, list[str]]:
    """Returns {star: [display_name, ...]} for every rating in the given month."""
    y_str = str(year)
    m_str = f"{month:02d}"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT rating, username, user_id FROM ratings"
            " WHERE strftime('%Y', rated_at) = ? AND strftime('%m', rated_at) = ?"
            " ORDER BY rating DESC, rated_at",
            (y_str, m_str),
        )
        rows = [dict(r) for r in await cursor.fetchall()]

    result: dict[int, list[str]] = {5: [], 4: [], 3: [], 2: [], 1: []}
    for r in rows:
        name = f"@{r['username']}" if r["username"] else f"id:{r['user_id']}"
        result[r["rating"]].append(name)
    return result


async def get_daily_breakdown() -> list[dict]:
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT
                strftime('%w', rated_at) AS weekday_num,
                strftime('%Y-%m-%d', rated_at) AS day,
                COUNT(*) AS count,
                AVG(rating) AS avg_rating
            FROM ratings
            WHERE rated_at >= ?
            GROUP BY day
            ORDER BY day
            """,
            (cutoff,),
        )
        rows = await cursor.fetchall()
    return [dict(r) for r in rows]
