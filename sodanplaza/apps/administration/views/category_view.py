from rest_framework.views import APIView
from apps.administration.serializer.serializers import*
from apps.users.models import *
from classes.response.map_reponse import map_response
from classes.response.generic_response import GenericsLC,GenericsRUD
from rest_framework.permissions import AllowAny
from classes.utils import get_value 
from django.db.models import Q
from classes.extra_schema import extra_schema
from apps.agency.models import*

class AddCategoryView(APIView):
    serializer_class= CategorySerializer

    def post(self,request):
        try:
            if request.user.role== CustomUser.Role.ADMIN:
                serializer= CategorySerializer(data=request.data or request.query_params)
                if serializer.is_valid():
                    serializer.save()
                    return map_response(message='Category Added',success=True,data=serializer.data)
                return map_response(message=serializer.errors,success=False)
            return map_response(message='User is not admin',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class CategoryEditDeleteGetView(GenericsRUD):
    model= Category
    serializer_class=CategorySerializer
    queryset=Category.objects.all()


class ListCategoryView(GenericsLC):
    permission_classes=[AllowAny]
    serializer_class= CategorySerializer
    model=Category
    queryset=Category.objects.all()


class AddCategoryView(APIView):
    serializer_class= CategorySerializer

    def post(self,request):
        try:
            if request.user.role==CustomUser.Role.ADMIN:
                serializer= CategorySerializer(data=request.data or request.query_params)
                if serializer.is_valid():
                    serializer.save()
                    return map_response(message='Categories added',success=True,data=serializer.data)
                return map_response(message=serializer.errors,success=False)
            return map_response(message='User must be Admin',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)

class SubCategoryEditDeleteGetView(GenericsRUD):
    serializer_class= SubcategorySerialzer
    model=SubCategory
    queryset=SubCategory.objects.all()

class ListSubcategoryView(GenericsLC):
    permission_classes=[AllowAny]
    serializer_class= SubcategorySerialzer
    model=SubCategory
    queryset= SubCategory.objects.all()

    def list(self,request,*args,**kwargs):
        try:
            search_query=get_value(request,key='search')
            print('------>>>',search_query)
            queryset= self.filter_queryset(self.get_queryset())

            if search_query:
                search_token= search_query.split()
                query_conditions=Q()

                for token in search_token:
                    query_conditions |=Q(email__icontains=token) | Q(username__icontains=token) | Q (
                        id__icontains=token)
                    
                queryset=queryset.filter(query_conditions)
            
            page= self.paginate_queryset(queryset)
            if page is not None:
                serializer= self.get_serializer(page,many=True).data
                print('serializer-->',serializer)
                for obj in serializer:
                    try:
                        category_title= SubCategory.objects.get(id=obj['category']).title
                        print('------>>>',category_title)
                        obj['category_title']=category_title
                    except:
                        pass
                response_data1=self.get_paginated_response(serializer)
                return map_response(message='List is generated',success=True,data=response_data1.data)
            serializer=self.get_serializer(queryset,many=True)
            return map_response(message='List is Generated',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)

class GetServiceBytCategoryView(APIView):

    @extra_schema(
            'ProfessionSearc',['category_id']
    )


    def get(self,request):
        try:
            category_id= get_value(request,key='category_id')
            services= SubCategory.objects.filter(category=category_id)
            serializer= CategorySerializer(services, many=True)
            return map_response(message='Services by Category',success=True,data=serializer.data)
        except Exception as e:
            return map_response(message=str(e),success=False)

class DeleteAgencyReviewView(APIView):
    def delete(self,request):
        try:
            if request.user.role==CustomUser.Role.ADMIN:
                review_id= get_value(request,key='review_id')
                agency_review= AgencyReview.objects.get(id=review_id)
                if agency_review:
                    agency_review.delete()
                    return map_response(message='Review Deleted',success=True)
                return map_response(message='No review found',success=False)
            return map_response(message='You are not admin',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)

                   
#needs to write the profession reiew delete


