"""Export all user queries to a CSV file.

This script queries the read-friendly `view_user_queries` if present,
falling back to the `conversations` table. It paginates through results
to avoid memory blowups and writes a timestamped CSV under `reports/`.
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


def _init_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in environment")
    return create_client(url, key)


def _ensure_reports_dir() -> Path:
    reports = Path(__file__).resolve().parents[1] / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    return reports


def _fetch_in_pages(client: Client, use_view: bool, page_size: int = 2000) -> Iterable[List[Dict]]:
    """Yield pages of rows from the view/table ordered by created_at asc.

    Uses keyset pagination on `created_at` to be robust to large datasets.
    """
    last_created_at: str | None = None
    table_name = "view_user_queries" if use_view else "conversations"

    while True:
        query = (
            client.table(table_name)
            .select(
                "id,user_id,username,first_name,agent_type,"
                + ("query" if use_view else "message")
                + ",tokens_used,created_at"
            )
        )

        # Filter to user role if reading raw table
        if not use_view:
            query = query.eq("role", "user")

        if last_created_at is not None:
            query = query.gt("created_at", last_created_at)

        query = query.order("created_at", desc=False).limit(page_size)
        res = query.execute()
        rows: List[Dict] = res.data or []
        if not rows:
            break

        last_created_at = rows[-1]["created_at"]
        yield rows


def export_user_queries() -> Path:
    client = _init_client()

    # Detect if the view exists by attempting a lightweight select
    use_view = True
    try:
        client.table("view_user_queries").select("id").limit(1).execute()
    except Exception:
        use_view = False

    reports_dir = _ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = reports_dir / f"user_queries_{ts}.csv"

    headers = [
        "user_id",
        "username",
        "first_name",
        "agent_type",
        "query",
        "tokens_used",
        "created_at",
    ]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for page in _fetch_in_pages(client, use_view=use_view):
            for row in page:
                writer.writerow(
                    [
                        row.get("user_id", ""),
                        row.get("username", ""),
                        row.get("first_name", ""),
                        row.get("agent_type", ""),
                        row.get("query", row.get("message", "")),
                        row.get("tokens_used", 0),
                        row.get("created_at", ""),
                    ]
                )

    return out_path


if __name__ == "__main__":
    path = export_user_queries()
    print(f"✅ Exported user queries to: {path}")


