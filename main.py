import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

# 🎨 Estilo visual
sns.set_style("whitegrid")
st.set_page_config(page_title="Amazon Deals Insights", layout="wide")

# 📂 Caminho absoluto do JSON
json_path = Path(__file__).parent / "amazon_data.json"

# 📥 Função para carregar os dados
@st.cache_data
def load_data(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Verifica se a estrutura esperada existe
        if "data" in data and "deals" in data["data"]:
            return pd.json_normalize(data["data"]["deals"])
        else:
            st.error("❌ Estrutura inesperada no JSON. Esperado: data → deals.")
            return pd.DataFrame()
    else:
        st.error(f"❌ Arquivo não encontrado em: {path}")
        return pd.DataFrame()

# 🔄 Carregando os dados
df = load_data(json_path)

# 🧹 Limpeza e conversão
if not df.empty:
    # Converte colunas numéricas com segurança
    df["savings_percentage"] = pd.to_numeric(df.get("savings_percentage"), errors="coerce")
    df["list_price.amount"] = pd.to_numeric(df.get("list_price.amount"), errors="coerce")

    # Trata a coluna de título
    if "deal_title" in df.columns:
        df["deal_title"] = df["deal_title"].astype(str).str.slice(0, 50)
    else:
        df["deal_title"] = "Sem título"

    # 🔝 Top 10 maiores descontos
    df_top = df.sort_values("savings_percentage", ascending=False).head(10)

    # 🏷️ Título
    st.title("📦 Dashboard de Ofertas Amazon (API JSON)")

    # 📊 Gráfico 1: Top 10 maiores descontos
    st.subheader("🔝 Top 10 produtos com maiores descontos (%)")
    fig1, ax1 = plt.subplots()
    sns.barplot(x="savings_percentage", y="deal_title", data=df_top, palette="viridis", ax=ax1)
    ax1.set_xlabel("Desconto (%)")
    ax1.set_ylabel("Produto")
    st.pyplot(fig1)

    # 📈 Gráfico 2: Distribuição dos descontos
    st.subheader("📈 Distribuição dos descontos (%)")
    fig2, ax2 = plt.subplots()
    sns.histplot(df["savings_percentage"], bins=20, kde=True, color='teal', ax=ax2)
    ax2.set_xlabel("Desconto (%)")
    ax2.set_ylabel("Frequência")
    st.pyplot(fig2)

    # 💰 Gráfico 3: Preço vs Desconto
    st.subheader("💰 Preço original vs Desconto (%)")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x='list_price.amount', y='savings_percentage', data=df, color='coral', alpha=0.5, ax=ax3)
    ax3.set_xlabel("Preço original (US$)")
    ax3.set_ylabel("Desconto (%)")
    st.pyplot(fig3)

else:
    st.warning("⚠️ Nenhum dado disponível para exibir os gráficos.")
