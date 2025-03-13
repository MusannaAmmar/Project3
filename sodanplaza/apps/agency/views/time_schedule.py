from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from apps.agency.models import *
from classes.response.map_reponse import map_response


class GetAgencyHoursView(APIView):
    @extra_schema(
            'Agencyhours',['agency_id']
        )
    def get(self,request):
        agency_id= get_value(request,key='agency_id')
        hours= AgencyHours.objects.get(agency=agency_id)

        hours_data=[
            {
                'day_of_week':hour.day_of_week,
                'opening_time':hour.opening_time,
                'closing_time':hour.closing_time,
            }
            for hour in hours
        ]
        return map_response(message=f'Working hours of bussiness {agency_id}',data=hours_data,success=True)

class AddAgencyHoursView(APIView):
    @extra_schema(
        'Addagencyhours',['agency_id','day_of_week','opening_time','closing_time']
    )

    def post(self,request):
        agency_id= get_value(request,key='agency_id')
        data= request.data or request.query_params
        day_of_week= data.get('day_of_week')
        opening_time=data.get('opening_time')
        closing_time=data.get('closing_time')

        if not (day_of_week and opening_time and closing_time):
            return map_response(message='Details required',success=False)
        
        try:
            hour_entry,created= AgencyHours.objects.create(
                agency_id=agency_id,
                day_of_week=day_of_week,
                defaults={'opening_time':opening_time,'closing_time':closing_time}
            )

            return map_response(
                message='Agency Hours Added',
                data={
                    'day_of_week':hour_entry.day_of_week,
                    'opening_time':hour_entry.opening_time,
                    'closing_time':hour_entry.closing_time,
                },
                success=True
            )
        
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class DeleteAgencyHoursView(APIView):
    @extra_schema(
        'DeleteAgencyHours',['agency_id','day_of_week']
    )

    def delete(self,request):
        agency_id= get_value(request,key='agency_id')
        data= request.data or request.query_params

        day_of_week= data.get('day_of_week')
        if not day_of_week:
            return map_response(message='Day of week is required',success=False)
        
        try:
            agency_hours=AgencyHours.objects.filter(agency_id=agency_id,day_of_week=day_of_week).first()

            if agency_hours:
                agency_hours.delete()
                return map_response(message='Hours Deleted Succesfully',success=False)
        except Exception as e:
            return map_response(message=str(e),success=False)
        
class PatchAgencyHoursView(APIView):
    @extra_schema(
        'PatchHours',['agency_id','day_of_week','opening_time','closing_time']
    )

    def patch(self,request):
        agency_id= get_value(request,key='agency_id')
        data=request.data or request.query_params

        day_of_week= data.get('day_of_week')
        opening_time=data.get('opening_time')
        closing_time=data.get('closing_time')


        if not day_of_week:
            return map_response(message='day_of_week is required',success=False)
        try:
            agency_hours,created= AgencyHours.objects.update(
                agency_id=agency_id,
                day_of_week=day_of_week,
                defaults={
                    'opening_time':opening_time,
                    'closing_time':closing_time,
                },
    
            )
            return map_response(
                message='Hours Saved',
                data={
                    'day_of_week':agency_hours.day_of_week,
                    'opening_time':agency_hours.opening_time,
                    'closing_time':agency_hours.closing_time,
                },
                success=True
            )
        except Exception as e:
            return map_response(message=str(e),success=False)
    
    





        



        
        

        










        









     
       



    