from rest_framework.views import APIView
from apps.users.models import *
from math import ceil
from apps.users.serializers.app_profile_serializer import*
from classes.response.map_reponse import map_response
from classes.utils import get_value
from classes.extra_schema import extra_schema

class GetProfessionalsView(APIView):
    def get(self,request):
        try:
            category_id= request.query_params.get('category')
            page= int(request.query_params.get('page',1))
            page_size= int(request.query_params.get('page_size',10))

            professionals=ProfessionProfile.objects.all()

            if category_id:
                professionals= professionals.filter(category_id=category_id)

            total_count= professionals.count()
            total_pages= ceil(total_count/page_size)
            start=(page - 1)* page_size
            end=start+page_size
            paginated_professionals= professionals[start:end]

            profession_serializer= ProfessionProfileSerializer(paginated_professionals,many=True)
            return map_response(
                data={
                    'data':profession_serializer.data,
                    'page':page,
                    'page_size':page_size,
                    'total_pages':total_pages
                },
                message='Profession List Retrieved',
                success=True
            )
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class ProfessionbyCategory(APIView):
    @extra_schema(
            'categorylist',['category']
    )
    def post(self,request):
        try:
            category= get_value(request,key='category')
            print('----->>>',category)
            profession=ProfessionProfile.objects.filter(category=category)
            print('------>>>>',profession)
            profession_serializer= ProfessionProfileSerializer(profession,many=True)
            return map_response(message='Profession by Category',success=True,data=profession_serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class TopProfessionView(APIView):

    def get(self,request):
        try:
            profession= ProfessionProfile.objects.order_by('-ratings')
            serializer= ProfessionProfileSerializer(profession)
            return map_response(message='Top Rated Professions',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)