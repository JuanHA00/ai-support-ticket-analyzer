from __future__ import annotations

import pandas as pd


def build_summary_metrics(df: pd.DataFrame) -> dict:
    high_critical_tickets = int(
        df["clean_ticket_priority"].isin(["High", "Critical"]).sum()
    )

    return {
        "total_tickets": int(len(df)),
        "open_tickets": int((df["clean_ticket_status"] == "Open").sum()),
        "high_critical_tickets": high_critical_tickets,
        "unknown_priority_tickets": int(
            (df["clean_ticket_priority"] == "Unknown").sum()
        ),
        "invalid_resolution_time_tickets": int(
            df["has_invalid_resolution_time"].sum()
        ),
        "tickets_by_priority": df["clean_ticket_priority"].value_counts().to_dict(),
        "tickets_by_type": df["clean_ticket_type"].value_counts().to_dict(),
        "tickets_by_status": df["clean_ticket_status"].value_counts().to_dict(),
        "tickets_by_responsible_team": df[
            "ai_responsible_team"
        ].value_counts().to_dict(),
        "top_products": df["clean_product_purchased"].value_counts().head(10).to_dict(),
    }
