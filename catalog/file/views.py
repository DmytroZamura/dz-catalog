from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from rest_framework import generics
from .models import *
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from PIL import Image
from rest_framework.exceptions import ParseError
# from .permissions import IsOwnerOrReadOnly



class FileUploadView(APIView):

    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, filetype, format=None):

        file_obj = request.data['file']


        try:
            user_file = File.objects.create(user=request.user, file=file_obj, name=filename, type=filetype)
            # user_file.file.save(filename, file_obj)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = FileSerializer(user_file, context={'request': request})
            return Response(serializer.data)


class FileDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FileSerializer
    queryset = File.objects.all()


class FilesView(generics.ListAPIView):
    serializer_class = FileSerializer


    def get_queryset(self):
        user = self.request.user.pk
        return File.objects.filter(user=user)


# class ImageUploadParser(FileUploadParser):
#     media_type = 'image-*'


class ImageUploadView(APIView):

    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, filetype, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        file_obj = request.data['file']



        try:
            img = Image.open(file_obj)
            img.verify()
        except:
            raise ParseError("Unsupported image type")



        try:
            user_file = UserImage.objects.create(file=file_obj, user=request.user, name=filename, type=filetype)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = UserImageSerializer(user_file, context={'request': request})
            return Response(serializer.data)