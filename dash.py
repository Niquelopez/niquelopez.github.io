import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

# --- Configuração da Pagina
st.set_page_config(
    page_title='Versões POS TDS Informática',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
)

# --- Criar o dataframe
df = pd.read_excel(
    io='./Datasets/versao.xlsx',
    engine='openpyxl',
    sheet_name='base',
    usecols='A:I',
    nrows=26412
)

# --- PÁGINA PRINCIPAL 
st.header(":bar_chart: DASHBOARD DE VERSÕES TDS")

# --- Central de Informação no Topo (Maior e mais destacada)
with st.expander("ℹ️ **📌CENTRAL DE INFORMAÇÃO - CLIQUE PARA EXPANDIR**", expanded=True):
    st.markdown("""
    <style>
    .big-font {
        font-size: 18px !important;
        font-weight: bold;
    }
    </style>
    <div class="big-font">
      ABERTURA DE CONTAS INDISPONIVEL, PROBLEMAS NA RECEITA FEDERAL /  ACERTO FINANCEIRO PIX - DESABILITADO TEMPORARIAMENTE. 
    </div>
    """, unsafe_allow_html=True)

# - sidebar
with st.sidebar:
    logo_teste = Image.open('./Mídia/logo tds.png')
    st.image(logo_teste, width=300)  
    st.subheader('MENU DE VERSÕES EM CAMPO')
    
    # Selectbox para selecionar a versão
    fVersao = st.selectbox(
        "Selecione a Versao:",
        options=df['Versao'].unique(),
        key="select_Versao"
    )
    
    # Multiselect para selecionar múltiplos POS
    fPos = st.multiselect(
        "Selecione o(s) POS",
        options=df["Id Fisica"].unique(),
        key="select_pos"
    )

    # Novo selectbox para mostrar ou não o gráfico de Pinpad (padrão "Não")
    mostrar_pinpad = st.selectbox(
        "Mostrar Pinpad:",
        options=["Não", "Sim"],  
        key="select_pinpad"
    )

    # Adiciona o texto das features da versão 4.19
    if str(fVersao) == "4.19":
        st.markdown("---")  
        st.subheader("FEATURES DA VERSÃO 4.19")
        st.markdown("""
        - **AJUSTE DO QR CODE**
        - **MVP2 - AJUSTE NO EXPRESSO DA SORTE**
        """)

#  mostra os dados de Pinpad ou de versão/POS
if mostrar_pinpad == "Sim":
    # Oculta os dados de versão e POS e exibe apenas os dados do Pinpad
    st.markdown("---")  
    st.subheader("Ranking de Modelos de Pinpad")

    # Agrupar os dados por modelo de Pinpad e contar o total
    pinpad_counts = df['Pin Modelo'].value_counts().reset_index()
    pinpad_counts.columns = ['Modelo de Pinpad', 'Total']

    # Ordenar os dados pelo total (do maior para o menor)
    pinpad_counts_sorted = pinpad_counts.sort_values(by='Total', ascending=False)

    # Exibir o destaque com o total de cada modelo de Pinpad
    st.subheader("Destaques de Modelos de Pinpad")
    num_cols = len(pinpad_counts_sorted)
    cols = st.columns(num_cols)

    for i, row in pinpad_counts_sorted.iterrows():
        with cols[i]:
            st.metric(label=f"Modelo {row['Modelo de Pinpad']}", value=row['Total'])

    # Exibir o gráfico de barras com Plotly
    fig = px.bar(
        pinpad_counts_sorted,
        x='Modelo de Pinpad',
        y='Total',
        text='Total',  
        title="Ranking de Modelos de Pinpad"
    )
    fig.update_traces(
        textfont_size=12,  
        textangle=0,       
        textposition="outside", 
        cliponaxis=False   
    )
    fig.update_layout(
        xaxis_title="Modelo de Pinpad",
        yaxis_title="Total",
        showlegend=False,
        height=400  
    )
    st.plotly_chart(fig, use_container_width=True)  

