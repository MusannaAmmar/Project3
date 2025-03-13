from rest_framework.views import APIView
from apps.chats.serializer.serializers import MediaUploadSerializer
from classes.response.map_reponse import map_response


class MediaUpload(APIView):
    def post(self,request):
        try:
            data=request.data or request.query_params
            serializer=MediaUploadSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return map_response(message='Media Uploaded',success=True,data=serializer.data)
            return map_response(message=serializer.errors,success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
        