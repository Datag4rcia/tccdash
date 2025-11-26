import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Campanhas",
    page_icon="📊",
    layout="wide"
)

# Dicionários de decodificação - AJUSTE CONFORME SEUS DADOS
DECODIFICACAO = {
    'campaign': {
        0: 'Email Marketing',
        1: 'Telemarketing',
        2: 'Redes Sociais',
        3: 'SMS',
        4: 'Publicidade Online',
        # Adicione mais conforme necessário
    },
    'previousy': {
        0: 'Não',
        1: 'Sim',
    },
    'persona': {
        0: 'Estudante',
        1: 'Empresário',
        2: 'Profissional Liberal',
        3: 'Aposentado',
        4: 'Funcionário Público',
        # Adicione mais conforme necessário
    },
    'resultado': {
        0: 'Falha',
        1: 'Sucesso',
    }
}

# Título
st.title("📊 Dashboard de Análise de Campanhas")
st.markdown("---")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregar arquivo CSV", type=['csv'])

if uploaded_file is not None:
    # Carregar dados
    df = pd.read_csv(uploaded_file)
    
    # Limpar nomes das colunas
    df.columns = df.columns.str.strip().str.lower()
    
    # Mostrar preview dos dados originais (codificados)
    with st.expander("🔍 Ver dados originais (codificados)"):
        st.dataframe(df.head(10))
        st.write("**Colunas disponíveis:**", df.columns.tolist())
    
    # Decodificar as colunas
    df_decoded = df.copy()
    for col in ['campaign', 'previousy', 'persona', 'resultado']:
        if col in df_decoded.columns:
            # Converter para numérico se necessário
            df_decoded[col] = pd.to_numeric(df_decoded[col], errors='coerce')
            # Aplicar decodificação
            if col in DECODIFICACAO:
                df_decoded[col] = df_decoded[col].map(DECODIFICACAO[col]).fillna('Desconhecido')
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Campanha
    campanhas = ['Todas'] + sorted(df_decoded['campaign'].unique().tolist())
    campanha_selecionada = st.sidebar.selectbox("Campanha", campanhas)
    
    # Filtro de Persona
    personas = ['Todas'] + sorted(df_decoded['persona'].unique().tolist())
    persona_selecionada = st.sidebar.selectbox("Persona", personas)
    
    # Aplicar filtros
    df_filtrado = df_decoded.copy()
    if campanha_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['campaign'] == campanha_selecionada]
    if persona_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['persona'] == persona_selecionada]
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_registros = len(df_filtrado)
    
    # Calcular taxa de sucesso
    if total_registros > 0:
        taxa_sucesso = (df_filtrado['resultado'] == 'Sucesso').sum() / total_registros * 100
    else:
        taxa_sucesso = 0
    
    # Calcular taxa de previousy
    if total_registros > 0:
        taxa_previousy = (df_filtrado['previousy'] == 'Sim').sum() / total_registros * 100
    else:
        taxa_previousy = 0
    
    personas_unicas = df_filtrado['persona'].nunique()
    
    with col1:
        st.metric("Total de Registros", f"{total_registros:,}")
    with col2:
        st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
    with col3:
        st.metric("Contato Prévio", f"{taxa_previousy:.1f}%")
    with col4:
        st.metric("Personas Únicas", personas_unicas)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribuição por Campanha")
        campaign_counts = df_filtrado['campaign'].value_counts().reset_index()
        campaign_counts.columns = ['campaign', 'count']
        fig1 = px.bar(campaign_counts, x='campaign', y='count',
                      color='count',
                      color_continuous_scale='Blues',
                      labels={'campaign': 'Campanha', 'count': 'Quantidade'})
        fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Resultado das Ações")
        resultado_counts = df_filtrado['resultado'].value_counts().reset_index()
        resultado_counts.columns = ['resultado', 'count']
        colors = {'Sucesso': '#10b981', 'Falha': '#ef4444', 'Desconhecido': '#gray'}
        fig2 = px.pie(resultado_counts, values='count', names='resultado',
                      color='resultado',
                      color_discrete_map=colors)
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("👥 Distribuição por Persona")
        persona_counts = df_filtrado['persona'].value_counts().reset_index()
        persona_counts.columns = ['persona', 'count']
        fig3 = px.bar(persona_counts, x='persona', y='count',
                      color='count',
                      color_continuous_scale='Greens',
                      labels={'persona': 'Persona', 'count': 'Quantidade'})
        fig3.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.subheader("📞 Contato Prévio (Previousy)")
        previousy_counts = df_filtrado['previousy'].value_counts().reset_index()
        previousy_counts.columns = ['previousy', 'count']
        colors_prev = {'Sim': '#f59e0b', 'Não': '#8b5cf6'}
        fig4 = px.pie(previousy_counts, values='count', names='previousy',
                      color='previousy',
                      color_discrete_map=colors_prev)
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # Análise cruzada
    st.subheader("📊 Análise Cruzada: Resultado por Campanha")
    cross_tab = pd.crosstab(df_filtrado['campaign'], df_filtrado['resultado'])
    fig5 = px.bar(cross_tab, barmode='group',
                  labels={'value': 'Quantidade', 'campaign': 'Campanha'},
                  color_discrete_sequence=['#10b981', '#ef4444'])
    fig5.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("---")
    
    # Análise: Taxa de Sucesso por Campanha
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Taxa de Sucesso por Campanha")
        success_by_campaign = df_filtrado.groupby('campaign').apply(
            lambda x: (x['resultado'] == 'Sucesso').sum() / len(x) * 100
        ).reset_index()
        success_by_campaign.columns = ['campaign', 'taxa_sucesso']
        fig6 = px.bar(success_by_campaign, x='campaign', y='taxa_sucesso',
                      color='taxa_sucesso',
                      color_continuous_scale='RdYlGn',
                      labels={'campaign': 'Campanha', 'taxa_sucesso': 'Taxa de Sucesso (%)'})
        fig6.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig6, use_container_width=True)
    
    with col2:
        st.subheader("📈 Taxa de Sucesso por Persona")
        success_by_persona = df_filtrado.groupby('persona').apply(
            lambda x: (x['resultado'] == 'Sucesso').sum() / len(x) * 100
        ).reset_index()
        success_by_persona.columns = ['persona', 'taxa_sucesso']
        fig7 = px.bar(success_by_persona, x='persona', y='taxa_sucesso',
                      color='taxa_sucesso',
                      color_continuous_scale='RdYlGn',
                      labels={'persona': 'Persona', 'taxa_sucesso': 'Taxa de Sucesso (%)'})
        fig7.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig7, use_container_width=True)
    
    st.markdown("---")
    
    # Tabela de dados decodificados
    st.subheader("📋 Dados Filtrados (Decodificados)")
    st.dataframe(df_filtrado, use_container_width=True, height=400)
    
    # Estatísticas resumidas
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Resumo Estatístico")
        st.write(f"**Total de registros no dataset:** {len(df):,}")
        st.write(f"**Registros após filtros:** {len(df_filtrado):,}")
        st.write(f"**Campanhas únicas:** {df_decoded['campaign'].nunique()}")
        st.write(f"**Personas únicas:** {df_decoded['persona'].nunique()}")
    
    with col2:
        st.subheader("🎯 Top Performers")
        top_campaign = df_filtrado['campaign'].value_counts().head(1)
        if len(top_campaign) > 0:
            st.write(f"**Campanha mais frequente:** {top_campaign.index[0]} ({top_campaign.values[0]} registros)")
        
        top_persona = df_filtrado['persona'].value_counts().head(1)
        if len(top_persona) > 0:
            st.write(f"**Persona mais frequente:** {top_persona.index[0]} ({top_persona.values[0]} registros)")
    
    # Download dos dados filtrados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download dados filtrados (CSV)",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )
    
    # Legenda de decodificação
    with st.expander("📖 Legenda de Decodificação"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("**Campaign:**")
            for k, v in DECODIFICACAO['campaign'].items():
                st.write(f"{k} = {v}")
        with col2:
            st.write("**Previousy:**")
            for k, v in DECODIFICACAO['previousy'].items():
                st.write(f"{k} = {v}")
        with col3:
            st.write("**Persona:**")
            for k, v in DECODIFICACAO['persona'].items():
                st.write(f"{k} = {v}")
        with col4:
            st.write("**Resultado:**")
            for k, v in DECODIFICACAO['resultado'].items():
                st.write(f"{k} = {v}")

else:
    st.info("👆 Por favor, faça upload do arquivo meus_dados.csv para visualizar o dashboard")
    st.markdown("""
    ### Formato esperado do CSV:
    O arquivo deve conter as seguintes colunas com valores codificados (números):
    - **campaign**: Código da campanha (0, 1, 2, etc.)
    - **previousy**: Contato prévio (0 = Não, 1 = Sim)
    - **persona**: Código da persona (0, 1, 2, etc.)
    - **resultado**: Resultado (0 = Falha, 1 = Sucesso)
    
    ### Exemplo de dados codificados:
    ```
    campaign,previousy,persona,resultado
    0,1,1,1
    2,0,0,0
    1,1,2,1
    ```
    
    **Observação:** Ajuste os dicionários de decodificação no código conforme seus dados reais.
    """)
