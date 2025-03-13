from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.administration.models import SiteSettings
from apps.administration.serializer.serializers import*
from apps.users.serializers.auth_serializer import CustomerUserSerializer
from classes.response.map_reponse import map_response


class SiteSettingView(APIView):
    @extra_schema(
        'site_settings',['+site_title','+site_description','+site_logo','+site_hero','+site_footer','+name',
                         '+new_password','+google','+apple']
    )

    def patch(self,request):
        try:
            user=request.user
            site_title=get_value(request,key='site_title')
            site_description=get_value(request,key='site_description')
            site_logo=get_value(request,key='site_logo')
            site_hero=get_value(request,key='site_hero')
            site_footer=get_value(request,key='site_footer')
            name=get_value(request,key='name')
            new_password=get_value(request,key='new_password')
            google=get_value(request,key='google')
            apple=get_value(request,key='apple')

            site_instance=SiteSettings.objects.get(id=1)

            site_instance.site_title=site_title if site_title else site_instance.site_title
            site_instance.site_description=site_description if site_description else site_instance.site_description
            site_instance.site_logo=site_logo if site_logo else site_instance.site_logo
            site_instance.site_hero=site_hero if site_hero else site_instance.site_hero
            site_instance.site_footer=site_footer if site_footer else site_instance.site_footer
            site_instance.apple_login= apple if apple else site_instance.apple_login
            site_instance.google_login=google if google else site_instance.google_login

            user.username=name if name else user.username

            if new_password:
                user.set_password(new_password)
            user.save()

            site_instance.save()

            site_serializer=SiteSettingSerializer(site_instance).data
            user_serializer=CustomerUserSerializer(user).data

            data={
                'site_serializer':site_serializer,
                'user_serializer':user_serializer
            }

            return map_response(message='Site Settings Updated',success=True,data=data)
        except Exception as e:
            return map_response(message=str(e),success=False)



