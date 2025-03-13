from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from classes.response.map_reponse import map_response
from classes.utils import get_value


class GenericsRUD(generics.RetrieveUpdateDestroyAPIView):
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return map_response(message='data retrieved',data=dict(serializer.data), success=True)
        except Exception as e:
            return map_response(
                
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e),
                success=False
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return map_response(message='data updated',data=dict(serializer.data), success=True)
        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid data",
                error=e.detail,
                success=False
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e),
                success=False
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # instance.is_deleted=True
            instance.delete()
            return map_response(
                message="Deleted successfully",
                status_code=status.HTTP_200_OK,
                success=True
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e),
                success=False
            )


class GenericsLC(generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return map_response(
                data=dict(serializer.data),
                status_code=status.HTTP_201_CREATED,
                success=True
            )
        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid data",
                error=e.detail,
                success=False
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e),
                success=False
            )

    def list(self, request, *args, **kwargs):
        try:
            search_query = get_value(request, key='search')

            queryset = self.filter_queryset(self.get_queryset())
            
            if search_query:
                # Split the search query into tokens to allow partial matching
                search_tokens = search_query.split()
                query_conditions = Q()

                # Build OR conditions for each token and relevant fields
                for token in search_tokens:
                    query_conditions |= Q(email__icontains=token) | Q(username__icontains=token) | Q(
                        id__icontains=token)

                queryset = queryset.filter(query_conditions)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response_data1= self.get_paginated_response(serializer.data)
                print(response_data1)
                return map_response(message='List is generated', data=response_data1.data, success=True)
                return response_data1

            serializer = self.get_serializer(queryset, many=True)
            return map_response(message='List is generated', data=list(serializer.data), success=True)
        except Exception as e:
                
            return map_response(message=str(e), success=False)
