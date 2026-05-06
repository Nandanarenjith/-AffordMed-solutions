import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


@dataclass
class Notification:
    id: str
    title: str
    weight: float
   
    timestamp: str


def parse_timestamp(ts: str) -> datetime:
    ts = ts.strip()
    if ts.endswith("Z"):
        # datetime.fromisoformat doesn't always accept trailing Z on older Python
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def priority_exponential(weight: float, age_hours: float, tau_hours: float) -> float:
    """priority = weight * exp(-age_hours / tau_hours)"""
    if weight <= 0:
        return 0.0
    if tau_hours <= 0:
        # Degenerate: no decay window
        return 0.0 if age_hours > 0 else weight
    return float(weight) * math.exp(-age_hours / tau_hours)


def age_hours_from_timestamp(ts: str, now: Optional[datetime] = None) -> float:
    now = now or datetime.now(timezone.utc)
    created = parse_timestamp(ts)
    return (now - created).total_seconds() / 3600.0


def top_n_notifications(
    notifications: List[Notification],
    n: int = 10,
    tau_hours: float = 12.0,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    now = now or datetime.now(timezone.utc)

    scored: List[Dict[str, Any]] = []
    for notif in notifications:
        age_h = age_hours_from_timestamp(notif.timestamp, now=now)
        pr = priority_exponential(notif.weight, age_h, tau_hours=tau_hours)
        item = asdict(notif)
        item["age_hours"] = age_h
        item["priority"] = pr
        scored.append(item)

    scored.sort(key=lambda x: x["priority"], reverse=True)
    return scored[:n]


def format_table(rows: List[Dict[str, Any]], max_title: int = 45) -> str:
    headers = ["Rank", "ID", "Weight", "Age(h)", "Priority", "Title"]

    def trunc(s: str) -> str:
        s = s or ""
        return s if len(s) <= max_title else s[: max_title - 3] + "..."

    col_widths = {
        "Rank": 4,
        "ID": 10,
        "Weight": 8,
        "Age(h)": 8,
        "Priority": 10,
        "Title": max_title,
    }

    def fmt(v: Any, w: int, right: bool = False) -> str:
        s = str(v)
        if len(s) > w:
            s = s[: w - 3] + "..."
        return s.rjust(w) if right else s.ljust(w)

    lines = []
    lines.append(
        " ".join(
            [
                fmt(headers[i], col_widths[headers[i]])
                for i in range(len(headers))
            ]
        )
    )
    lines.append("-" * (sum(col_widths[h] for h in headers) + (len(headers) - 1)))

    for idx, r in enumerate(rows, start=1):
        lines.append(
            " ".join(
                [
                    fmt(idx, col_widths["Rank"]),
                    fmt(r["id"], col_widths["ID"]),
                    fmt(f"{r['weight']:.2f}", col_widths["Weight"], right=True),
                    fmt(f"{r['age_hours']:.2f}", col_widths["Age(h)"], right=True),
                    fmt(f"{r['priority']:.6f}", col_widths["Priority"], right=True),
                    fmt(trunc(r.get("title", "")), col_widths["Title"]),
                ]
            )
        )
    return "\n".join(lines)


def main() -> None:
    # Replace this sample data with your real notifications input.
    # timestamp should be ISO-8601.
    now = datetime.now(timezone.utc)

    sample_notifications: List[Notification] = [
        Notification(
            id="n1",
            title="Security alert: new login",
            weight=9.0,
            timestamp=(now).isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n2",
            title="Weekly digest: new matches",
            weight=6.0,
            timestamp=(now.replace(microsecond=0) - (datetime.now(timezone.utc) - (now - math.ceil(36) * 0 * 3600 * 0)).replace(microsecond=0) ),
            # This line is intentionally nonsensical to emphasize that you should provide real timestamps.
            # Comment it out and use simpler timestamps below.
        ),
    ]

    # Practical sample data (uncomment):
    sample_notifications = [
        Notification(
            id="n1",
            title="Security alert: new login",
            weight=9.0,
            timestamp=(now - (0.5 * 3600 * 1.0)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n2",
            title="Promotion: 20% off",
            weight=4.5,
            timestamp=(now - (12 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n3",
            title="Mentions in your post",
            weight=7.0,
            timestamp=(now - (3 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n4",
            title="Friend request accepted",
            weight=5.0,
            timestamp=(now - (30 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n5",
            title="System maintenance reminder",
            weight=3.5,
            timestamp=(now - (8 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n6",
            title="High-priority: task overdue",
            weight=10.0,
            timestamp=(now - (1.2 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n7",
            title="New message from support",
            weight=8.0,
            timestamp=(now - (6 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n8",
            title="Tip of the day",
            weight=2.0,
            timestamp=(now - (60 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n9",
            title="Live event starts soon",
            weight=6.5,
            timestamp=(now - (2.5 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n10",
            title="Account verification needed",
            weight=7.5,
            timestamp=(now - (16 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
        Notification(
            id="n11",
            title="Low engagement content suggestion",
            weight=1.0,
            timestamp=(now - (5 * 3600)) .isoformat().replace("+00:00", "Z"),
        ),
    ]

    tau_hours = 12.0
    top10 = top_n_notifications(sample_notifications, n=10, tau_hours=tau_hours, now=now)

    print("Top 10 Notifications (priority = weight * exp(-age_hours / tau))")
    print(f"tau_hours = {tau_hours}\n")
    print(format_table(top10))


if __name__ == "__main__":
    main()

