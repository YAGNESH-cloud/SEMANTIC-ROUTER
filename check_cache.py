from app.database import get_connection

with get_connection() as connection:
    rows = connection.execute(
        "SELECT id, question, expires_at FROM cache_entries ORDER BY id DESC"
    ).fetchall()

print("Cached entries:", len(rows))

for row in rows:
    print(dict(row))
