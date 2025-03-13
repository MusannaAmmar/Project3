from apps.chats.models import*
from rest_framework.views import APIView
from apps.users.models import*
from apps.users.serializers.app_profile_serializer import*
from apps.agency.models import*
from apps.agency.serializers.profile_serializers import*
from classes.extra_schema import extra_schema
from classes.utils import get_value
from classes.response.map_reponse import map_response
from django.db.models import Max,Count,Q


def fetch_chat_details(request,chats):
    user=request.user
    chat_list=[]
    for chat in chats:
        room_name=chat['room_name']
        last_message=ChatMessage.objects.filter(room_name=room_name).latest('timestamp')
        room,user_1,user_2=room_name.split('_')
        other_user= CustomUser.objects.get(id=user_1) if request.user.id==int(user_1) else CustomUser.objects.get(
            id=user_2)
        
        if other_user.role==CustomUser.Role.PROFESSION:
            profession_profile=ProfessionProfile.objects.get(user=other_user)
            profession_profile_serializer= ProfessionProfileSerializer(profession_profile).data
            profession_profile=profession_profile_serializer
            agency_profile=None
            user_profile=None
        elif other_user.role==CustomUser.Role.AGENCY:
            agency_profile=AgencyProfile.objects.get(user=other_user)
            agency_profile_serializer=AgencyProfileSerializer(agency_profile).data
            agency_profile=agency_profile_serializer
            user_profile=None
            profession_profile=None
        elif other_user.role==CustomUser.Role.USER:
            user_profile= UserProfile.objects.get(user=other_user)
            user_profile_serializer=UserProfileSerializer(user_profile).data
            user_profile=user_profile_serializer
            agency_profile=None
            profession_profile=None
        else:
            pass
        chat_list.append({
            'room_name':room_name,
            'receiver':last_message.receiver.id if last_message.sender==user else last_message.sender.id,
            'last_message':last_message.message,
            'is_seen':last_message.is_seen,
            'unread_count':chat['unread_count'],
            'role':other_user.role,
            'profession_profile':profession_profile,
            'user_profile':user_profile,
            'agency_profile':agency_profile
        })

    return chat_list

class ChattingView(APIView):
    @extra_schema(
        'chatting',['room_name']
    )

    def post(self,request):
        try:
            room_name= get_value(request,key='room_name')
            room=ChatMessage.objects.filter(room_name=room_name)

            if room.exists():
                messages= room.order_by('timestamp')

                messages_dict=[
                    {
                        'sender':message.sender.id,
                        'receiver':message.receiver.id,
                        'message':message.message,
                        'timestamp':message.timestamp,
                    }
                    for message in messages
                ]

                return map_response(message='Chatting Message View',success=True,data={
                    'room_name':room_name,
                    'message':messages_dict,
                })
            else:
                return map_response(message='Room does not exist',success=False)
        except Exception as e:
            map_response(message=str(e),success=False)

class UserChatView(APIView):
    def get(self,request):
        try:
            user=request.user
            archived_chats= ChatMessage.objects.filter(
                Q(sender=user)| Q(receiver=user), is_archived=True
            ).values(
                'room_name'
            ).annotate(
                last_message=Max('timestamp'),
                unread_count= Count('id',filter=Q(receiver=user,is_seen=False))
            ).order_by('-last_message')

            active_chats= ChatMessage.objects.filter(
                Q(sender=user) | Q(receiver=user),is_archived=False
            ).values(
                'room_name'
            ).annotate(
                last_message= Max('timestamp'),
                unread_count=Count('id',filter=Q(receiver=user,is_seen=False))
            ).order_by('-last_message')

            archived_chat_list= fetch_chat_details(request,archived_chats)
            archived_chat_list=fetch_chat_details(request,active_chats)

            return map_response(
                success=True,
                message='List of user chats retrieve successfully',
                data={
                    'archived_chats':archived_chat_list,
                    'active_chats':active_chats
                }
            )
        except Exception as e:
            return map_response(message=str(e),success=False)
        
