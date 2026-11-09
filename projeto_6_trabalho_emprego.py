"""
PROJETO 6: Trabalho, Emprego, Formalidade e Rendimento
Projeto Integrador: Números que Falam — Descobrindo o Brasil
Startup DataVision Analytics • Ensino Médio Técnico em Informática
Bases Governamentais: IBGE PNAD Contínua (Trabalho e Rendimento 2012–2022) e CAGED
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da Página
st.set_page_config(
    page_title="Projeto 6: Trabalho & Informalidade | DataVision",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        padding: 1.3rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.2rem;
    }
    .header-box h1 { color: white; margin-bottom: 0.2rem; font-size: 2rem; }
    .header-box p { color: #E0E7FF; margin-bottom: 0; font-size: 1rem; }
    .badge {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 3px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Funções Matemáticas Embutidas
def calcular_estatisticas(series: pd.Series) -> dict:
    s = series.dropna()
    if len(s) == 0:
        return {}
    media = float(s.mean())
    mediana = float(s.median())
    q1 = float(np.percentile(s, 25))
    q2 = mediana
    q3 = float(np.percentile(s, 75))
    iqr = q3 - q1
    desvio = float(s.std())
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    outliers = s[(s < lim_inf) | (s > lim_sup)]
    return {
        "media": media,
        "mediana": mediana,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "iqr": iqr,
        "desvio_padrao": desvio,
        "limite_inferior": lim_inf,
        "limite_superior": lim_sup,
        "qtd_outliers": len(outliers),
        "pct_outliers": (len(outliers) / len(s)) * 100
    }

# Carregamento com Fallback
@st.cache_data
def carregar_dados():
    arquivo = "dados_trabalho.csv"
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
        
    np.random.seed(42)
    n = 3000
    ufs = ["SP", "RJ", "MG", "BA", "PE", "CE", "PR", "RS", "GO", "DF", "AM", "PA"]
    setores = ["Comércio", "Serviços", "Indústria", "Agropecuária", "Construção Civil"]
    escolaridades = ["Fundamental Incompleto", "Médio Completo", "Superior Completo"]
    vinculos = ["Formal (Com Carteira / CNPJ)", "Informal / Sem Carteira"]
    anos = [2012, 2022]
    
    rows = []
    for i in range(n):
        ano = int(np.random.choice(anos))
        uf = np.random.choice(ufs)
        setor = np.random.choice(setores, p=[0.25, 0.40, 0.15, 0.10, 0.10])
        sexo = np.random.choice(["Mulher", "Homem"])
        esc = np.random.choice(escolaridades, p=[0.30, 0.50, 0.20])
        
        # Desocupação
        p_desoc = 0.08 if ano == 2022 else 0.11
        if sexo == "Mulher":
            p_desoc += 0.03
        desocupado = 1 if np.random.rand() < p_desoc else 0
        
        # Vínculo e Rendimento
        if desocupado == 1:
            vinculo = "Desocupado"
            renda = 0.0
        else:
            p_inf = 0.45 if uf in ["BA", "PE", "CE", "PA", "AM"] else 0.32
            vinculo = np.random.choice(vinculos, p=[1 - p_inf, p_inf])
            
            base_sal = 1800 if vinculo == "Informal / Sem Carteira" else 3200
            if esc == "Superior Completo":
                base_sal *= 2.4
            elif esc == "Fundamental Incompleto":
                base_sal *= 0.75
            if sexo == "Mulher":
                base_sal *= 0.82
                
            # Assimetria positiva (outliers de altos salários)
            renda = float(np.random.lognormal(mean=np.log(base_sal), sigma=0.45))
            
        rows.append({
            "id": 600000 + i,
            "ano": ano,
            "uf": uf,
            "setor_economico": setor,
            "sexo": sexo,
            "escolaridade": esc,
            "tipo_vinculo": vinculo,
            "desocupado": desocupado,
            "rendimento_mensal": round(renda, 2)
        })
    df_gen = pd.DataFrame(rows)
    df_gen.to_csv(arquivo, index=False)
    return df_gen

df = carregar_dados()

# Cabeçalho
st.markdown("""
<div class="header-box">
    <h1>💼 Projeto 6: Trabalho, Formalidade e População Empregada</h1>
    <p>Monitoramento da Taxa de Desocupação (2012 x 2022), Informalidade e Paridade Salarial de Gênero</p>
    <div class="badge">Startup DataVision Analytics • Foco: Ministério do Trabalho, Indústria e Sebrae</div>
