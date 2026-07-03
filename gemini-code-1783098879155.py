import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats

# Configuração da página
st.set_page_config(page_title="Análise Estatística de Forms", page_icon="📊", layout="wide")

st.title("📊 Ferramenta de Análise Avançada - Google Forms")
st.write("Faça o upload da sua planilha para gerar estatísticas descritivas e testes de hipóteses (Qui-Quadrado, Teste T).")

# Área de upload
arquivo_upload = st.file_uploader("Selecione o arquivo de respostas (CSV ou Excel)", type=["csv", "xlsx"])

if arquivo_upload is not None:
    try:
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload, encoding='utf-8')
        else:
            df = pd.read_excel(arquivo_upload)
            
        # Filtrar colunas úteis (ignora data/hora)
        colunas_uteis = [col for col in df.columns if col.lower() not in ['carimbo de data/hora', 'timestamp']]
        
        st.success("Arquivo carregado com sucesso!")
        
        # Abas para organizar a ferramenta
        tab_geral, tab_individual, tab_cruzamento = st.tabs([
            "1. Visão Geral", 
            "2. Análise por Pergunta", 
            "3. Cruzamento de Dados (Testes Estatísticos)"
        ])

        # --- ABA 1: VISÃO GERAL ---
        with tab_geral:
            st.header("Visão Geral dos Dados")
            st.dataframe(df.head(10))
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Total de Respostas", df.shape[0])
            col_m2.metric("Total de Perguntas", len(colunas_uteis))
            
            st.subheader("Resumo Descritivo Geral")
            st.dataframe(df.describe(include='all').fillna('-'))

        # --- ABA 2: ANÁLISE POR PERGUNTA ---
        with tab_individual:
            st.header("Análise Univariada")
            pergunta_selecionada = st.selectbox("Escolha uma pergunta:", colunas_uteis, key="sb_individual")
            dados_pergunta = df[pergunta_selecionada].dropna()
            
            if pd.api.types.is_numeric_dtype(dados_pergunta):
                st.subheader(f"Análise Numérica: {pergunta_selecionada}")
                
                # Cálculos Estatísticos
                media = dados_pergunta.mean()
                desvio_padrao = dados_pergunta.std()
                variancia = dados_pergunta.var()
                mediana = dados_pergunta.median()
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    fig = px.histogram(df, x=pergunta_selecionada, nbins=20, marginal="box",
                                       title="Distribuição das Respostas", color_discrete_sequence=['#4CAF50'])
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.metric("Média É", round(media, 2))
                    st.metric("Desvio Padrão (SD)", round(desvio_padrao, 2))
                    st.metric("Mediana", round(mediana, 2))
                    st.metric("Variância", round(variancia, 2))
                    st.metric("Mínimo / Máximo", f"{dados_pergunta.min()} / {dados_pergunta.max()}")
                
                st.info(f"**Interpretação do Desvio Padrão:** A maioria das suas respostas varia em torno de "
                        f"**{round(media - desvio_padrao, 2)}** a **{round(media + desvio_padrao, 2)}** "
                        f"(Média ± 1 Desvio Padrão).")

            else:
                st.subheader(f"Análise Categórica: {pergunta_selecionada}")
                contagem = dados_pergunta.value_counts().reset_index()
                contagem.columns = ['Resposta', 'Frequência Absoluta']
                contagem['Frequência Relativa (%)'] = round((contagem['Frequência Absoluta'] / len(dados_pergunta)) * 100, 2)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    fig = px.bar(contagem, x='Frequência Absoluta', y='Resposta', orientation='h',
                                 title="Contagem de Respostas", color='Frequência Absoluta', color_continuous_scale='Purples')
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    st.write("**Tabela de Frequências**")
                    st.dataframe(contagem, hide_index=True)

        # --- ABA 3: CRUZAMENTO DE DADOS (TESTES) ---
        with tab_cruzamento:
            st.header("Testes Estatísticos de Associação")
            st.write("Cruze duas perguntas para saber se uma influencia a outra estatisticamente.")
            
            tipo_teste = st.radio("Escolha o tipo de cruzamento:", [
                "Duas perguntas de múltipla escolha (Teste Qui-Quadrado)",
                "Uma pergunta de escolha vs. Uma pergunta numérica (Teste T de Student)"
            ])
            
            # --- CASO 1: QUI-QUADRADO ---
            if "Qui-Quadrado" in tipo_teste:
                st.subheader("🎲 Teste de Qui-Quadrado de Independência")
                st.write("Ideal para testar a associação entre duas variáveis categóricas (ex: 'Gênero' vs 'Opinião').")
                
                var1 = st.selectbox("Selecione a Primeira Pergunta (Linha):", colunas_uteis, key="v1")
                var2 = st.selectbox("Selecione a Segunda Pergunta (Coluna):", colunas_uteis, key="v2")
                
                if var1 == var2:
                    st.warning("Por favor, selecione duas perguntas diferentes.")
                else:
                    # Criar tabela de contingência (Tabela Cruzada)
                    tabela_cruzada = pd.crosstab(df[var1], df[var2])
                    st.write("**Tabela de Contingência (Valores Observados):**")
                    st.dataframe(tabela_cruzada)
                    
                    # Rodar o Teste Qui-Quadrado
                    try:
                        chi2, p_valor, dof, esperados = stats.chi2_contingency(tabela_cruzada)
                        
                        st.markdown("---")
                        st.subheader("Resultado do Teste")
                        col_q1, col_q2 = st.columns(2)
                        col_q1.metric("Valor Qui-Quadrado", round(chi2, 4))
                        col_q2.metric("p-valor", round(p_valor, 5))
                        
                        # Interpretação do p-valor
                        if p_valor < 0.05:
                            st.success(f"📌 **Resultado Estatisticamente Significativo (p < 0.05).**\n\n"
                                       f"Como o p-valor ({round(p_valor,5)}) é menor que 5%, rejeitamos a hipótese nula. "
                                       f"Existe uma **associação significativa** entre '{var1}' e '{var2}'. "
                                       f"As respostas de uma pergunta parecem depender ou estar ligadas à outra.")
                        else:
                            st.error(f"📌 **Resultado NÃO Significativo (p >= 0.05).**\n\n"
                                     f"Como o p-valor ({round(p_valor,5)}) é maior ou igual a 5%, não podemos afirmar que há associação. "
                                     f"As variáveis '{var1}' e '{var2}' parecem ser **independentes** uma da outra.")
                    except Exception as e:
                        st.error(f"Não foi possível calcular o Qui-Quadrado para essas colunas. Certifique-se de que são categóricas. Erro: {e}")

            # --- CASO 2: TESTE T ---
            else:
                st.subheader("🧪 Teste T de Student (Para 2 Grupos)")
                st.write("Compara a média de um grupo numérico entre duas categorias (ex: comparar a 'Nota' entre 'Homens' e 'Mulheres').")
                
                var_cat = st.selectbox("Selecione a pergunta categórica (Ex: Gênero):", colunas_uteis, key="v_cat")
                var_num = st.selectbox("Selecione a pergunta numérica (Ex: Idade ou Nota):", colunas_uteis, key="v_num")
                
                dados_filtrados = df[[var_cat, var_num]].dropna()
                grupos = dados_filtrados[var_cat].unique()
                
                if len(grupos) != 2:
                    st.warning(f"O Teste T padrão precisa que a pergunta categórica tenha exatamente **2 grupos/opções** de resposta. Sua coluna tem {len(grupos)} grupos ({grupos}).")
                elif not pd.api.types.is_numeric_dtype(df[var_num]):
                    st.error("A segunda pergunta precisa ser estritamente numérica.")
                else:
                    g1 = dados_filtrados[dados_filtrados[var_cat] == grupos[0]][var_num]
                    g2 = dados_filtrados[dados_filtrados[var_cat] == grupos[1]][var_num]
