from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.profession.models import*
from apps.users.models import *
from apps.users.serializers.app_profile_serializer import*
from classes.response.map_reponse import map_response
from django.shortcuts import get_object_or_404
from apps.agency.models import *


class AttachAgencyView(APIView):

    @extra_schema(
        'AttachAgency',['profession_id','business_id']
    )


    def patch(self,request):
        try:
            profession_id=get_value(request,key='profession_id')
            business_id=get_value(request,key='business_id')

            profession_instance= ProfessionProfile.objects.get(id=profession_id)
            profession_serializer= ProfessionProfileSerializer(profession_instance)
            profession_serializer_copy=profession_serializer.data.copy()
            profession_serializer_copy['agency_attach']=True
            profession_serializer_copy['agency']=business_id

            request=RequestAttachAgency.objects.get(professioon=profession_id,agency=business_id)
            request.request_status=True
            request.save()
            return map_response(message='Profession Added',success=True,data=profession_serializer_copy)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class RequestAttachAgencyView(APIView):
    @extra_schema(
        'requestattach',['business_id']
    )

    def patch(self,request):
        try:
            user=request.user
            agency_id= get_value(request,key='business_id')
            agency= AgencyProfile.objects.get(id=agency_id)
            profession= ProfessionProfile.objects.get(user=user)

            previous_instance_delete= RequestAttachAgency.objects.filter(profession=profession,
                                                                         agency_id=agency_id).delete()
            
            request_instance= RequestAttachAgency.objects.create(profession=profession,agency_id=agency_id)

            profession.request_agency=agency
            profession.save()
            return map_response(message='Request Sent',success=False)
        
        except Exception as e:
            return map_response(message=str(e,),success=False)

class AcceptInviteView(APIView):
    @extra_schema(
        'AttachProfession',['agency_id']
    )

    def patch(self,request):
        try:
            user= request.user
            agency= get_value(request,key='agency_id')
            profession= get_object_or_404(ProfessionProfile,user=user)
            agency_instance= get_object_or_404(AgencyProfile,id=agency)
            invite_instance= get_object_or_404(InviteMembers,profession=profession,agency_id=agency)

            agency_employe= AgencyEmploye.objects.filter(agency=agency_instance,profession=profession).first()
            if agency_employe:
                return map_response(message='Agency Employe Exists',success=True)
            
            agency_employe_instance= AgencyEmploye.objects.create(agency=agency_instance,profession=profession)

            agency_instance.employee_count+=1
            agency_instance.save()

            invite_instance.invite_status=True
            profession.agency=invite_instance.agency
            profession.save()
            return map_response(message='Invite accepted',success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)


        

