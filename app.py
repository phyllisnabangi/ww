# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# — Inject custom CSS to tighten up margins/padding —
st.markdown("""
<style>
  /* Expander header styling */
  .stExpander > button > div {
    font-family: 'Arial', sans-serif !important;
    font-size: 1.8rem !important;
  }

  /* Collapse bottom margin under any Plotly chart */
  section[data-testid="stPlotlyChart"] {
    margin-bottom: 0 !important;
  }

  /* Collapse top/bottom margin around Streamlit tables & dataframes */
  div[data-testid="stDataFrame"],
  .stTable {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
  }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Performance Dashboard", layout="wide")

@st.cache_data
def load_data():
    xls = pd.read_excel("detaileddata.xlsx", sheet_name=None)
    frames = []
    for sheet, df in xls.items():
        df = df.copy()
        if "Traget" in df.columns:
            df = df.rename(columns={"Traget": "Target"})
        df["Stakeholder"] = sheet
        frames.append(df[["Division", "Name", "Target", "Actual", "Stakeholder"]])
    full = pd.concat(frames, ignore_index=True)
    full["Target"] = full["Target"].astype(int)
    full["Actual"] = full["Actual"].astype(int)
    full["Performance"] = full["Actual"] / full["Target"] * 100
    return full

df = load_data()

def pick_color(p):
    if p >= 100:
        return "green"
    if p >= 70:
        return "orange"
    return "red"

# ── Top Section: Overall Performance ─────────────────────────
st.markdown("## Overall Performance")
col1, col2 = st.columns(2, gap="large")

with col1:
    df_div = df.groupby("Division")[["Target", "Actual"]].sum().reset_index()
    df_div["Performance"] = df_div["Actual"] / df_div["Target"] * 100
    df_div["Color"] = df_div["Performance"].apply(pick_color)
    df_div["Label"] = df_div["Performance"].round(1).astype(str) + "%"

    fig_div = px.bar(
        df_div,
        x="Division",
        y="Performance",
        text="Label",
        color="Color",
        color_discrete_map={"green": "green", "orange": "orange", "red": "red"},
        custom_data=["Target", "Actual"],
        hover_data=[]
    )
    fig_div.update_traces(
        textposition="outside",
        hovertemplate=(
            "Division: %{x}<br>Perf: %{y:.1f}%<br>"
            "Target: %{customdata[0]}<br>Actual: %{customdata[1]}<extra></extra>"
        )
    )
    fig_div.update_layout(
        width=900,
        height=450,
        yaxis=dict(range=[0, df_div.Performance.max() + 10], ticksuffix="%"),
        showlegend=False,
        margin=dict(t=10, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_div, use_container_width=True)

with col2:
    df_stk = df.groupby("Stakeholder")[["Target", "Actual"]].sum().reset_index()
    df_stk["Performance"] = df_stk["Actual"] / df_stk["Target"] * 100
    df_stk["Color"] = df_stk["Performance"].apply(pick_color)
    df_stk["Label"] = df_stk["Performance"].round(1).astype(str) + "%"

    fig_stk = px.bar(
        df_stk,
        x="Stakeholder",
        y="Performance",
        text="Label",
        color="Color",
        color_discrete_map={"green": "green", "orange": "orange", "red": "red"},
        custom_data=["Target", "Actual"],
        hover_data=[]
    )
    fig_stk.update_traces(
        textposition="outside",
        hovertemplate=(
            "Stakeholder: %{x}<br>Perf: %{y:.1f}%<br>"
            "Target: %{customdata[0]}<br>Actual: %{customdata[1]}<extra></extra>"
        )
    )
    fig_stk.update_layout(
        yaxis=dict(range=[0, df_stk.Performance.max() + 10], ticksuffix="%"),
        showlegend=False,
        margin=dict(t=10, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_stk, use_container_width=True)

# ── Bottom Section: Detailed Breakdown ──────────────────────
with st.expander("🔍 Detailed Breakdown", expanded=True):
    left, right = st.columns([1, 2], gap="small")
    with left:
        division = st.selectbox("Division", sorted(df.Division.unique()))
        stakeholder = st.selectbox(
            "Stakeholder",
            sorted(df[df.Division == division].Stakeholder.unique())
        )
    with right:
        sub = df[(df.Division == division) & (df.Stakeholder == stakeholder)]
        if sub.empty:
            st.warning("No data for this selection.")
        else:
            # 1) Aggregated stakeholder table (styled Streamlit dataframe)
            agg = sub.groupby("Stakeholder")[["Target", "Actual"]].sum().reset_index()
            agg["Performance"] = agg["Actual"] / agg["Target"] * 100

            def color_perf(val):
                if val >= 100:
                    c = "green"
                elif val >= 70:
                    c = "orange"
                else:
                    c = "red"
                return f"color: {c}"

            styled_agg = (
                agg.style
                   .format({"Target": "{:.0f}", "Actual": "{:.0f}", "Performance": "{:.1f}%"})
                   .applymap(color_perf, subset=["Performance"])
            )

            st.dataframe(styled_agg, use_container_width=True)

            # 2) Detailed breakdown (another Streamlit dataframe)
            df_detail = (
                sub[["Name", "Target", "Actual"]]
                   .assign(**{"Performance %": sub.Performance.round(1).astype(str) + "%"})
            )
            st.dataframe(df_detail, use_container_width=True)



# # app.py
# import streamlit as st
# import pandas as pd
# import plotly.express as px

# # — Inject custom CSS to tighten up margins/padding —
# st.markdown("""
# <style>
#   /* Expander header styling */
#   .stExpander > button > div {
#     font-family: 'Arial', sans-serif !important;
#     font-size: 1.8rem !important;
#   }

#   /* Collapse bottom margin under any Plotly chart */
#   section[data-testid="stPlotlyChart"] {
#     margin-bottom: 0 !important;
#   }

#   /* Collapse top/bottom margin around Streamlit tables & dataframes */
#   div[data-testid="stDataFrame"],
#   .stTable {
#     margin-top: 0 !important;
#     margin-bottom: 0 !important;
#   }
# </style>
# """, unsafe_allow_html=True)

# st.set_page_config(page_title="Performance Dashboard", layout="wide")

# @st.cache_data
# def load_data():
#     xls = pd.read_excel("detaileddata.xlsx", sheet_name=None)
#     frames = []
#     for sheet, df in xls.items():
#         df = df.copy()
#         if "Traget" in df.columns:
#             df = df.rename(columns={"Traget": "Target"})
#         df["Stakeholder"] = sheet
#         frames.append(df[["Division", "Name", "Target", "Actual", "Stakeholder"]])
#     full = pd.concat(frames, ignore_index=True)
#     full["Target"] = full["Target"].astype(int)
#     full["Actual"] = full["Actual"].astype(int)
#     full["Performance"] = full["Actual"] / full["Target"] * 100
#     return full

# df = load_data()

# def pick_color(p):
#     if p >= 100:
#         return "green"
#     if p >= 70:
#         return "orange"
#     return "red"

# # ── Top Section: Overall Performance ─────────────────────────
# st.markdown("## Overall Performance")
# col1, col2 = st.columns(2, gap="large")

# with col1:
#     df_div = df.groupby("Division")[["Target", "Actual"]].sum().reset_index()
#     df_div["Performance"] = df_div["Actual"] / df_div["Target"] * 100
#     df_div["Color"] = df_div["Performance"].apply(pick_color)
#     df_div["Label"] = df_div["Performance"].round(1).astype(str) + "%"

#     fig_div = px.bar(
#         df_div,
#         x="Division",
#         y="Performance",
#         text="Label",
#         color="Color",
#         color_discrete_map={"green": "green", "orange": "orange", "red": "red"},
#         custom_data=["Target", "Actual"],
#         hover_data=[]
#     )
#     fig_div.update_traces(
#         textposition="outside",
#         hovertemplate=(
#             "Division: %{x}<br>Perf: %{y:.1f}%<br>"
#             "Target: %{customdata[0]}<br>Actual: %{customdata[1]}<extra></extra>"
#         )
#     )
#     fig_div.update_layout(
#         width=900,
#         height=450,
#         yaxis=dict(range=[0, df_div.Performance.max() + 10], ticksuffix="%"),
#         showlegend=False,
#         margin=dict(t=10, b=20, l=20, r=20)
#     )
#     st.plotly_chart(fig_div, use_container_width=True)

# with col2:
#     df_stk = df.groupby("Stakeholder")[["Target", "Actual"]].sum().reset_index()
#     df_stk["Performance"] = df_stk["Actual"] / df_stk["Target"] * 100
#     df_stk["Color"] = df_stk["Performance"].apply(pick_color)
#     df_stk["Label"] = df_stk["Performance"].round(1).astype(str) + "%"

#     fig_stk = px.bar(
#         df_stk,
#         x="Stakeholder",
#         y="Performance",
#         text="Label",
#         color="Color",
#         color_discrete_map={"green": "green", "orange": "orange", "red": "red"},
#         custom_data=["Target", "Actual"],
#         hover_data=[]
#     )
#     fig_stk.update_traces(
#         textposition="outside",
#         hovertemplate=(
#             "Stakeholder: %{x}<br>Perf: %{y:.1f}%<br>"
#             "Target: %{customdata[0]}<br>Actual: %{customdata[1]}<extra></extra>"
#         )
#     )
#     fig_stk.update_layout(
#         yaxis=dict(range=[0, df_stk.Performance.max() + 10], ticksuffix="%"),
#         showlegend=False,
#         margin=dict(t=10, b=20, l=20, r=20)
#     )
#     st.plotly_chart(fig_stk, use_container_width=True)

# # ── Bottom Section: Detailed Breakdown ──────────────────────
# with st.expander("🔍 Detailed Breakdown", expanded=True):
#     left, right = st.columns([1, 2], gap="small")
#     with left:
#         division = st.selectbox("Division", sorted(df.Division.unique()))
#         stakeholder = st.selectbox(
#             "Stakeholder",
#             sorted(df[df.Division == division].Stakeholder.unique())
#         )
#     with right:
#         sub = df[(df.Division == division) & (df.Stakeholder == stakeholder)]
#         if sub.empty:
#             st.warning("No data for this selection.")
#         else:
#             # 1) Aggregated stakeholder table (Streamlit dataframe)
#             agg = sub.groupby("Stakeholder")[["Target", "Actual"]].sum().reset_index()
#             agg["Performance %"] = (agg["Actual"] / agg["Target"] * 100).round(1).astype(str) + "%"
#             st.dataframe(agg, use_container_width=True)

#             # 2) Detailed breakdown (another Streamlit dataframe)
#             df_detail = (
#                 sub[["Name", "Target", "Actual"]]
#                 .assign(**{"Performance %": sub.Performance.round(1).astype(str) + "%"})
#             )
#             st.dataframe(df_detail, use_container_width=True)

