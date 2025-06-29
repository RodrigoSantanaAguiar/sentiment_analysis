# export_data.py
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Nome do seu arquivo de banco de dados SQLite
DB_FILE = 'sentiment_data.db'

def export_table_to_csv(table_name, output_filename):
    conn = None
    try:
        # Verifica se o arquivo do banco de dados existe
        if not os.path.exists(DB_FILE):
            print(f"Erro: Banco de dados '{DB_FILE}' não encontrado.")
            return

        conn = sqlite3.connect(DB_FILE)

        # Constrói a query SQL para selecionar todos os dados da tabela
        query = f"SELECT * FROM {table_name};"

        # Lê os dados do SQLite para um DataFrame do pandas
        df = pd.read_sql_query(query, conn)

        # Define o caminho de saída para o CSV
        # Você pode criar uma pasta 'exports' para organizar
        output_dir = 'exports'
        os.makedirs(output_dir, exist_ok=True) # Cria a pasta se ela não existir
        output_filepath = os.path.join(output_dir, output_filename)

        # Exporta o DataFrame para um arquivo CSV
        # index=False evita que o pandas escreva o índice do DataFrame como uma coluna no CSV
        df.to_csv(output_filepath, index=False, encoding='utf-8')

        print(f"Dados da tabela '{table_name}' exportados com sucesso para '{output_filepath}'")
        print(f"Total de linhas exportadas: {len(df)}")

    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    except pd.errors.EmptyDataError:
        print(f"A tabela '{table_name}' está vazia. Nenhum dado para exportar.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Exemplo de uso:
    # Exportar a tabela de dados brutos
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_table_to_csv('comments_sentiments_raw', f'comments_raw_{timestamp_str}.csv')

    print("\n---")

    # Exportar a tabela de dados agregados
    export_table_to_csv('comments_sentiments_aggregated', f'comments_aggregated_{timestamp_str}.csv')