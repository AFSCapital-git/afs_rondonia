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

# Per-column filters (only Inc. columns)
inc_cols = [c for c in df.columns if c.strip().startswith("Inc.")]

with st.sidebar.expander("Filtrar por coluna", expanded=False):
    bool_op = st.radio(
        "Operação entre filtros",
        options=["E", "OU"],
        horizontal=True,
        help="E: mostra linhas que atendem a TODOS os filtros. OU: mostra linhas que atendem a QUALQUER filtro.",
    )
    filters = {}
    for col in inc_cols:
        unique_vals = ["(Todos)"] + sorted(df[col].dropna().unique().tolist())
        selected = st.selectbox(col.strip(), unique_vals, key=f"filter_{col}")
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

if filters:
    col_masks = [filtered_df[col] == val for col, val in filters.items()]
    if bool_op == "E":
        combined = col_masks[0]
        for m in col_masks[1:]:
            combined = combined & m
    else:  # OU
        combined = col_masks[0]
        for m in col_masks[1:]:
            combined = combined | m
    filtered_df = filtered_df[combined]

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

# --- Legend ---
st.divider()
with st.expander("Legenda das Incidências", expanded=False):
    st.markdown("""
| Incidência | Descrição |
|---|---|
| **Inc. I** | Recepção e encaminhamento de propostas de abertura de contas de depósitos à vista, a prazo e de poupança mantidas pela instituição contratante |
| **Inc. II** | Realização de recebimentos, pagamentos e transferências eletrônicas visando à movimentação de contas de depósitos de titularidade de clientes mantidas pela instituição contratante |
| **Inc. III** | Recebimentos e pagamentos de qualquer natureza, e outras atividades decorrentes da execução de contratos e convênios de prestação de serviços mantidos pela instituição contratante com terceiros |
| **Inc. IV** | Execução ativa e passiva de ordens de pagamento cursadas por intermédio da instituição contratante por solicitação de clientes e usuários |
| **Inc. V** | Recepção e encaminhamento de propostas de operações de crédito e de arrendamento mercantil concedidas pela instituição contratante, bem como outros serviços prestados para o acompanhamento da operação |
| **Inc. VI** | Recebimentos e pagamentos relacionados a letras de câmbio de aceite da instituição contratante |
| **Inc. VIII** | Recepção e encaminhamento de propostas de fornecimento de cartões de crédito de responsabilidade da instituição contratante |
""")
