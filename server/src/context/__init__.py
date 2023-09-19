from argparse import Namespace
from pathlib import Path
from typing import Dict
import boto3
from .participant import Participant
from .session import Session
COLLECTION_FOLDER = Path('questions')
SESSION_LOG_FOLDER = Path('session_log')

class AppContext:
    args = Namespace(
        mqtt_port=9001,
        api_port=8080,
    )

    mqtt_broker = None
    api_service = None

    sessions: 'Dict[Session]' = {}
    collections = {}
    # Configura el cliente de S3
    s3 = boto3.client('s3')
    bucket_name = 'hans-platform-collections'
    @staticmethod
    def reload_collections():
        # Listar objetos en el bucket
        response = AppContext.s3.list_objects_v2(Bucket=AppContext.bucket_name)

        # Procesar objetos y construir el diccionario
        for obj in response.get('Contents', []):
            collection_name = obj['Key'].split('/')[0]
            file_name = obj['Key'].split('/')[1]
            
            # Verificar si el nombre del objeto comienza con "Question"
            if file_name.startswith('Question'):
                # Obtén el conjunto de objetos para esta colección, o crea uno nuevo si no existe
                questions = AppContext.collections.get(collection_name, set())
                
                # Agrega el nombre del objeto al conjunto
                questions.add(file_name)
                
                # Actualiza el diccionario con el conjunto actualizado
                AppContext.collections[collection_name] = questions

