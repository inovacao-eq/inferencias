import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Análise de Forms", page_icon="📊", layout="wide")

st.title("📊 Ferramenta de Análise do Google Forms")
st.write("Faça o upload da sua planilha de respostas para gerar estatísticas e gráficos automaticamente.")

# Área de upload de arquivo
arquivo_upload = st.file_uploader("Selecione o arquivo de respostas (CSV ou Excel)", type=["csv", "xlsx"])

if arquivo_upload is not None:
    # Carregando os dados
    try:
        if arquivo_upload.name.endswith('.csv'):
            # Google Forms geralmente exporta CSV com codificação utf-8
            df = pd.read_csv(arquivo_upload, encoding='utf-8')
        else:
            df = pd.read_excel(arquivo_upload)
            
        # Remover a coluna de "Carimbo de data/hora" se não for necessária para a análise estrita
        colunas_uteis = [col for col in df.columns if col.lower() not in ['carimbo de data/hora', 'timestamp']]
        
        st.success("Arquivo carregado com sucesso!")
        
        # --- SEÇÃO 1: Visualização dos Dados Brutos ---
        st.header("1. Visão Geral dos Dados")
        st.dataframe(df.head(10)) # Mostra as 10 primeiras linhas
        st.write(f"**Total de respostas (linhas):** {df.shape[0]}")
        st.write(f"**Total de perguntas (colunas):** {df.shape[1]}")

        st.divider()

        # --- SEÇÃO 2: Estatísticas Gerais ---
        st.header("2. Estatísticas Descritivas")
        st.write("Resumo estatístico das respostas numéricas e categóricas:")
        st.dataframe(df.describe(include='all').fillna('-'))

        st.divider()

        # --- SEÇÃO 3: Análise Individual por Pergunta ---
        st.header("3. Análise por Pergunta")
        
        # Selecionar a coluna/pergunta para analisar
        pergunta_selecionada = st.selectbox("Selecione uma pergunta para gerar o gráfico:", colunas_uteis)
        
        # Limpar valores nulos da coluna selecionada para a análise
        dados_pergunta = df[pergunta_selecionada].dropna()
        
        # Verifica se o dado é numérico ou categórico (texto/múltipla escolha)
        if pd.api.types.is_numeric_dtype(dados_pergunta):
            st.subheader(f"Distribuição de: {pergunta_selecionada}")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                # Gráfico de Histograma para números
                fig = px.histogram(df, x=pergunta_selecionada, nbins=20, marginal="box", 
                                   color_discrete_sequence=['#4CAF50'])
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                # Métricas rápidas
                st.metric("Média", round(dados_pergunta.mean(), 2))
                st.metric("Mediana", round(dados_pergunta.median(), 2))
                st.metric("Valor Máximo", dados_pergunta.max())
                st.metric("Valor Mínimo", dados_pergunta.min())
                
        else:
            st.subheader(f"Frequência de respostas: {pergunta_selecionada}")
            
            # Contagem de respostas para perguntas de texto/múltipla escolha
            contagem = dados_pergunta.value_counts().reset_index()
            contagem.columns = ['Resposta', 'Quantidade']
            
            col1, col2 = st.columns([2, 1])
            with col1:
                # Gráfico de barras
                fig = px.bar(contagem, x='Quantidade', y='Resposta', orientation='h',
                             color='Quantidade', color_continuous_scale='Blues')
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                # Tabela de frequência
                st.dataframe(contagem, hide_index=True)

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")