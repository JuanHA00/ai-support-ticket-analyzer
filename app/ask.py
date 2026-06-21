from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.metrics import build_summary_metrics


def load_knowledge_base(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def answer_question(question: str, df: pd.DataFrame, knowledge_base: str) -> str:
    question_lower = question.lower()
    metrics = build_summary_metrics(df)

    if any(word in question_lower for word in ["critico", "crítico", "critical"]):
        top_types = (
            df[df["ai_suggested_priority"] == "Critical"]["clean_ticket_type"]
            .value_counts()
            .head(3)
            .to_dict()
        )
        return (
            f"Hay {metrics['tickets_by_priority'].get('Critical', 0)} tickets con "
            f"prioridad original critica. Los tipos mas frecuentes entre tickets "
            f"criticos son: {top_types}. Segun la base de conocimiento, Critical "
            f"representa clientes bloqueados, problemas urgentes o sin workaround."
        )

    if any(word in question_lower for word in ["producto", "product"]):
        top_products = metrics["top_products"]
        return (
            f"Los productos con mas tickets son: {top_products}. Esto puede ayudar "
            f"a priorizar analisis de calidad, soporte o documentacion."
        )

    if any(word in question_lower for word in ["equipo", "team", "responsable"]):
        teams = metrics["tickets_by_responsible_team"]
        return (
            f"La carga sugerida por equipo es: {teams}. Segun la base de "
            f"conocimiento, Billing atiende pagos/reembolsos, Technical Support "
            f"atiende fallas tecnicas y Customer Success atiende cancelaciones."
        )

    if any(word in question_lower for word in ["cancel", "churn", "retencion"]):
        cancellation_count = int(
            (df["clean_ticket_type"] == "Cancellation Request").sum()
        )
        return (
            f"Hay {cancellation_count} tickets de cancelacion. La base de "
            f"conocimiento los marca como posibles riesgos de churn o perdida "
            f"de cliente."
        )

    if any(word in question_lower for word in ["tiempo", "resolucion", "resolution"]):
        invalid_count = metrics["invalid_resolution_time_tickets"]
        return (
            f"Se detectaron {invalid_count} tickets con resolucion anterior a la "
            f"primera respuesta. Estos registros requieren revision antes de usar "
            f"tiempos de resolucion como KPI operativo."
        )

    return (
        "Puedo responder preguntas sobre prioridades criticas, productos con mas "
        "tickets, carga por equipo responsable, cancelaciones y consistencia de "
        "tiempos. La respuesta usa tickets procesados y la base de conocimiento."
    )
