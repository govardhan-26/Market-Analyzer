import streamlit as st
from main import run_analysis

st.set_page_config(page_title="Market Analyzer", page_icon="📊", layout="wide")
st.title("📊 Data-Driven Market Analyzer")
st.caption("Hierarchical multi-agent system: Researcher + Coder supervised by a Project Manager")

with st.sidebar:
    st.header("Example Queries")
    examples = [
        "Compare the tech job market in the US vs UK: salaries, demand, and top cities",
        "Compare AI/ML engineer salaries in Germany vs Canada",
        "Analyze the fintech job market growth in Singapore vs Australia",
        "Compare remote work trends in tech: US vs Europe",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.prefill = ex

st.subheader("Market Comparison Query")
default_query = st.session_state.pop("prefill", "")
query = st.text_area(
    "Describe the market comparison you want to analyze:",
    value=default_query,
    height=100,
    placeholder="e.g. Compare software engineer salaries in the US vs Germany...",
)

if st.button("Run Analysis", type="primary", disabled=not query.strip()):
    with st.spinner("Researching and analyzing... This may take a minute."):
        try:
            result = run_analysis(query)
            st.subheader("Analysis Report")
            st.markdown(result)
        except Exception as e:
            st.error(f"Error: {e}")
