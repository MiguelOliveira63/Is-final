import pika
import json
import os
import logging
from io import StringIO
import pandas as pd
import pg8000

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")
QUEUE_NAME = 'csv_chunks'

# Database Configuration
DBHOST = os.getenv('DBHOST', 'localhost')
DBUSERNAME = os.getenv('DBUSERNAME', 'myuser')
DBPASSWORD = os.getenv('DBPASSWORD', 'mypassword')
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBPORT = int(os.getenv('DBPORT', '5432'))

# Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()

# To handle multiple files concurrently
file_data_store = {}

def save_to_database(df):
    """Save DataFrame to the database."""
    try:
        conn = pg8000.connect(
            host=DBHOST,
            port=DBPORT,
            database=DBNAME,
            user=DBUSERNAME,
            password=DBPASSWORD
        )
        cursor = conn.cursor()

        # Assuming a table 'data_table' exists with appropriate schema
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO data_table (column1, column2) VALUES (%s, %s)", (row[0], row[1]))
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Data successfully saved to the database.")
    except Exception as e:
        logger.error(f"Database save failed: {e}", exc_info=True)

def process_message(ch, method, properties, body):
    """Process incoming RabbitMQ messages."""
    try:
        file_id = properties.correlation_id  # Unique file identifier
        if not file_id:
            logger.error("Message missing correlation_id. Skipping...")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        str_stream = body.decode('utf-8')
        if str_stream == "__EOF__":
            logger.info(f"EOF marker received for file_id={file_id}. Finalizing...")
            if file_id in file_data_store:
                file_content = b"".join(file_data_store[file_id])
                csv_text = file_content.decode('utf-8')
                csvfile = StringIO(csv_text)
                df = pd.read_csv(csvfile)
                save_to_database(df)
                del file_data_store[file_id]  # Clean up stored data
                logger.info(f"File processing complete for file_id={file_id}.")
            else:
                logger.warning(f"No data found for file_id={file_id}.")
        else:
            logger.info(f"Received chunk for file_id={file_id}.")
            if file_id not in file_data_store:
                file_data_store[file_id] = []
            file_data_store[file_id].append(body)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    """Main function to start the RabbitMQ worker."""
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST,
                                      port=RABBITMQ_PORT,
                                      credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_consume(queue=QUEUE_NAME,
                              on_message_callback=process_message,
                              auto_ack=False)
        logger.info("Worker is waiting for messages.")
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error in main worker loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()
