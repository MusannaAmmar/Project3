from rest_framework.views import APIView
from classes.response.map_reponse import map_response
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.users.serializers.quote_serializer import*
from apps.agency.models import AgencyProfile
from apps.chats.models import generate_room_name
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.chats.models import ChatMessage


class SendQuoteView(APIView):
    @extra_schema(
        'VerifyOTP',['+profession_id','+agency_id','quotation','address','budget','message']
    )

    def post(self,request):
        try:
            data=request.data
            user=request.user
            profession_id= get_value(request,key='profession_id')
            agency_id= get_value(request,key='agency_id')

            if not agency_id and not profession_id:
                return map_response(message='Receiver id is required',success=False)
            
            data={
                'quotation':data.get('quotation'),
                'address':data.get('address'),
                'budget':data.get('budget'),
                'message':data.get('message'),
                'profession':int(profession_id) if profession_id else None,
                'agency':int(agency_id) if agency_id else None,
                'user':user.id
            }

            quote_serializer= QuoteSerializer(data=data)
            if quote_serializer.is_valid():
                quote_serializer.save()
                if profession_id:
                    profession=ProfessionProfile.objects.get(id=profession_id)
                    receiver_id= profession.user.id
                else:
                    agency=AgencyProfile.objects.get(id=agency_id)
                    receiver_id= agency.user.id
                receiver_instance= CustomUser.objects.get(id=receiver_id)
                room_name=generate_room_name(user,receiver_id)

                channel_layer= get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'{room_name}',
                    {
                        'type':'chat_message',
                        'messages':str(quote_serializer.data),
                        'sender':user,
                        'receiver':receiver_instance
                    }
                )
                ChatMessage.objects.create(sender=user,receiver=receiver_id,message=str(quote_serializer.data),room_name=room_name)
                quote_serializer_data=quote_serializer.data
                quote_serializer_data['room_name']=room_name
                return map_response(message='Quote requested',data=quote_serializer_data,success=True)
            else:
                return map_response(message=quote_serializer.errors,success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
