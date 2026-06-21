from __future__ import annotations

from pathlib import Path

import pandas as pd


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def load_tickets(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def normalize_customer_age(df: pd.DataFrame) -> pd.DataFrame:
    age_mapping = {
        "thirty": 30,
        "veinticinco": 25,
    }

    df["clean_customer_age"] = (
        df["Customer Age"].replace(age_mapping).pipe(pd.to_numeric, errors="coerce")
    )

    df.loc[
        ~df["clean_customer_age"].between(18, 90),
        "clean_customer_age",
    ] = pd.NA

    return df


def normalize_ticket_priority(df: pd.DataFrame) -> pd.DataFrame:
    priority_mapping = {
        "critical": "Critical",
        "urgent": "Critical",
        "p1": "Critical",
        "high": "High",
        "alta": "High",
        "p2": "High",
        "medium": "Medium",
        "med": "Medium",
        "p3": "Medium",
        "low": "Low",
        "baja": "Low",
        "p4": "Low",
    }

    priority_text = df["Ticket Priority"].astype("string").str.strip().str.lower()
    df["clean_ticket_priority"] = priority_text.map(priority_mapping).fillna("Unknown")

    return df


def normalize_spanish_date_text(value):
    if pd.isna(value):
        return value

    spanish_months = {
        "enero": "january",
        "febrero": "february",
        "marzo": "march",
        "abril": "april",
        "mayo": "may",
        "junio": "june",
        "julio": "july",
        "agosto": "august",
        "septiembre": "september",
        "setiembre": "september",
        "octubre": "october",
        "noviembre": "november",
        "diciembre": "december",
    }

    text = str(value).strip().lower()

    for spanish_month, english_month in spanish_months.items():
        text = text.replace(spanish_month, english_month)

    return text.replace(" de ", " ")


def parse_purchase_date(value):
    if pd.isna(value):
        return pd.NaT

    normalized = normalize_spanish_date_text(value)
    formats = [
        "%Y-%m-%d",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%d %B %Y",
    ]

    for date_format in formats:
        parsed = pd.to_datetime(normalized, format=date_format, errors="coerce")
        if pd.notna(parsed):
            return parsed

    return pd.NaT


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    df["clean_first_response_time"] = pd.to_datetime(
        df["First Response Time"],
        format=DATETIME_FORMAT,
        errors="coerce",
    )
    df["clean_time_to_resolution"] = pd.to_datetime(
        df["Time to Resolution"],
        format=DATETIME_FORMAT,
        errors="coerce",
    )
    df["purchase_date_text_normalized"] = df["Date of Purchase"].apply(
        normalize_spanish_date_text
    )
    df["clean_date_of_purchase"] = df["Date of Purchase"].apply(parse_purchase_date)

    df["has_invalid_resolution_time"] = (
        df["clean_first_response_time"].notna()
        & df["clean_time_to_resolution"].notna()
        & (df["clean_time_to_resolution"] < df["clean_first_response_time"])
    )

    return df


def normalize_ticket_type(df: pd.DataFrame) -> pd.DataFrame:
    ticket_type_mapping = {
        "product inquiry": "Product Inquiry",
        "technical issue": "Technical Issue",
        "billing inquiry": "Billing Inquiry",
        "billing": "Billing Inquiry",
        "refund request": "Refund Request",
        "refund": "Refund Request",
        "cancellation request": "Cancellation Request",
        "cancel request": "Cancellation Request",
    }

    df["ticket_type_text"] = (
        df["Ticket Type"].astype("string").str.strip().str.lower().str.replace("_", " ")
    )
    df["clean_ticket_type"] = df["ticket_type_text"].map(ticket_type_mapping)

    return df


def normalize_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    df["clean_customer_email"] = (
        df["Customer Email"].astype("string").str.strip().str.lower()
    )
    df["clean_product_purchased"] = (
        df["Product Purchased"].astype("string").str.strip().str.lower().str.title()
    )
    df["clean_ticket_channel"] = df["Ticket Channel"].astype("string").str.strip()
    df["clean_ticket_status"] = df["Ticket Status"].astype("string").str.strip()
    df["clean_customer_gender"] = df["Customer Gender"].astype("string").str.strip()

    return df


def assign_responsible_team(ticket_type: str) -> str:
    mapping = {
        "Technical Issue": "Technical Support",
        "Billing Inquiry": "Billing",
        "Refund Request": "Billing",
        "Cancellation Request": "Customer Success",
        "Product Inquiry": "Customer Support",
    }
    return mapping.get(ticket_type, "General Support")


def detect_sentiment(text) -> str:
    text = str(text).lower()
    urgent_words = ["urgent", "critical", "immediately", "as soon as"]
    negative_words = ["issue", "problem", "error", "unable", "can't", "bug", "failed"]

    if any(word in text for word in urgent_words):
        return "Urgent"
    if any(word in text for word in negative_words):
        return "Frustrated"

    return "Neutral"


def suggest_priority(row: pd.Series) -> str:
    if row["clean_ticket_priority"] != "Unknown":
        return row["clean_ticket_priority"]

    text = f"{row['Ticket Subject']} {row['Ticket Description']}".lower()

    if any(
        word in text
        for word in ["urgent", "critical", "unable", "not working", "failed"]
    ):
        return "High"
    if any(word in text for word in ["refund", "payment", "billing", "cancel"]):
        return "Medium"

    return "Low"


def create_mock_summary(row: pd.Series) -> str:
    return (
        f"Cliente reporta {row['clean_ticket_type'].lower()} "
        f"relacionado con {row['clean_product_purchased']}. "
        f"Asunto: {row['Ticket Subject']}."
    )


def enrich_with_mock_ai(df: pd.DataFrame) -> pd.DataFrame:
    df["ai_category"] = df["clean_ticket_type"]
    df["ai_suggested_priority"] = df.apply(suggest_priority, axis=1)
    df["ai_summary"] = df.apply(create_mock_summary, axis=1)
    df["ai_sentiment"] = df["Ticket Description"].apply(detect_sentiment)
    df["ai_responsible_team"] = df["clean_ticket_type"].apply(assign_responsible_team)

    return df


def process_tickets(path: str | Path) -> pd.DataFrame:
    df = load_tickets(path)
    df = df.drop_duplicates().reset_index(drop=True)
    df = normalize_customer_age(df)
    df = normalize_ticket_priority(df)
    df = normalize_dates(df)
    df = normalize_ticket_type(df)
    df = normalize_text_fields(df)
    df = enrich_with_mock_ai(df)

    return df