</div>
""", unsafe_allow_html=True)

# Filtros na Barra Lateral
st.sidebar.markdown("### 🏢 **DataVision Analytics**")
st.sidebar.markdown("**Consultoria Estratégica em Mercado de Trabalho**")
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros de Análise")

ufs_sel = st.sidebar.multiselect("Filtrar Estado (UF):", sorted(df["uf"].unique()), default=sorted(df["uf"].unique()))
setores_sel = st.sidebar.multiselect("Setor Econômico:", sorted(df["setor_economico"].unique()), default=sorted(df["setor_economico"].unique()))
anos_sel = st.sidebar.multiselect("Ano de Análise:", sorted(df["ano"].unique()), default=sorted(df["ano"].unique()))

df_filtrado = df[(df["uf"].isin(ufs_sel)) & (df["setor_economico"].isin(setores_sel)) & (df["ano"].isin(anos_sel))]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

df_ocupados = df_filtrado[df_filtrado["rendimento_mensal"] > 0]
stats = calcular_estatisticas(df_ocupados["rendimento_mensal"])

# Cards de KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Média Salarial", f"R$ {stats['media']:,.2f}")
c2.metric("Mediana Salarial (Q2)", f"R$ {stats['mediana']:,.2f}")
c3.metric("IQR Salarial", f"R$ {stats['iqr']:,.2f}")
c4.metric("Desvio Padrão", f"R$ {stats['desvio_padrao']:,.2f}")

# Abas
t1, t2, t3, t4 = st.tabs([
    "🎯 Perguntas de Negócio",
    "📐 Assimetria Média vs Mediana",
    "📰 Mercado de Trabalho & CAGED",
    "🏛️ PNAD Contínua & Séries Históricas"
])

with t1:
    st.markdown("#### 1. Formalidade vs Informalidade por Estado")
    comp_vinc = df_filtrado[df_filtrado["tipo_vinculo"] != "Desocupado"].groupby(["uf", "tipo_vinculo"]).size().reset_index(name="trabalhadores")
    fig_vinc = px.bar(
        comp_vinc, x="uf", y="trabalhadores", color="tipo_vinculo", barmode="group",
        title="Trabalhadores Formais vs Informais por Estado",
        color_discrete_map={"Formal (Com Carteira / CNPJ)": "#10B981", "Informal / Sem Carteira": "#F59E0B"}
    )
    st.plotly_chart(fig_vinc, width='stretch')
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("#### 2. Desocupação por Gênero (2012 vs 2022)")
        taxa_desoc = df_filtrado.groupby(["ano", "sexo"])["desocupado"].mean().reset_index()
        taxa_desoc["taxa_pct"] = (taxa_desoc["desocupado"] * 100).round(1)
        fig_desoc = px.bar(
            taxa_desoc, x="sexo", y="taxa_pct", color="ano", barmode="group",
            title="Taxa de Desocupação por Gênero (%)", labels={"taxa_pct": "Taxa de Desocupação (%)"}
        )
        st.plotly_chart(fig_desoc, width='stretch')
        
    with col_t2:
        st.markdown("#### 3. Taxa de Desocupação por Estado (2012 x 2022)")
        desoc_uf = df_filtrado.groupby(["uf", "ano"])["desocupado"].mean().reset_index()
        desoc_uf["desocupado_pct"] = (desoc_uf["desocupado"] * 100).round(1)
        fig_uf_desoc = px.bar(
            desoc_uf, x="uf", y="desocupado_pct", color="ano", barmode="group",
            title="Taxa de Desocupação por Estado (%)"
        )
        st.plotly_chart(fig_uf_desoc, width='stretch')
        
    st.info("💡 **Conclusão para a Ministra e Sebrae:** A informalidade permanece como o principal amortecedor da desocupação, especialmente nos serviços. As mulheres continuam sofrendo taxa de desocupação superior e rendimento médio cerca de 18% a 20% inferior aos homens para cargos equivalentes.")

with t2:
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("#### Histograma Salarial: Assimetria Média vs Mediana")
        fig_hist = px.histogram(df_ocupados, x="rendimento_mensal", nbins=40, title="Distribuição do Rendimento do Trabalho (R$)")
        fig_hist.add_vline(x=stats['media'], line_dash="dash", line_color="red", annotation_text=f"Média: R${stats['media']:.0f}")
        fig_hist.add_vline(x=stats['mediana'], line_dash="dot", line_color="green", annotation_text=f"Mediana: R${stats['mediana']:.0f}")
        st.plotly_chart(fig_hist, width='stretch')
    with col_h2:
        st.markdown("#### Boxplot de Renda por Escolaridade")
        fig_box = px.box(
            df_ocupados, x="escolaridade", y="rendimento_mensal", color="escolaridade", points="outliers",
            title="Rendimento Estratificado por Nível de Escolaridade"
        )
        st.plotly_chart(fig_box, width='stretch')

with t3:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
        ### 📈 PNAD Contínua e Criação de Vagas pelo CAGED
        *Fonte: Ministério do Trabalho / IBGE*  
        O aquecimento dos setores de serviços e comércio impulsiona a recuperação do emprego formal, embora a remuneração de entrada continue pressionada pela inflação e produtividade.
        """)
        st.image("https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&auto=format&fit=crop&q=80", caption="Geração de empregos e ambientes corporativos brasileiros.", width='stretch')
    with col_m2:
        st.markdown("""
        ### 🏢 O Papel do Pequeno Negócio e do MEI
        Micro e pequenas empresas são responsáveis por mais de 70% dos novos postos com carteira assinada, demandando capacitação e crédito orientado.
        """)
        st.image("https://images.unsplash.com/photo-1556742049-0a67e557224f?w=800&auto=format&fit=crop&q=80", caption="Empreendedorismo e comércio local fortalecendo a economia.", width='stretch')

