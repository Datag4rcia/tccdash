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
        0: 'Campanha 0',
        1: 'Campanha 1',
        2: 'Campanha 2',
        3: 'Campanha 3',
        4: 'Campanha 4',
    },
    'previousy': {
        0: 'Não',
        1: 'Sim',
    },
    'previous': {
        0: 'Não',
        1: 'Sim',
    },
    'persona': {
        0: 'Persona 0',
        1: 'Persona 1',
        2: 'Persona 2',
        3: 'Persona 3',
        4: 'Persona 4',
        5: 'Persona 5',
        6: 'Persona 6',
        7: 'Persona 7',
        8: 'Persona 8',
        9: 'Persona 9',
    },
    'resultado': {
        0: 'Falha',
        1: 'Sucesso',
    },
    'result': {
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
    
    # Mostrar colunas disponíveis
    st.sidebar.info(f"**Colunas detectadas:** {', '.join(df.columns.tolist())}")
    
    # Mostrar preview dos dados originais (codificados)
    with st.expander("🔍 Ver dados originais (codificados) - PRIMEIRAS 20 LINHAS"):
        st.dataframe(df.head(20))
        st.write("**Total de linhas:**", len(df))
    
    # Mapear nomes de colunas (flexível para diferentes nomes)
    col_map = {}
    for col in df.columns:
        if 'campaign' in col or 'campanha' in col:
            col_map['campaign'] = col
        elif 'previous' in col or 'previo' in col:
            col_map['previousy'] = col
        elif 'persona' in col:
            col_map['persona'] = col
        elif 'result' in col or 'resultado' in col:
            col_map['resultado'] = col
    
    st.sidebar.success(f"**Mapeamento:** {col_map}")
    
    # Criar DataFrame decodificado
    df_decoded = df.copy()
    
    # Decodificar cada coluna encontrada
    for standard_name, original_name in col_map.items():
        if original_name in df_decoded.columns:
            # Converter para numérico
            df_decoded[standard_name] = pd.to_numeric(df_decoded[original_name], errors='coerce')
            # Aplicar decodificação
            if standard_name in DECODIFICACAO:
                df_decoded[standard_name] = df_decoded[standard_name].map(DECODIFICACAO[standard_name])
            # Se não houver mapeamento, usar o original
            if df_decoded[standard_name].isna().all():
                df_decoded[standard_name] = df_decoded[original_name].astype(str)
            # Preencher valores NaN
            df_decoded[standard_name] = df_decoded[standard_name].fillna('Desconhecido')
    
    # Verificar quais colunas foram processadas
    has_campaign = 'campaign' in df_decoded.columns
    has_previousy = 'previousy' in df_decoded.columns
    has_persona = 'persona' in df_decoded.columns
    has_resultado = 'resultado' in df_decoded.columns
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Campanha
    if has_campaign:
        campanhas = ['Todas'] + sorted([str(x) for x in df_decoded['campaign'].unique()])
        campanha_selecionada = st.sidebar.selectbox("Campanha", campanhas)
    else:
        campanha_selecionada = 'Todas'
    
    # Filtro de Persona
    if has_persona:
        personas = ['Todas'] + sorted([str(x) for x in df_decoded['persona'].unique()])
        persona_selecionada = st.sidebar.selectbox("Persona", personas)
    else:
        persona_selecionada = 'Todas'
    
    # Aplicar filtros
    df_filtrado = df_decoded.copy()
    if has_campaign and campanha_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['campaign'] == campanha_selecionada]
    if has_persona and persona_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['persona'] == persona_selecionada]
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    total_registros = len(df_filtrado)
    
    # Calcular taxa de sucesso
    taxa_sucesso = 0
    if has_resultado and total_registros > 0:
        taxa_sucesso = (df_filtrado['resultado'] == 'Sucesso').sum() / total_registros * 100
    
    # Calcular taxa de previousy
    taxa_previousy = 0
    if has_previousy and total_registros > 0:
        taxa_previousy = (df_filtrado['previousy'] == 'Sim').sum() / total_registros * 100
    
    # Personas únicas
    personas_unicas = df_filtrado['persona'].nunique() if has_persona else 0
    
    with col1:
        st.metric("Total de Registros", f"{total_registros:,}")
    with col2:
        st.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%" if has_resultado else "N/A")
    with col3:
        st.metric("Contato Prévio", f"{taxa_previousy:.1f}%" if has_previousy else "N/A")
    with col4:
        st.metric("Personas Únicas", personas_unicas if has_persona else "N/A")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        if has_campaign:
            st.subheader("📈 Distribuição por Campanha")
            campaign_counts = df_filtrado['campaign'].value_counts().reset_index()
            campaign_counts.columns = ['campaign', 'count']
            fig1 = px.bar(campaign_counts, x='campaign', y='count',
                          color='count',
                          color_continuous_scale='Blues',
                          labels={'campaign': 'Campanha', 'count': 'Quantidade'})
            fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("Coluna 'campaign' não encontrada")
    
    with col2:
        if has_resultado:
            st.subheader("🎯 Resultado das Ações")
            resultado_counts = df_filtrado['resultado'].value_counts().reset_index()
            resultado_counts.columns = ['resultado', 'count']
            colors = {'Sucesso': '#10b981', 'Falha': '#ef4444', 'Desconhecido': '#gray'}
            fig2 = px.pie(resultado_counts, values='count', names='resultado',
                          color='resultado',
                          color_discrete_map=colors)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Coluna 'resultado' não encontrada")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if has_persona:
            st.subheader("👥 Distribuição por Persona")
            persona_counts = df_filtrado['persona'].value_counts().reset_index()
            persona_counts.columns = ['persona', 'count']
            fig3 = px.bar(persona_counts, x='persona', y='count',
                          color='count',
                          color_continuous_scale='Greens',
                          labels={'persona': 'Persona', 'count': 'Quantidade'})
            fig3.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Coluna 'persona' não encontrada")
    
    with col4:
        if has_previousy:
            st.subheader("📞 Contato Prévio")
            previousy_counts = df_filtrado['previousy'].value_counts().reset_index()
            previousy_counts.columns = ['previousy', 'count']
            colors_prev = {'Sim': '#f59e0b', 'Não': '#8b5cf6'}
            fig4 = px.pie(previousy_counts, values='count', names='previousy',
                          color='previousy',
                          color_discrete_map=colors_prev)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("Coluna 'previousy' não encontrada")
    
    st.markdown("---")
    
    # Análise cruzada
    if has_campaign and has_resultado:
        st.subheader("📊 Análise Cruzada: Resultado por Campanha")
        cross_tab = pd.crosstab(df_filtrado['campaign'], df_filtrado['resultado'])
        fig5 = px.bar(cross_tab, barmode='group',
                      labels={'value': 'Quantidade', 'campaign': 'Campanha'},
                      color_discrete_sequence=['#10b981', '#ef4444'])
        fig5.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig5, use_container_width=True)
        
        st.markdown("---")
    
    # Análise: Taxa de Sucesso
    if has_campaign and has_resultado:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Taxa de Sucesso por Campanha")
            success_by_campaign = df_filtrado.groupby('campaign').apply(
                lambda x: (x['resultado'] == 'Sucesso').sum() / len(x) * 100 if len(x) > 0 else 0
            ).reset_index()
            success_by_campaign.columns = ['campaign', 'taxa_sucesso']
            fig6 = px.bar(success_by_campaign, x='campaign', y='taxa_sucesso',
                          color='taxa_sucesso',
                          color_continuous_scale='RdYlGn',
                          labels={'campaign': 'Campanha', 'taxa_sucesso': 'Taxa de Sucesso (%)'})
            fig6.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            if has_persona:
                st.subheader("📈 Taxa de Sucesso por Persona")
                success_by_persona = df_filtrado.groupby('persona').apply(
                    lambda x: (x['resultado'] == 'Sucesso').sum() / len(x) * 100 if len(x) > 0 else 0
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
    
    # Mostrar apenas as colunas decodificadas
    cols_to_show = [col for col in ['campaign', 'previousy', 'persona', 'resultado'] if col in df_filtrado.columns]
    if cols_to_show:
        st.dataframe(df_filtrado[cols_to_show], use_container_width=True, height=400)
    else:
        st.dataframe(df_filtrado, use_container_width=True, height=400)
    
    # Estatísticas resumidas
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Resumo Estatístico")
        st.write(f"**Total de registros no dataset:** {len(df):,}")
        st.write(f"**Registros após filtros:** {len(df_filtrado):,}")
        if has_campaign:
            st.write(f"**Campanhas únicas:** {df_decoded['campaign'].nunique()}")
        if has_persona:
            st.write(f"**Personas únicas:** {df_decoded['persona'].nunique()}")
    
    with col2:
        st.subheader("🎯 Top Performers")
        if has_campaign:
            top_campaign = df_filtrado['campaign'].value_counts().head(1)
            if len(top_campaign) > 0:
                st.write(f"**Campanha mais frequente:** {top_campaign.index[0]} ({top_campaign.values[0]} registros)")
        
        if has_persona:
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

else:
    st.info("👆 Por favor, faça upload do arquivo meus_dados.csv para visualizar o dashboard")
    st.markdown("""
    ### O dashboard detecta automaticamente as colunas:
    - Busca por colunas com nomes: **campaign**, **campanha**, **previous**, **previousy**, **persona**, **result**, **resultado**
    - Decodifica valores numéricos automaticamente
    - Adapta-se aos dados disponíveis
    
    ### Exemplo de dados codificados:
    ```
    campaign,previous,persona,resultado
    0,1,1,1
    2,0,0,0
    1,1,2,1
    ```
    """)
