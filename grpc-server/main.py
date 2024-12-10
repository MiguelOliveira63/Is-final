from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
import os
import server_services_pb2_grpc
import server_services_pb2
import grpc
import pg8000
import logging


#Configure logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("FileService")

#Consult the file "server_services_pb2_grpc" to find out the name of the Servicer class of the "SendFileService" service
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
    #Establish Connection to POstgreSQL
    try:
      #connect to database
      conn = pg8000.connect(user=f'{DBUSERNAME}', password=f'{DBPASSWORD}', host=f'{DBHOST}', port=f'{DBPORT}', database=f'{DBNAME}')
      cursor = conn.cursor()
      #SQL query to create a table
      create_table_query = """
      CREATE TABLE IF NOT EXISTS files (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE NOT NULL,
        age INT
      );
      """
      #Execute the SQL query to create the table
      cursor.execute(create_table_query)
      #Commit the changes(optional)
      conn.commit()
      #nome definido no proto para a resposta "SendFileResponseBody"
      return server_services_pb2.SendFileResponseBody(success=True)
    except Exception as e:
      logger.error(f"Error: {str(e)}", exc_info=True)
      context.set_details(f"Failed: {str(e)}")
      context.set_code(grpc.StatusCode.INTERNAL)
      return server_services_pb2.SendFileResponseBody(success=False)
  
def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  # Consult the file "server_services_pb2_grpc" to see the name of the function generated to add the service to the server
  server_services_pb2_grpc.add_SendFileServiceServicer_to_server(SendFileService(),
  server)
  server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
  server.start()
  server.wait_for_termination()

if __name__ == '__main__':
  serve()