with t4:
    st.markdown("### 🏛️ PNAD Contínua, Séries Temporais & Microdados")
    st.write("Bases governamentais oficiais para monitoramento do mercado de trabalho e emprego:")
    
    c_w1, c_w2 = st.columns(2)
    with c_w1:
        st.markdown("""
        #### 📊 SIDRA — PNAD Contínua (Trabalho & Rendimento):
        - **Séries Históricas:** Módulos anuais e trimestrais cobrindo o período de 2012 a 2022.
        - **Indicadores Chave:** Taxa de desocupação, taxa de informalidade, rendimento médio e mediano real habitual.
        - 🔗 **Link Oficial:** [SIDRA — PNAD Contínua (IBGE)](https://sidra.ibge.gov.br/pesquisa/pnadca/)
        
        #### 💾 Portal de Downloads de Microdados:
        - **Arquivos Ponderados:** Permite calcular o coeficiente de variação e a massa de rendimentos por unidade da federação.
        - 🔗 **Link Oficial:** [IBGE — Portal de Downloads](https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html)
        """)
    with c_w2:
        st.markdown("""
        #### 🔌 APIs Públicas do IBGE & Base dos Dados:
        - **API de Agregados (SIDRA):** [servicodados.ibge.gov.br/api/docs/agregados](https://servicodados.ibge.gov.br/api/docs/agregados) — Extração automatizada das taxas de desocupação e informalidade da PNADC.
        - **Base dos Dados (BigQuery):** [basedosdados.org](https://basedosdados.org/) — Tabela `basedosdados.br_ibge_pnadc.microdados` para consultas rápidas em SQL.
        - **Rigor Estatístico BNCC:** Demonstração da distorção da média salarial em relação à mediana provocada pela alta desigualdade de renda (assimetria positiva severa).
        """)

st.markdown("---")
st.caption("DataVision Analytics • Projeto Integrador • Ensino Médio Técnico em Informática (Turma 3D1)")
