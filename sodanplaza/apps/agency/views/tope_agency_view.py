from rest_framework.views import APIView
from apps.agency.models import*
from apps.agency.serializers.profile_serializers import*
from classes.response.map_reponse import map_response


class GetTopAgencyView(APIView):
    def get(self,request):
        try:
            sorting= AgencyProfile.objects.order_by('-ratings')
            serializer= AgencyProfileSerializer(sorting,many=True).data
            return map_response(message='Top Agencies List',success=True,data=serializer)
        except Exception as e:
            return map_response(message=str(e),success=False)

