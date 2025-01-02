from concurrent import futures
import os
import grpc
import logging
import pika
import pg8000
import server_services_pb2_grpc
import server_services_pb2
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT


# Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

class SendFileService(server_services_pb2_grpc.SendFileServiceServicer):

    def __init__(self, *args, **kwargs):
        pass

    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path = os.path.join(MEDIA_PATH, request.file_name + request.file_mime)
        ficheiro_em_bytes = request.file
        with open(file_path, 'wb') as f:
            f.write(ficheiro_em_bytes)

        logger.info(f"{DBHOST}:{DBPORT}", exc_info=True)
        # Establish Connection to PostgreSQL
        try:
            # Connect to database
            conn = pg8000.connect(
                user=DBUSERNAME, 
                password=DBPASSWORD, 
                host=DBHOST, 
                port=DBPORT, 
                database=DBNAME
            )
            cursor = conn.cursor()
            # SQL query to create a table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE NOT NULL,
                age INT
            );
            """
            # Execute the SQL query to create the table
            cursor.execute(create_table_query)
            # Commit the changes (optional)
            conn.commit()
            # Nome definido no proto para a resposta "SendFileResponseBody"
            return server_services_pb2.SendFileResponseBody(success=True)
        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            context.set_details(f"Failed: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

    def SendFileChunks(self, request_iterator, context):
        try:
            os.makedirs(MEDIA_PATH, exist_ok=True)
            file_name = None
            file_chunks = []  # Armazenar todos os chunks na memória

            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name
                # Coletar os dados do arquivo
                file_chunks.append(chunk.data)

            # Combinar todos os chunks em um único objeto de bytes
            file_content = b"".join(file_chunks)
            file_path = os.path.join(MEDIA_PATH, file_name)

            # Escrever os dados coletados no arquivo no final
            with open(file_path, "wb") as f:
                f.write(file_content)
            logger.info(f"File {file_name} saved successfully at {MEDIA_PATH}")

            return server_services_pb2.SendFileChunksResponse(success=True, message="File imported successfully")

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)
            return server_services_pb2.SendFileChunksResponse(success=False, message=str(e))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
