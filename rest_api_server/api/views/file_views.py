from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import os

class FileUploadView(APIView):
  def post(self, request):
    serializer = FileUploadSerializer(data=request.data)
    if serializer.is_valid():

      file = serializer.validated_data['file']

      if not file:
        return Response({"error": "No file uploaded"}, status=400)
      
      # Get MIME type using mimetypes
      file_name, file_extension = os.path.splitext(file.name)
      return Response({
      "file_name": file_name,
      "file_extension": file_extension
      }, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)