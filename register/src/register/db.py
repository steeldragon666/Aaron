"""Database access and migrations.

SQLite, addressed through plain SQL. Two reasons, both worth writing down
because they constrain later choices:

1. **No external dependency of any kind on a client-context path** (CLAUDE.md
   §2). SQLite ships with the interpreter; there is no driver, no server, no
   connection string pointing anywhere.
2. The register is small enough to sit entirely in a 1M context window
   (CONSOLIDATION_BRIEF §0.4), so this store is an audit and query surface, not
   a retrieval engine under load.

The SQL here is ANSI-shaped and the only SQLite-specific pieces are the
``AUTOINCREMENT`` columns and the append-only triggers. Moving to Postgres if a
second tenant ever needs row-level security is a migration, not a rewrite.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from importlib import resources
from pathlib import Path

MIGRATIONS_PACKAGE = "register.migrations"


def _migration_files() -> list[tuple[str, str]]:
    """Return ``(name, sql)`` for every migration, in lexical order."""
    out: list[tuple[str, str]] = []
    root = resources.files(MIGRATIONS_PACKAGE)
    for entry in sorted(root.iterdir(), key=lambda p: p.name):
        if entry.name.endswith(".sql"):
            out.append((entry.name, entry.read_text(encoding="utf-8")))
    return out


def migration_sql() -> str:
    """All migration SQL concatenated — used by the migration guard test."""
    return "\n".join(sql for _, sql in _migration_files())


def connect(path: str | Path) -> sqlite3.Connection:
    """Open a connection with the pragmas this schema assumes."""
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = FULL")
    return conn


def migrate(conn: sqlite3.Connection) -> list[str]:
    """Apply pending migrations. Returns the names applied this call."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            name        TEXT PRIMARY KEY,
            applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    applied = {row["name"] for row in conn.execute("SELECT name FROM schema_migrations")}
    fresh: list[str] = []
    for name, sql in _migration_files():
        if name in applied:
            continue
        # The bookkeeping INSERT goes inside the script's own transaction rather
        # than around it: executescript commits any open transaction before it
        # runs, so an outer BEGIN would not cover the schema change. A migration
        # that half-applies and still records itself is the worst outcome
        # available here.
        escaped = name.replace("'", "''")
        conn.executescript(
            f"BEGIN;\n{sql}\nINSERT INTO schema_migrations (name) VALUES ('{escaped}');\nCOMMIT;"
        )
        fresh.append(name)
    return fresh


def open_register(path: str | Path) -> sqlite3.Connection:
    """Connect and bring the schema up to date in one call."""
    conn = connect(path)
    migrate(conn)
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    conn.execute("BEGIN")
    try:
        yield conn
    except Exception:
        conn.execute("ROLLBACK")
        raise
    try:
        conn.execute("COMMIT")
    except Exception:
        # A failed COMMIT used to leave the transaction open, so the next
        # caller's BEGIN raised "cannot start a transaction within a
        # transaction" and the real error was buried under an unrelated one.
        conn.execute("ROLLBACK")
        raise
