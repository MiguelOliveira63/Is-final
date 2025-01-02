from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import grpc
import api.grpc.server_services_pb2 as server_services_pb2
import api.grpc.server_services_pb2_grpc as server_services_pb2_grpc
import os
from rest_api_server.settings import GRPC_PORT, GRPC_HOST


class FileUploadView(APIView):
    def post(self, request):
        # Valida os dados do request usando o serializer
        serializer = FileUploadSerializer(data=request.data)
        
        # Se os dados forem válidos, pega o arquivo
        if serializer.is_valid():
            file = serializer.validated_data['file']
        
            # Verifica se o arquivo foi enviado
            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtém o nome e a extensão do arquivo
            file_name, file_extension = os.path.splitext(file.name)
            
            # Lê o conteúdo do arquivo
            file_content = file.read()
            
            # Conecta ao serviço gRPC
            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)
            
            # Prepara a requisição gRPC
            grpc_request = server_services_pb2.SendFileRequestBody(
                file_name=file_name,
                file_mime=file_extension,
                file=file_content
            )
            
            # Envia os dados do arquivo ao serviço gRPC
            try:
                stub.SendFile(grpc_request)  # Envia a requisição sem atribuí-la a `response`
                
                # Retorna a resposta de sucesso
                return Response({
                    "file_name": file_name,
                    "file_extension": file_extension
                }, status=status.HTTP_201_CREATED)
            
            except grpc.RpcError as e:
                # Se a chamada gRPC falhar, retorna o erro
                return Response({
                    "error": f"gRPC call failed: {e.details()}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Se o serializer não for válido, retorna os erros do serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class FileUploadChunksView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response(
                    {"error": "No file uploaded"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Conectar ao serviço gRPC
            channel = grpc.insecure_channel(f'{GRPC_HOST}:{GRPC_PORT}')
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)

            def generate_file_chunks(file, file_name, chunk_size=(64 * 1024)):
                """
                Gera os chunks do arquivo para envio.
                """
                try:
                    while chunk := file.read(chunk_size):
                        yield server_services_pb2.SendFileChunksRequest(
                            data=chunk,
                            file_name=file_name
                        )
                except Exception as e:
                    print(f"Error reading file: {e}")
                    raise  # Propagar a exceção

            # Enviar os chunks do arquivo para o serviço gRPC
            try:
                response = stub.SendFileChunks(generate_file_chunks(file, file.name, (64 * 1024)))
                if response.success:
                    return Response(
                        {"file_name": file.name},
                        status=status.HTTP_201_CREATED
                    )
                return Response(
                    {"error": f"gRPC response error: {response.message}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except grpc.RpcError as e:
                return Response(
                    {"error": f"gRPC call failed: {e.details()}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
