from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError

from classes.response.map_reponse import map_response

class CustomModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return map_response(data=list(serializer.data))
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e)
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return map_response(data=dict(serializer.data))
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e)
            )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return map_response(
                data=dict(serializer.data),
                status_code=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid data",
                error=e.detail
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e)
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return map_response(data=dict(serializer.data))
        except ValidationError as e:
            return map_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Invalid data",
                error=e.detail
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e)
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return map_response(
                message="Deleted successfully",
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return map_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred",
                error=str(e)
            )
