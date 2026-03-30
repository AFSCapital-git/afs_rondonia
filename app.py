import streamlit as st
import pandas as pd

st.set_page_config(page_title="Correspondentes RO", layout="wide")

st.title("Correspondentes RO")

@st.cache_data
def load_data():
    return pd.read_excel("CORRESPONDENTES_RO.xlsx", dtype=str)

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filtros")

# Global text search
search = st.sidebar.text_input("Busca geral (qualquer coluna)")

# Per-column filters
with st.sidebar.expander("Filtrar por coluna", expanded=False):
    filters = {}
    for col in df.columns:
        unique_vals = ["(Todos)"] + sorted(df[col].dropna().unique().tolist())
        selected = st.selectbox(col, unique_vals, key=f"filter_{col}")
        if selected != "(Todos)":
            filters[col] = selected

# --- Apply filters ---
filtered_df = df.copy()

if search:
    mask = filtered_df.apply(
        lambda row: row.astype(str).str.contains(search, case=False, na=False).any(),
        axis=1,
    )
    filtered_df = filtered_df[mask]

for col, val in filters.items():
    filtered_df = filtered_df[filtered_df[col] == val]

# --- Results ---
st.caption(f"{len(filtered_df):,} de {len(df):,} registros")

st.dataframe(filtered_df, use_container_width=True, height=600)

# --- Download ---
csv = filtered_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="Baixar resultado (.csv)",
    data=csv,
    file_name="correspondentes_filtrado.csv",
    mime="text/csv",
)
