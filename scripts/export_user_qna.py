"""Export user queries alongside the bot's next answer to a CSV.

This script reads from `view_user_qna` (preferred) and falls back to
joining `conversations` if the view does not exist.
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

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


def _fetch_qna_pages(client: Client, use_view: bool, page_size: int = 1500) -> Iterable[List[Dict]]:
    last_created_at: str | None = None

    if use_view:
        table = "view_user_qna"
        select = (
            "user_msg_id,user_id,username,first_name,agent_type," \
            "user_query,user_tokens,user_created_at,assistant_msg_id," \
            "assistant_response,assistant_tokens,assistant_created_at"
        )
        while True:
            q = (
                client.table(table)
                .select(select)
            )
            if last_created_at is not None:
                q = q.gt("user_created_at", last_created_at)
            q = q.order("user_created_at", desc=False).limit(page_size)
            res = q.execute()
            rows: List[Dict] = res.data or []
            if not rows:
                break
            last_created_at = rows[-1]["user_created_at"]
            yield rows
    else:
        # Raw fallback: fetch user messages then look ahead for next assistant msg per user/agent
        # Note: less efficient; the view is recommended.
        while True:
            q = (
                client.table("conversations")
                .select("*")
                .eq("role", "user")
            )
            if last_created_at is not None:
                q = q.gt("created_at", last_created_at)
            q = q.order("created_at", desc=False).limit(page_size)
            res = q.execute()
            users: List[Dict] = res.data or []
            if not users:
                break
            last_created_at = users[-1]["created_at"]

            batch: List[Dict] = []
            for u in users:
                # Find next assistant response for same user/agent after this message
                resp = (
                    client.table("conversations")
                    .select("id,message,tokens_used,created_at")
                    .eq("user_id", u["user_id"])\
                    .eq("agent_type", u["agent_type"])\
                    .eq("role", "assistant")\
                    .gt("created_at", u["created_at"])\
                    .order("created_at", desc=False)\
                    .limit(1)\
                    .execute()
                )
                a = resp.data[0] if resp.data else None
                batch.append(
                    {
                        "user_msg_id": u["id"],
                        "user_id": u.get("user_id"),
                        "username": u.get("username"),
                        "first_name": u.get("first_name"),
                        "agent_type": u.get("agent_type"),
                        "user_query": u.get("message", ""),
                        "user_tokens": u.get("tokens_used", 0),
                        "user_created_at": u.get("created_at"),
                        "assistant_msg_id": a.get("id") if a else None,
                        "assistant_response": a.get("message") if a else None,
                        "assistant_tokens": a.get("tokens_used") if a else None,
                        "assistant_created_at": a.get("created_at") if a else None,
                    }
                )
            yield batch


def export_user_qna() -> Path:
    client = _init_client()
    # Detect view
    use_view = True
    try:
        client.table("view_user_qna").select("user_msg_id").limit(1).execute()
    except Exception:
        use_view = False

    reports_dir = _ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_path = reports_dir / f"user_qna_{ts}.csv"

    headers = [
        "user_id",
        "username",
        "first_name",
        "agent_type",
        "user_query",
        "assistant_response",
        "user_tokens",
        "assistant_tokens",
        "user_created_at",
        "assistant_created_at",
    ]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for page in _fetch_qna_pages(client, use_view=use_view):
            for row in page:
                writer.writerow(
                    [
                        row.get("user_id", ""),
                        row.get("username", ""),
                        row.get("first_name", ""),
                        row.get("agent_type", ""),
                        row.get("user_query", ""),
                        row.get("assistant_response", ""),
                        row.get("user_tokens", 0),
                        row.get("assistant_tokens", 0),
                        row.get("user_created_at", ""),
                        row.get("assistant_created_at", ""),
                    ]
                )

    return out_path


if __name__ == "__main__":
    path = export_user_qna()
    print(f"✅ Exported user QnA to: {path}")


