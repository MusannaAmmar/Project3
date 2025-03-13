from rest_framework.views import APIView
from apps.administration.serializer.serializers import*
from classes.response.map_reponse import map_response
from classes.response.generic_response import GenericsRUD,GenericsLC

class VideoTutorialView(APIView):
    serializer_class=VideoTutorialSerializer


    def post(self,request):
        try:
            if request.user.role=='admin':
                data= request.data or request.query_params
                data['user']=request.user.id
                serializer=VideoTutorialSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return map_response(message='Video Uploaded',success=True,data=serializer.data)
                return map_response(message=serializer.errors,success=False)
            return map_response(message='User must be admin',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class VideoTutorialUpdateDeleteView(GenericsRUD):
    model= VideoTutorial
    serializer_class=VideoTutorialSerializer
    queryset= VideoTutorial.objects.all()

class VideoTutorialListView(GenericsLC):
    model= VideoTutorial
    serializer_class=VideoTutorialSerializer
    queryset= VideoTutorial.objects.all()


