from confluent_kafka import Producer
import json
import time
import random
from datetime import datetime
import logging
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configurações do Kafka Producer
# 'bootstrap.servers': É o endereço do seu broker Kafka.
# Como o Kafka está rodando no Docker e mapeamos a porta 9092 para o localhost,
# ele será acessível em 'localhost:9092'.
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'python-social-media-producer'
}

# Tópico Kafka para os comentários
# É o nome do "canal" para onde os comentários serão enviados.
TOPIC_NAME = "social_media_comments"

# --- NOVA FUNÇÃO: Carregar comentários do arquivo ---
def load_comments_from_file(filepath):
    comments = []
    # Constrói o caminho completo para o arquivo de comentários
    script_dir = os.path.dirname(__file__)
    full_filepath = os.path.join(script_dir, filepath)

    if not os.path.exists(full_filepath):
        print(f"Erro: Arquivo de comentários não encontrado em {full_filepath}. Verifique o caminho.")
        return []

    with open(full_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # Remove espaços em branco (como quebras de linha) do início/fim da linha
            comment = line.strip()
            if comment: # Garante que a linha não está vazia
                comments.append(comment)
    print(f"Carregados {len(comments)} comentários do arquivo: {filepath}")
    return comments


# --- Carrega a lista de comentários usando a nova função ---
# O nome do arquivo TXT que você criou
COMMENTS_FILE = "comments_en.txt" # Ou "data/comments_en.txt" se você criou a pasta "data"
sample_comments = load_comments_from_file(COMMENTS_FILE)

# Verificação essencial: se o arquivo não foi encontrado ou está vazio
if not sample_comments:
    print("Nenhum comentário para processar. Por favor, verifique o arquivo de comentários.")
    exit() # Encerra o script se não houver comentários


# Lista de comentários de exemplo (alguns neutros, positivos, negativos)
# Isso simula a variedade de comentários que você encontraria em uma rede social.
sources = ["Facebook", "Twitter", "TikTok", "Instagram", "Youtube", "Website", "Email"]

devices = ["web", "smartphone", "tablet", "smartphone", "smartphone", "smartphone", "web"]

# Inicializa o Produtor
# Criamos uma instância do Produtor com as configurações definidas.
producer = Producer(conf)

def delivery_report(err, msg):
    """
    Callback chamado quando uma mensagem é entregue ou falha.
    É importante para depuração e para saber se as mensagens estão chegando ao Kafka.
    """
    if err is not None:
        logging.error(f"Falha na entrega da mensagem: {err}")
    else:
        logging.info(f"Mensagem entregue para o tópico '{msg.topic()}' na partição [{msg.partition()}] com offset {msg.offset()}")


logging.info(f"Iniciando produtor de comentários para o tópico '{TOPIC_NAME}'...")

try:
    user_id_counter = 0
    while True: # Loop infinito para simular um fluxo contínuo de comentários
        user_id_counter += 1
        comment_text = random.choice(sample_comments) # Escolhe um comentário aleatório
        timestamp = datetime.now().isoformat() + "Z" # Gera um timestamp ISO 8601

        # Monta os dados do comentário em um dicionário
        comment_data = {
            "user_id": f"user_{user_id_counter}",
            "timestamp": timestamp,
            "comment": comment_text,
            "source": random.choice(sources),
            "device": random.choice(devices)
        }

        # Converte o dicionário para JSON e depois para bytes (Kafka exige bytes)
        message_value = json.dumps(comment_data).encode('utf-8')

        # Produz a mensagem para o tópico.
        # O 'callback=delivery_report' faz com que a função seja chamada
        # após a tentativa de entrega da mensagem.
        producer.produce(TOPIC_NAME, value=message_value, callback=delivery_report)

        # Garante que as mensagens pendentes sejam enviadas.
        # producer.poll(0) força o produtor a processar callbacks pendentes.
        producer.poll(0)

        # Pausa para simular o tempo entre os posts de usuários.
        time.sleep(random.uniform(5, 10.0))

except KeyboardInterrupt:
    # Permite encerrar o produtor com Ctrl+C no terminal
    logging.info("Produtor encerrado pelo usuário.")
finally:
    # Garante que todas as mensagens pendentes sejam enviadas antes de fechar o produtor.
    producer.flush()
    logging.info("Produtor finalizado.")
