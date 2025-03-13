from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.agency.models import*
from apps.agency.serializers.profile_serializers import *
from classes.response.map_reponse import map_response
from classes.response.generic_response import GenericsRUD


class AgencyGalleryView(APIView):
    @extra_schema(
        'AddAgencyGallery',['agency_id','images']
    )

    def post(self,request):
        try:
            agency= get_value(request,key='agency_id')
            images= request.data.getlist('images[]')
            response_data=[]
            for image in images:
                data={
                    'agency':agency,
                    'images':image,
    
                }
                serializer= AgencyGallerySerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    response_data.append(serializer.data)
                else:
                    return map_response(message=serializer.errors,success=False)
            return map_response(message='Business Gallery added',success=True,data=response_data)
        except Exception as e:
            return map_response(message=str(e),success=False)

class GetAgencyGallery(APIView):
    @extra_schema(
        'AddAgencyGallery',['agency_id'],
    )

    def get(self,request):
        try:
            agency= get_value(request,key='agency_id')
            images= AgencyGallery.objects.get(agency=agency)

            serializer= AgencyGallerySerializer(images,many=True)
            return map_response(message='Business Gallery',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)

class AgencyGalleryEditDeleteView(GenericsRUD):
    model= AgencyGallery
    queryset=AgencyGallery.objects.all()
    serializer_class= AgencyGallerySerializer
    
    










