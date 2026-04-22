"""
Streamlit example

This file is typically run inside Streamlit-in-Snowflake, where Snowpark is available and
`get_active_session()` returns the bound Snowpark session.

For local development in Cursor (without pushing to Snowflake), enable LOCAL_PREVIEW:
  LOCAL_PREVIEW=1 streamlit run src/streamlit_example.py

In LOCAL_PREVIEW mode, the app renders using mocked Pandas data so you can validate the UI.
"""

from __future__ import annotations

import os
import sys
from datetime import timedelta
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

try:
    from snowflake.snowpark.context import get_active_session
    from snowflake.snowpark.functions import sum as sp_sum, col, when, max as sp_max, lag
    from snowflake.snowpark import Window
except Exception:
    get_active_session = None  # type: ignore
    sp_sum = col = when = sp_max = lag = Window = None  # type: ignore


LOCAL_PREVIEW = os.getenv("LOCAL_PREVIEW", "0").lower() in ("1", "true", "yes") or (
    get_active_session is None
)

# Set page config
st.set_page_config(layout="wide")

st.title("Streamlit Example (Local Preview Compatible)")

if LOCAL_PREVIEW:
    st.caption(
        "LOCAL_PREVIEW is enabled (or Snowpark is unavailable). Rendering with mocked data."
    )

    # Minimal dataset to preview layout + charts
    df = pd.DataFrame(
        {
            "date": pd.date_range(end=pd.Timestamp.today().normalize(), periods=30, freq="D"),
            "metric": (pd.Series(range(30)) * 1.7 + 10).round(2),
        }
    )

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(x="date:T", y="metric:Q", tooltip=["date:T", "metric:Q"])
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    st.dataframe(df, use_container_width=True)

else:
    # Snowflake-native path (Streamlit-in-Snowflake)
    session = get_active_session()
    st.success("Connected to Snowflake via active Snowpark session.")

    # Example query stub (customize as needed)
    # df_sp = session.table("<DB>.<SCHEMA>.<TABLE>").limit(10)
    # st.dataframe(df_sp.to_pandas(), use_container_width=True)
    st.info("Add Snowpark queries/logic here for your in-Snowflake example.")