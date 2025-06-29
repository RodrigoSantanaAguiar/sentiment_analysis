import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

# --- Função para carregar dados do SQLite (COM CACHE) ---
# st.cache_data armazena em cache o DataFrame retornado.
# Ele só reexecutará se o conteúdo de 'sentiment_data.db' mudar (baseado em hash do arquivo).
# Ou, se for forçado a invalidar o cache (st.rerun() não invalida por padrão,
# mas se os dados mudam no arquivo .db, o hash muda e o cache é invalidado).
@st.cache_data(ttl=60) # Opcional: TTL para invalidar cache após N segundos
def load_data_from_db():
    conn = None
    df = pd.DataFrame()
    try:
        conn = sqlite3.connect('sentiment_data.db')
        df = pd.read_sql_query("SELECT * FROM comments_sentiments_aggregated", conn)
        df['observation_time'] = pd.to_datetime(df['observation_time'])
    except sqlite3.Error as e:
        st.error(f"Error while loading the data: {e}")
    finally:
        if conn:
            conn.close()
    return df

# --- Configurações da Página Streamlit ---
st.set_page_config(layout="wide", page_title="Real-time sentiment analysis")

st.title("📊 Real-time sentiment analysis")
st.write("Monitoring social network comments using Kafka and Python")

# --- Controles de Atualização Automática ---
status_text = st.empty() # Placeholder para a mensagem de status da atualização
# margin_l, col_auto, col_interval, margin_r = st.columns([1, 1, 3, 1]) # Organiza os controles em colunas
#
# with col_auto:
    # auto_refresh = st.checkbox("Auto refresh", value=True)
#
# with col_interval:
#     refresh_interval_seconds = st.slider("Refresh interval (seconds)", 5, 30, 10)

# --- Cria um Placeholder para o Conteúdo Dinâmico ---
# Tudo dentro deste placeholder será atualizado sem "piscar" a página inteira

dashboard_placeholder = st.empty()

# --- Loop de Atualização ---
while True:
    with dashboard_placeholder.container(): # Usa o placeholder para o conteúdo principal
        # Atualiza a mensagem de status
        # status_text.info(f"Refreshing charts each {refresh_interval_seconds} seconds. Last update: {datetime.now().strftime('%H:%M:%S')}", icon="🔄")

        # --- Carrega os dados mais recentes ---
        # A função load_data_from_db() será chamada, mas o cache pode evitar a leitura real do DB
        df = load_data_from_db()

        if df.empty:
            st.warning("No available data. Make sure both Producer and Consumer are running and saving data.")
        else:
            # --- Métricas Principais ---
            st.subheader("Sentiment Summary")

            # Global values
            total_count = df['total_comments'].sum()
            positive_count = df['positive_comment_number'].sum()
            neutral_count = df['neutral_comment_number'].sum()
            negative_count = df['negative_comment_number'].sum()

            positive_perc = positive_count / total_count
            neutral_perc = neutral_count / total_count
            negative_perc = negative_count / total_count

            # Source values
            # total_count_source = df['total_comments'].groupby('source').sum()
            # positive_count_source = df['positive_comment_number'].groupby('source').sum()
            # neutral_count_source = df['neutral_comment_number'].groupby('source').sum()
            # negative_count_source = df['negative_comment_number'].groupby('source').sum()

            # Device values
            # total_count_device = df['total_comments'].groupby('device').sum()
            # positive_count_device = df['positive_comment_number'].groupby('device').sum()
            # neutral_count_device = df['neutral_comment_number'].groupby('device').sum()
            # negative_count_device = df['negative_comment_number'].groupby('device').sum()


            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total comments", total_count)
            with col2:
                st.metric("% Positive", round(positive_perc, 2))
            with col3:
                st.metric("% Neutral", round(neutral_perc, 2))
            with col4:
                st.metric("% Negative", round(negative_perc, 2))

            # --- Gráfico de Distribuição de Sentimento (Barras) ---
            st.subheader("Sentiment distribution")

            fig1, ax1 = plt.subplots(figsize=(10, 6))
            plt.pie([positive_perc, neutral_perc, negative_perc], labels=['Positive', 'Neutral', 'Negative'], autopct='%1.1f%%')
            ax1.set_title('Sentiment by % of comments')
            st.pyplot(fig1, use_container_width=False)

            # --- Gráfico de Sentimento ao Longo do Tempo (Linha - Média Móvel) ---
            st.subheader("Sentiment over time")
            sentiment_polarity = df.groupby(['device', 'observation_time'])['sentiment_polarity'].mean().reset_index()
            # df_sorted['sentiment_numeric'] = df_sorted['sentiment_label'].map({'Positivo': 1, 'Neutro': 0, 'Negativo': -1})

            # df_resampled = df_sorted.set_index('timestamp').resample('10S')['sentiment_numeric'].mean().fillna(0)

            fig2, ax2 = plt.subplots(figsize=(12, 6))

            for source_val, group_df in sentiment_polarity.groupby('device'):
                # Ordena os dados dentro de cada grupo por tempo para garantir que a linha seja contínua
                group_df_sorted = group_df.sort_values('observation_time')
                ax2.plot(group_df_sorted['observation_time'], group_df_sorted['sentiment_polarity'],
                         marker='o', linestyle='-', markersize=4,
                         label=f'{source_val}')  # Rótulo da legenda

            ax2.set_title('Média de Sentimento Agregado por Hora e Fonte/Dispositivo')
            ax2.set_xlabel('Tempo de Observação (Hora)')
            ax2.set_ylabel('Média de Sentimento (1=Positivo, 0=Neutro, -1=Negativo)')
            ax2.grid(True)
            ax2.legend(title='Fonte (Dispositivo)', bbox_to_anchor=(1.05, 1), loc='upper left')  # Legenda fora do gráfico
            plt.xticks(rotation=45, ha='right')  # Rotação para o eixo X
            plt.tight_layout()  # Ajusta o layout para evitar sobreposição
            st.pyplot(fig2)

            # --- Tabela dos Últimos Comentários ---
            # st.subheader("Últimos Comentários Analisados")
            # display_cols = ['timestamp', 'user_id', 'comment', 'sentiment_label', 'sentiment_polarity', 'source', 'device']
            # existing_cols = [col for col in display_cols if col in df.columns]
            # st.dataframe(df.tail(10).sort_values('timestamp', ascending=False)[existing_cols])

    # Espera antes da próxima atualização
    time.sleep(10)
    # st.rerun() é chamado apenas se auto_refresh estiver True
    # O loop 'while auto_refresh' com sleep e reruns é o que faz a mágica.
    # if auto_refresh: # Verifica novamente a flag, caso o usuário a desmarque durante o sleep
    st.rerun() # Use st.experimental_rerun() para reruns programados