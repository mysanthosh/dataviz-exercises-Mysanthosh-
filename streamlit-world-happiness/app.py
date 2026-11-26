#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""World Happiness Dashboard (2023) — Streamlit + Plotly."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout="wide")
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# The CSV must be located in the data folder next to app.py.
DATA = Path(__file__).parent / "data" / "world_happiness_2023.csv"
if not DATA.exists():
    st.error(f"Dataset not found: {DATA}. Put world_happiness_2023.csv in the data folder.")
    st.stop()

@st.cache_data
def load_data(csv_path: str) -> pd.DataFrame:
    data = pd.read_csv(csv_path)
    expected = [
        "Country name", "Regional indicator", "Ladder score",
        "Logged GDP per capita", "Social support", "Healthy life expectancy",
        "Freedom to make life choices", "Generosity", "Perceptions of corruption",
    ]
    if list(data.columns) != expected:
        raise ValueError("The CSV columns do not match the World Happiness 2023 dataset.")
    data.columns = [
        "Country", "Region", "Score", "GDP", "Social_Support",
        "Life_Expectancy", "Freedom", "Generosity", "Corruption",
    ]
    return data

try:
    df = load_data(str(DATA))
except (OSError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

# ONE sidebar shared by both charts. Widget keys are unique.
with st.sidebar:
    st.header("Filters")
    regions = ["All Regions"] + sorted(df["Region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions, key="region_filter")
    top_n = st.slider("Show top N", min_value=5, max_value=25, value=15, key="top_n_filter")

filtered = df if selected_region == "All Regions" else df[df["Region"] == selected_region]
if filtered.empty:
    st.warning("No countries match this region.")
    st.stop()

top = filtered.nlargest(top_n, "Score").sort_values("Score")

# Key statistics
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric(
    "Avg Score",
    f"{filtered['Score'].mean():.2f}",
    f"{filtered['Score'].mean() - df['Score'].mean():+.2f} vs global",
)
col3.metric("Happiest", filtered.loc[filtered["Score"].idxmax(), "Country"])

st.divider()

# Chart 1: the highest-scoring countries
fig_bar = px.bar(
    top,
    x="Score",
    y="Country",
    orientation="h",
    labels={"Score": "Happiness Score (0–10)", "Country": ""},
    template="plotly_white",
    title=f"Happiest {len(top)} Countries in 2023 — {selected_region}",
    height=600,
)
fig_bar.update_layout(
    title_font=dict(family="Arial", size=16, color="slategrey"),
    xaxis=dict(range=[0, 8.0]),
)
st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Chart 2: GDP vs happiness score
st.subheader("GDP per Capita vs Happiness Score")
st.write(
    "Each point represents a country. The horizontal axis is **logged GDP per capita**, "
    "not GDP in dollars. Hover over points for details. The region filter affects both charts."
)
fig_scatter = px.scatter(
    filtered,
    x="GDP",
    y="Score",
    color="Region",
    hover_name="Country",
    hover_data={"Social_Support": ":.3f", "Life_Expectancy": ":.1f"},
    labels={"GDP": "Logged GDP per Capita", "Score": "Happiness Score (0–10)", "Region": "Region"},
    title=f"GDP and Happiness Relationship — {selected_region}",
    template="plotly_white",
    height=550,
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()
st.caption("Built with Streamlit + Plotly | World Happiness Report 2023")
