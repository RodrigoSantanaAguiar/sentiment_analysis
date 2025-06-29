from confluent_kafka import Consumer, KafkaException, KafkaError
import json
from textblob import TextBlob
import logging
import sqlite3
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações do Kafka Consumer
# 'bootstrap.servers': Endereço do seu broker Kafka (o mesmo do produtor).
# 'group.id': É o identificador do seu grupo de consumidores.
#             Todos os consumidores com o mesmo group.id formam um grupo,
#             e o Kafka distribui as mensagens do tópico entre eles.
# 'auto.offset.reset': 'earliest' significa que se este consumidor (ou grupo)
#                      não tiver um offset salvo para o tópico, ele começará
#                      a ler as mensagens desde o início do tópico.
#                      'latest' (o padrão) começaria a ler apenas novas mensagens.
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'sentiment_analyzer_group_new',
    'auto.offset.reset': 'earliest'
}

# Inicializa o Consumidor
consumer = Consumer(conf)

# Tópico Kafka para os comentários
# Deve ser o mesmo tópico para o qual o produtor está enviando.
TOPIC_NAME = "social_media_comments"

# Função para analisar o sentimento
# Usamos a biblioteca TextBlob para simplicidade.
def analyze_sentiment(text):
    analysis = TextBlob(text)
    # TextBlob retorna uma polaridade de -1.0 (negativo) a 1.0 (positivo).
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        label = "Positive"
    elif analysis.sentiment.polarity < 0:
        label = "Negative"
    else:
        label = "Neutral"
    return polarity, label


def load_sql_query(filename):
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(script_dir, "sql_queries", filename)
    with open(filepath, "r") as query_file:
        return query_file.read()


def initialize_database():
    """Inicializa o banco de dados criando a tabela se não existir"""
    conn = None
    try:
        conn = sqlite3.connect('sentiment_data.db')
        cursor = conn.cursor()
        
        # Executa a criação da tabela apenas uma vez
        create_query = load_sql_query("create_raw_table.sql")
        cursor.execute(create_query)
        conn.commit()
        logging.info("Banco de dados inicializado com sucesso")
        
    except sqlite3.Error as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")
    finally:
        if conn:
            conn.close()


def save_to_database(user_id, comment_text, sentiment_label, sentiment_polarity, timestamp, source, device):
    conn = None
    try:
        conn = sqlite3.connect('sentiment_data.db')
        cursor = conn.cursor()

        # Executa apenas a inserção dos dados
        insert_query = load_sql_query("insert_raw_data.sql")
        cursor.execute(insert_query, (user_id, comment_text, sentiment_label, sentiment_polarity, timestamp, source, device))
        conn.commit()
        
        logging.info(f"Dados salvos: {user_id} - {sentiment_label} ({sentiment_polarity:.2f})")

    except sqlite3.Error as e:
        logging.error(f"Erro no banco de dados: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


logging.info(f"Starting sentiment analyzer... Topic: {TOPIC_NAME}")

# Inicializa o banco de dados apenas uma vez
initialize_database()

try:
    # Se inscreve no tópico.
    # O consumidor começará a receber mensagens deste tópico.
    consumer.subscribe([TOPIC_NAME])

    while True: # Loop infinito para continuamente buscar novas mensagens
        # Polling para novas mensagens.
        # consumer.poll(1.0) espera por até 1 segundo por uma mensagem.
        # Se não houver mensagens após 1 segundo, ele retorna None.
        msg = consumer.poll(1.0)

        if msg is None:
            # Nenhum dado disponível dentro do timeout
            continue
        if msg.error():
            # Tratamento de erros do Kafka
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Fim da partição. Isso é normal, significa que não há mais mensagens
                # novas nesta partição por enquanto. O consumidor continuará esperando.
                continue
            elif msg.error():
                # Outro tipo de erro no Kafka (ex: rede, configuração)
                raise KafkaException(msg.error())
        else:
            # Mensagem recebida com sucesso!
            # 1. Decodifica a mensagem (que está em bytes) para string JSON.
            # 2. Converte a string JSON de volta para um dicionário Python.
            comment_data = json.loads(msg.value().decode('utf-8'))

            # Extrai as informações relevantes do dicionário.
            comment_text = comment_data.get('comment', 'N/A')
            user_id = comment_data.get('user_id', 'N/A')
            timestamp = comment_data.get('timestamp', 'N/A')
            source = comment_data.get('source', 'N/A')
            device = comment_data.get('device', 'N/A')

            # Realiza a análise de sentimento.
            sentiment_polarity, sentiment_label = analyze_sentiment(comment_text)

            # Imprime o resultado.
            save_to_database(user_id, comment_text, sentiment_label, sentiment_polarity, timestamp, source, device)

except KeyboardInterrupt:
    # Permite encerrar o consumidor com Ctrl+C no terminal
    logging.info("Consumidor encerrado pelo usuário.")
finally:
    # Garante que o consumidor seja fechado corretamente, liberando recursos.
    consumer.close()
    logging.info("Consumidor finalizado.")