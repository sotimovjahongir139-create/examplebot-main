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