else:
    
    if fPos:  # Verifica se pelo menos um POS foi selecionado
        tab1_qtde_Versao = df.loc[
            (df['Id Fisica'].isin(fPos)) &  
            (df['Versao'] == fVersao)
        ]
    else:
        # Se nenhum POS for selecionado, filtra apenas pela versão
        tab1_qtde_Versao = df.loc[df['Versao'] == fVersao]

    # --- Conta o total de ocorrências por Id Fisica
    if not tab1_qtde_Versao.empty:
        # Agrupa por 'Id Fisica' e conta o número de ocorrências
        tab1_qtde_Versao = tab1_qtde_Versao.groupby('Id Fisica').size().reset_index(name='Total')
    else:
        tab1_qtde_Versao = pd.DataFrame()  

    # --- Exibe os destaques apenas para POS com dados
    st.subheader("Dados Filtrados em Destaque")
    if not tab1_qtde_Versao.empty:
        # Calcula o total de ocorrências
        total_ocorrencias = tab1_qtde_Versao['Total'].sum()

        # Cria colunas para exibir os destaq
        num_cols = len(tab1_qtde_Versao) + 1  
        cols = st.columns(num_cols)

        # Exibe os destaques para cada POS com dados
        for i, row in tab1_qtde_Versao.iterrows():
            with cols[i]:
                valor_pos = row['Total']
                if valor_pos == tab1_qtde_Versao['Total'].max():
                    st.metric(label=f"POS {row['Id Fisica']}", value=valor_pos, delta=f"Maior valor ({valor_pos})")
                elif valor_pos == tab1_qtde_Versao['Total'].min():
                    st.metric(label=f"POS {row['Id Fisica']}", value=valor_pos, delta=f"Menor valor ({valor_pos})")
                else:
                    st.metric(label=f"POS {row['Id Fisica']}", value=valor_pos)

        # Exibe o destaque do total
        with cols[-1]:
            st.metric(label="Total de POS", value=total_ocorrencias)
    else:
        st.write("Nenhum dado encontrado com os filtros selecionados.")

    # --- Adicionar botões para selecionar o modelo de POS
    st.markdown("---")  # Linha separadora
    st.subheader("Selecione o Modelo de POS para Visualizar o Ranking por Estado")

    # Lista dos 3 modelos de POS disponíveis
    modelos_pos = df['Id Fisica'].unique()[:3]  

    # Botões para selecionar o modelo de POS
    modelo_selecionado = st.radio(
        "Selecione o Modelo de POS:",
        options=modelos_pos,
        key="select_modelo_pos"
    )

    # --- Filtrar os dados pelo modelo de POS selecionado
    df_filtrado = df[df['Id Fisica'] == modelo_selecionado]

    # --- Agrupar os dados por UF e contar o total de POS para o modelo selecionado
    total_por_uf_filtrado = df_filtrado.groupby('UF').size().reset_index(name='Total')

    # --- Ordenar os dados pelo total de POS (do maior para o menor)
    total_por_uf_filtrado_sorted = total_por_uf_filtrado.sort_values(by='Total', ascending=False)

    # --- Exibir os gráficos lado a lado
    if not total_por_uf_filtrado_sorted.empty:
        # Cria colunas para alinhar os gráficos lado a lado
        col1, col2 = st.columns([1, 2])  # Ajuste das proporções das colunas

        # Gráfico de pizza na primeira coluna
        with col1:
            if not tab1_qtde_Versao.empty:
                st.subheader("Distribuição de POS")
                fig = px.pie(
                    tab1_qtde_Versao,
                    values='Total',
                    names='Id Fisica',
                    title='Distribuição de POS',
                    hover_data=['Total'],
                    labels={'Total': 'Total de POS'}
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Nenhum dado encontrado para gerar o gráfico de pizza.")

        # Gráfico de ranking por estado na segunda coluna (usando Plotly)
        with col2:
            st.subheader(f"Ranking de Estados por POS - Modelo {modelo_selecionado}")
            fig = px.bar(
                total_por_uf_filtrado_sorted,
                x='UF',
                y='Total',
                text='Total',  
                title=f"Ranking de Estados por POS - Modelo {modelo_selecionado}"
            )
            fig.update_traces(
                textfont_size=12,  
                textangle=0,       
                textposition="outside",  
                cliponaxis=False   
            )
            fig.update_layout(
                xaxis_title="UF (Estado)",
                yaxis_title="Total de POS",
                showlegend=False,
                height=400  
            )
            st.plotly_chart(fig, use_container_width=True)  
    else:
        st.write(f"Nenhum dado encontrado para o modelo de POS {modelo_selecionado}.")

# --- Rodapé com mensagem em transição
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #black;
        text-align: center;
        padding: 10px;
        font-size: 16px;
        animation: slide 8s infinite;
    }
    @keyframes slide {
        0% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; }
    }
    </style>
    <div class="footer">
      Ultima atualização da base 20/02 - 12:00
    </div>
    """,
    unsafe_allow_html=True
)   