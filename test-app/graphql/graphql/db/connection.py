import psycopg2
from psycopg2 import pool

try:
    connection_pool = pool.SimpleConnectionPool(
        1, 
        10,
        user="myuser",
        password="mypassword",
        host="db",  
        port="5432",
        database="mydatabase"
    )

except Exception as e:
    print("Erro ao ligar ao PostgreSQL:", e)

def execute_query(query, params=None):
    connection = connection_pool.getconn()  # Obtenha a conexão do pool
    try:
        with connection:  # Garante que a transação será automaticamente commitada
            with connection.cursor() as cursor:
                cursor.execute(query, params)  # Executa a query
                if cursor.description:  # Para SELECT ou RETURNING
                    return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao executar query: {e}")
        raise
    finally:
        connection_pool.putconn(connection)  # Retorna a conexão ao pool



