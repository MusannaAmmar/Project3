from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.chats.models import *
from classes.response.map_reponse import*
from apps.chats.serializer.serializers import*

class AddCommunityView(APIView):
    @extra_schema(
        'Community',['name','description']
    )

    def post(self,request,*args,**kwargs):
        try:
            name=get_value(request,key='name')
            description=get_value(request,key='description')

            community=Community.objects.create(name=name,description=description)
            community.admin.add(request.user)
            community.members.add(request.user)

            return map_response(message=f'Community created successfully,id:{community.id}',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)

class JoinCommunityView(APIView):
    @extra_schema(
        'community',['community_id']
    )

    def post(self,request,*args,**kwargs):
        try:
            user_id= request.user.id
            community_id=get_value(request,key='community_id')
            community= Community.objects.get(id=community_id)
            user= CustomUser.objects.get(id=user_id)

            if community.members.filter(id=user.id).exists():
                return map_response(message=f'User {user_id} is already a member',success=False)
            
            community.members.add(user)

            return map_response(message=f'User {user_id} joined community',success=True)
        except Community.DoesNotExist:
            return map_response(message='Community Does not exist',success=False)
        except CustomUser.DoesNotExist:
            return map_response(message='User does not exist',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class CommunityListView(APIView):
    def get(self,request):
        try:
            user=request.user

            joined_communities=Community.objects.filter(member=user)
            joined_communities_serializer= CommunitySerializer(joined_communities,many=True).data

            joined_communities_data=[]

            for idx in range(len(joined_communities)):
                community= joined_communities[idx]
                if user.last_login is not None:
                    unread_count= CommunityMessage.objects.filter(
                        community=community,timestamp__gt=user.last_login
                    ).count()
                    unread_count=unread_count if unread_count >0 else None
                else:
                    unread_count=None
                community_data={
                    **joined_communities_serializer[idx],
                    'unread_count':unread_count
                }

                joined_communities_data.append(community_data)

            explore_communities=Community.objects.filter(members=user)
            explore_communities_serializer= CommunitySerializer(explore_communities,many=True).data
            data={
                'joined_communities':joined_communities_data,
                'explore_communities':explore_communities_serializer
            }
            return map_response(message='Community Data Retrieved',success=False,data=data)
        except Exception as e:
            return map_response(message=str(e),success=False)

class PatchCommunityView(APIView):
    @extra_schema(
        'Community',['user_id','action']
    )

    def patch(self,request,*args,**kwargs):
        try:
            community_id= kwargs.get('community_id')
            action= get_value(request,key='action')
            user_id= get_value(request,key='user_id')

            community= Community.objects.get(id=community_id)
            user=CustomUser.objects.get(id=user_id)

            if action=='add_member':
                community.members.add(user)
            elif action=='remove_member':
                community.members.remove(user)
            elif action=='add_admin':
                community.admin.add(user)
            elif action=='remove_admin':
                community.admin.remove(user)
            else:
                return map_response(message='Invalid Action',success=False)
            return map_response(message=f'Action {action} executed successfully',success=True)
        except Community.DoesNotExist:
            return map_response(message='Community Doest not esxist',success=False)
        except CustomUser.DoesNotExist:
            return map_response(message='User does not exists',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class CheckCommunityAdminStatusView(APIView):
    def get(self,request,community_id):
        try:
            community= Community.objects.get(id=community_id)
            community_serializer= CommunitySerializer(community).data

            is_admin= community.admin.filter(id=request.user.id).exists()

            return map_response(message='Community Admins',
                                data={
                                    'is_admin':is_admin,
                                    'community_name':community_serializer['name'],
                                    'community_admins':community_serializer['admin'],
                                    'community_members':community_serializer['members'],
                                    'community_description':community_serializer['description'],
                                    'community_image':community_serializer['display_picture'],
                                },success=True)
        except Community.DoesNotExist:
            return map_response(message='Community not found',success=False)
        except Exception as e:
            return  map_response(message=str(e),success=False)
        







