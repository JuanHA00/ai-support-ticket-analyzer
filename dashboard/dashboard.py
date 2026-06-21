import os

import requests
import pandas as pd
import streamlit as st
import plotly.express as px

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.logo("dashboard/download.png", size = "large")
st.set_page_config(page_title="AI Support Ticket Analyzer", layout="wide")

st.title("AI Support Ticket Analyzer")

summary = requests.get(f"{API_URL}/summary").json()
tickets = requests.get(f"{API_URL}/tickets?limit=403").json()
df = pd.DataFrame(tickets)

col1, col2, col3 = st.columns(3)
col1.metric("Total tickets", summary["total_tickets"])
col2.metric("Open tickets", summary["open_tickets"])
col3.metric("High/Critical", summary["high_critical_tickets"])

st.subheader("Tickets by Responsible Team")
team_df = pd.DataFrame(
    summary["tickets_by_responsible_team"].items(),
    columns=["Team", "Tickets"]
)
fig = px.bar(team_df, x="Team", y="Tickets", color = "Team",text = "Tickets")
st.plotly_chart(fig, use_container_width=True)

st.subheader("Filters")

priority = st.multiselect(
    "Priority",
    sorted(df["clean_ticket_priority"].dropna().unique())
)

team = st.multiselect(
    "Responsible team",
    sorted(df["ai_responsible_team"].dropna().unique())
)

filtered_df = df.copy()

if priority:
    filtered_df = filtered_df[filtered_df["clean_ticket_priority"].isin(priority)]

if team:
    filtered_df = filtered_df[filtered_df["ai_responsible_team"].isin(team)]

st.subheader("Processed Tickets")
st.dataframe(filtered_df, use_container_width=True)
