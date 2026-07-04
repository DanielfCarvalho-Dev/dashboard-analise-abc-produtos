import streamlit as st
import pandas as pd
from connection import conectar_banco
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Dashboard de Produtos",
    layout="wide"
)

st.markdown(
    """
    <style>
    div.stDownloadButton > button {
        background-color: #16A34A;
        color: white;
        border: none;
    }

    div.stDownloadButton > button:hover {
        background-color: #15803D;
        color: white;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

query = """
SELECT * FROM vw_analise_abc_produtos

"""

df = pd.read_sql_query(query, conectar_banco())

st.sidebar.header("Filtros")

categorias = st.sidebar.multiselect(
    "Selecione as categorias",
    options=df["Categoria"].unique(),
    default=df["Categoria"].unique(),
)
# Adicionar filtro classe ABC
classes = st.sidebar.multiselect(
    "Selecione a classe",
    options=df["Classe_Vip"].unique(),
    default=df["Classe_Vip"].unique(),
)
# Aplicando filtros
df_filtrados = df[
    (df["Categoria"].isin(categorias)) &
    (df["Classe_Vip"].isin(classes))
]

st.title("Dashboard de Análise de Produtos")

col1, col2, col3, col4 = st.columns(4)

receita_total = df_filtrados["Receita_Total"].sum()
quantitade_total = df_filtrados["Quantidade_Vendida"].sum()
total_produtos = df_filtrados["ProdutoId"].nunique()
ticket_medio = receita_total / quantitade_total

col1.metric("Receita Total", f"R$ {receita_total:,.2f}")
col2.metric("Quantidade Vendida", quantitade_total)
col3.metric("Total de Produtos", total_produtos)
col4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

top10 = df_filtrados.sort_values(
    by="Receita_Total",
    ascending=False,
).head(10)

fig_top10, ax_top10 = plt.subplots(figsize=(12, 6))

cores_classe = {
    "CLASSE A": "#0B3D91",
    "CLASSE B": "#4682B4",
    "CLASSE C": "#B0C4DE",
}

classe_top10 = (
    top10["Classe_Vip"]
    .astype(str)
    .str.upper()
    .str.strip()
    .replace({"A": "CLASSE A", "B": "CLASSE B", "C": "CLASSE C"})
)
cores_top10 = classe_top10.map(cores_classe).fillna("#B0C4DE")

bars_top10 = ax_top10.bar(
    top10["Descricao"],
    top10["Receita_Total"],
    color=cores_top10,
)
ax_top10.bar_label(
    bars_top10,
    labels=[f"R$ {valor:,.0f}" for valor in top10["Receita_Total"]],
    padding=3,
)

ax_top10.tick_params(axis="x", rotation=45)
ax_top10.set_title("Top 10 Produtos por Receita")
ax_top10.set_ylabel("Receita Total")
ax_top10.set_xlabel("Produtos")
ax_top10.margins(y=0.15)
ax_top10.legend(
    handles=[
        plt.Rectangle((0, 0), 1, 1, color=cores_classe["CLASSE A"], label="Classe A"),
        plt.Rectangle((0, 0), 1, 1, color=cores_classe["CLASSE B"], label="Classe B"),
        plt.Rectangle((0, 0), 1, 1, color=cores_classe["CLASSE C"], label="Classe C"),
    ]
)

# Pareto chart
df_pareto = (
    df_filtrados.groupby("Categoria", as_index=False)["Receita_Total"]
    .sum()
    .sort_values("Receita_Total", ascending=False)
)

df_pareto["Percentual_Acumulado"] = (
    df_pareto["Receita_Total"].cumsum()
    / df_pareto["Receita_Total"].sum()
    * 100
)
df_pareto["Classe_ABC"] = "CLASSE C"
df_pareto.loc[df_pareto["Percentual_Acumulado"] <= 95, "Classe_ABC"] = "CLASSE B"
df_pareto.loc[df_pareto["Percentual_Acumulado"] <= 80, "Classe_ABC"] = "CLASSE A"

if not df_pareto.empty:
    df_pareto.loc[df_pareto.index[0], "Classe_ABC"] = "CLASSE A"

fig_pareto, ax_pareto = plt.subplots(figsize=(12, 6))
cores_pareto = df_pareto["Classe_ABC"].map(cores_classe).fillna("#B0C4DE")
bars_pareto = ax_pareto.bar(
    df_pareto["Categoria"],
    df_pareto["Receita_Total"],
    color=cores_pareto,
)
ax_pareto.bar_label(
    bars_pareto,
    labels=[f"R$ {valor:,.0f}" for valor in df_pareto["Receita_Total"]],
    padding=3,
)
ax_pareto.set_ylabel("Receita Total")
ax_pareto.set_xlabel("Categoria")
ax_pareto.margins(y=0.15)

ax2 = ax_pareto.twinx()

ax2.plot(
    df_pareto["Categoria"],
    df_pareto["Percentual_Acumulado"],
    marker="o",
)

ax2.set_ylabel("Percentual Acumulado (%)")
ax2.set_ylim(0, 100)

# Linha de corte ABC (80%)
ax2.axhline(y=80, color="red", linestyle="--", label="Corte ABC (80%)")
ax_pareto.tick_params(axis="x", rotation=45)
ax_pareto.set_title("Pareto Chart")

# Scatter de Performance
fig, ax = plt.subplots(figsize=(12, 6))

classe_scatter = (
    df_filtrados["Classe_Vip"]
    .astype(str)
    .str.upper()
    .str.strip()
    .replace({"A": "CLASSE A", "B": "CLASSE B", "C": "CLASSE C"})
)
cores_scatter = classe_scatter.map(cores_classe).fillna("#B0C4DE")

ax.scatter(
    df_filtrados["Quantidade_Vendida"],
    df_filtrados["Receita_Total"],
    s=df_filtrados["Preco_Medio"] * 2,
    c=cores_scatter,
    alpha=0.75,
)

ax.set_xlabel("Quantidade Vendida")
ax.set_ylabel("Receita Total")
ax.set_title("Matriz de Performance")
ax.legend(
    handles=[
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Classe A",
            markerfacecolor=cores_classe["CLASSE A"],
            markersize=10,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Classe B",
            markerfacecolor=cores_classe["CLASSE B"],
            markersize=10,
        ),
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label="Classe C",
            markerfacecolor=cores_classe["CLASSE C"],
            markersize=10,
        ),
    ]
)

# KPI de Concentração
percentual_a = df_filtrados[df_filtrados["Classe_Vip"] == "Classe A"]["Percentual"].sum()
percentual_b = df_filtrados[df_filtrados["Classe_Vip"] == "Classe B"]["Percentual"].sum()
percentual_c = df_filtrados[df_filtrados["Classe_Vip"] == "Classe C"]["Percentual"].sum()

# Relatório CSV
csv = df_filtrados.to_csv(index=False)
st.download_button(
    label="Baixar Relatório",
    data=csv,
    file_name="analise_abc_produtos.csv",
    mime="text/csv"
)

st.subheader("Tabela de Produtos")
st.dataframe(df_filtrados)

st.subheader("Top 10 Produtos por Receita")
st.pyplot(fig_top10)

st.subheader("Pareto por Categoria")
st.pyplot(fig_pareto)

st.subheader("Matriz de Performance")
st.pyplot(fig)

st.subheader("KPI de Concentração")
st.metric("Concentração Classe A", f"{percentual_a:.2f}%", delta=f"{percentual_a:.2f}%")
st.metric("Concentração Classe B", f"{percentual_b:.2f}%", delta=f"{percentual_b:.2f}%")
st.metric("Concentração Classe C", f"{percentual_c:.2f}%", delta=f"{percentual_c:.2f}%")