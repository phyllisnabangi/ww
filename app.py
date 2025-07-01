# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# — Inject a little CSS to tighten up padding/margins —
st.markdown("""
    <style>
      /* reduce top padding of the main block-container */
      .block-container { padding-top: 0.5rem; }
      /* reduce spacing above headers */
      h2 { margin-top: 0.5rem; margin-bottom: 0.25rem;}
      /* tighten space around tables */
      .element-container, .stTable { margin-bottom: 0.25rem; }
    </style>
""", unsafe_allow_html=True)

# # Narrow the gap & restyle the expander header
# st.markdown("""
# <style>
#   /* 1) Expander header: same font as your other H2s */
#   .stExpander > button > div {
#     font-family: 'Arial', sans-serif !important;
#     font-size: 1.8rem !important; /* Increased font size */
#   }
#   /* 2) Remove the bottom margin under any Plotly chart/table */
#   section[data-testid="stPlotlyChart"] {
#     margin-bottom: 0.1rem !important; /* Reduced bottom margin */
#   }
#   /* 3) Also collapse margin under Streamlit DataFrames */
#   .stDataFrame, .stTable {
#     margin-top: 0.1rem !important; /* Reduced top margin */
#     margin-bottom: 0.25rem !important; /* Reduced bottom margin */
#   }
# </style>
# """, unsafe_allow_html=True)


st.set_page_config(page_title="Performance Dashboard", layout="wide")

@st.cache_data
def load_data():
    xls = pd.read_excel("detaileddata.xlsx", sheet_name=None)
    frames = []
    for sheet, df in xls.items():
        df = df.copy()
        if "Traget" in df.columns:
            df = df.rename(columns={"Traget":"Target"})
        df["Stakeholder"] = sheet
        frames.append(df[["Division","Name","Target","Actual","Stakeholder"]])
    full = pd.concat(frames, ignore_index=True)
    full["Target"] = full["Target"].astype(int)
    full["Actual"] = full["Actual"].astype(int)
    full["Performance"] = full["Actual"] / full["Target"] * 100
    return full

df = load_data()

def pick_color(p):
    if p >= 100: return "green"
    if p >= 70:  return "orange"
    return "red"

st.markdown("## Overall Performance", unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    df_div = df.groupby("Division")[["Target","Actual"]].sum().reset_index()
    df_div["Performance"] = df_div["Actual"]/df_div["Target"]*100
    df_div["Color"] = df_div["Performance"].apply(pick_color)
    df_div["Label"] = df_div["Performance"].round(1).astype(str)+"%"

    fig_div = px.bar(
        df_div, x="Division", y="Performance", text="Label",
        color="Color", color_discrete_map={"green":"green","orange":"orange","red":"red"},
        custom_data=["Target","Actual"], hover_data=[]
    )
    fig_div.update_traces(
        textposition="outside",
        hovertemplate=(
            "Division: %{x}<br>Perf: %{y:.1f}%<br>"
            "Target: %{customdata[0]}<br>Actual: %{customdata[1]}<extra></extra>"
        )
    )
    fig_div.update_layout(
        width=900, height=450,
        yaxis=dict(range=[0, df_div.Performance.max()+10], ticksuffix="%"),
        showlegend=False,
        margin=dict(t=10,b=20,l=20,r=20)
    )
    st.plotly_chart(fig_div, use_container_width=True)

with col2:
    df_stk = df.groupby("Stakeholder")[["Target","Actual"]].sum().reset_index()
    df_stk["Performance"] = df_stk["Actual"]/df_stk["Target"]*100
    df_stk["Color"] = df_stk["Performance"].apply(pick_color)
    df_stk["Label"] = df_stk["Performance"].round(1).astype(str)+"%"

    fig_stk = px.bar(
        df_stk, x="Stakeholder", y="Performance", text="Label",
        color="Color", color_discrete_map={"green":"green","orange":"orange","red":"red"},
        custom_data=["Target","Actual"], hover_data=[]
    )
    fig_stk.update_traces(
        textposition="outside",
        hovertemplate=(
            "Stakeholder: %{x}<br>Perf: %{y:.1f}%<br>"
            "Target: %{customdata[0]}<br>Actual: %{customdata[1]}<extra></extra>"
        )
    )
    fig_stk.update_layout(
        yaxis=dict(range=[0, df_stk.Performance.max()+10], ticksuffix="%"),
        showlegend=False,
        margin=dict(t=10,b=20,l=20,r=20)
    )
    st.plotly_chart(fig_stk, use_container_width=True)

# ────────────────────────────────────────────────────────────────────────
# Bottom section in one expander to eliminate extra whitespace
with st.expander("🔍 Detailed Breakdown", expanded=True):
    left, right = st.columns([1, 2], gap="small")
    with left:
        division = st.selectbox("Division", sorted(df.Division.unique()))
        stakeholder = st.selectbox(
            "Stakeholder",
            sorted(df[df.Division==division].Stakeholder.unique())
        )
    with right:
        sub = df[(df.Division==division)&(df.Stakeholder==stakeholder)]
        if sub.empty:
            st.warning("No data for this selection.")
        else:
            # Aggregated stakeholder table as Plotly Table
            agg = sub.groupby("Stakeholder")[["Target","Actual"]].sum().reset_index()
            agg["Performance"] = agg["Actual"]/agg["Target"]*100
            agg["PerfLabel"] = agg["Performance"].round(1).astype(str) + "%"
            row_colors = [ pick_color(p) for p in agg["Performance"] ]
            fig_table = go.Figure(data=[go.Table(
                header=dict(values=["Stakeholder","Target","Actual","Performance %"],
                            fill_color="lightgrey"),
                cells=dict(
                    values=[agg.Stakeholder, agg.Target, agg.Actual, agg.PerfLabel],
                    fill_color=[["white"]*len(agg)]*3 + [row_colors]
                )
            )])
            fig_table.update_layout(margin=dict(t=0,b=0))
            st.plotly_chart(fig_table, use_container_width=True)

            # Detail breakdown DataFrame
            df_detail = (
                sub[["Name","Target","Actual"]]
                .assign(**{"Performance %": sub.Performance.round(1).astype(str)+"%"})
            )
            st.dataframe(df_detail, use_container_width=True)
