from rest_framework.views import APIView
from classes.extra_schema import extra_schema
from classes.utils import get_value
from classes.response.map_reponse import map_response
from apps.agency.models import AgencyProfile
from django.db.models import Q,F
from apps.users.models import ProfessionProfile
from apps.profession.models import Gig,GigSelectedService
from datetime import timedelta,datetime
import json
from apps.users.serializers.app_profile_serializer import ProfessionProfileSerializer
from apps.profession.serializer.serializers import GigSelectedServiceSerializer
from apps.agency.models import AgencyServices
from apps.agency.serializers.profile_serializers import AgencyProfileSerializer,AgencyServicesSerializer
from django.contrib.postgres.search import SearchQuery,SearchVector,SearchRank
from apps.administration.models import SubCategory
from apps.administration.serializer.serializers import SubcategorySerialzer


class MultiModelSearchView(APIView):
    @extra_schema(
        'Search',['query','+location','+tags','+date_posted','+stars']
    )

    def get(self,request,*args,**kwargs):
        try:
            query= get_value(request,key='query')
            location=get_value(request,key='location')
            tags=get_value(request,key='tags')
            date_posted=get_value(request,key='date_posted')
            stars_param=request.query_params.get('stars',[])

            if not query:
                return map_response(message='Search Query is required',success=False)
            

            #Agecny Profile Search
            agency_results=AgencyProfile.objects.filter(
                Q(business_name__icontains=query)|
                Q(city__icontains=query)|
                Q(state__icontains=query)|
                Q(country__icontains=query)|
                Q(category_title__icontains=query)

            )

            #Profession Profile
            profession_results=ProfessionProfile.objects.filter(
                Q(first_name__icontains=query)|
                Q(city__icontains=query)|
                Q(state__icontains=query)|
                Q(category_title__icontains=query)
            )

            # Gig Search 
            gig_results= Gig.objects.filter(
                Q(title__icontains=query)|
                Q(description__icontains=query)|
                Q(meta_title__icontains=query)|
                Q(meta_description__icontains=query)|
                Q(category_title__icontains=query) |
                Q(profession__first_name__icontains=query) |
                Q(gigselectedservice__service__title__icontains=query)|
                Q(gigselectedlocation__location__icontains=query) |
                Q(gigreview_review__icontains=query)|
                Q(gigfaq_question__icontains=query) |
                Q(giglanguage__question__icontains=query),
                is_publish=True
            ).distinct()

            if date_posted:
                now=datetime.now()
                if date_posted.lower()=='today':
                    start_date= now.replace(hour=0,minute=0,second=0,microsecond=0)
                    end_date=now
                elif date_posted.lower()=='yesterday':
                    start_date=(now -timedelta(days=1)).replace(hour=0,minute=0,second=0,microsecond=0)
                elif date_posted.lower=='last_week':
                    start_date=timedelta(weeks=1)
                    end_date=now
                elif date_posted.lower=='last_month':
                    start_date=timedelta(days=30)
                    end_date=now
                else:
                    start_date=None
                    end_date=None
                if start_date and end_date:
                    agency_results=agency_results.filter(
                        created_at__range=(start_date,end_date)
                    )
                    profession_results=profession_results.filter(
                        created_at__range=(start_date,end_date)
                    )
                    gig_results=gig_results.filter(
                        created_at__range=(start_date,end_date)
                    )
            if stars_param:
                star_ratings=json.loads(stars_param)
                if star_ratings:
                    star_filter=Q()
                    if 1 in star_ratings:
                        star_filter |=Q(one_star__gt=0)
                    if 2 in star_ratings:
                        star_filter|=Q(two_star__gt=0)
                    if 3 in star_ratings:
                        star_filter|=Q(three_star__gt=0)
                    if 4 in star_ratings:
                        star_filter|=Q(four_star__gt=0)
                    if 5 in star_ratings:
                        star_filter|=Q(five_star__gt=0)
                    
                    agency_results=agency_results.filter(star_filter)
                    profession_results=profession_results.filter(star_filter)

            gigs_list=[]
            for gig in gig_results:
                gig_data={
                    'id':gig.id,
                    'title':gig.title,
                    'description':gig.description,
                    'created_at':gig.created_at,
                    'is_available':gig.is_available,
                    'meta_title':gig.meta_title,
                    'slug':gig.slug,
                    'category_id':gig.category.id,
                    'profession_id':gig.profession.id,
                    'profession_profile':ProfessionProfileSerializer(gig.profession).data,
                    'skills':GigSelectedServiceSerializer(gig.gigselectedskill_set.all(),many=True).data,
                }

                gigs_list.append(gig_data)

            service_results=AgencyServices.objects.filter(
                service__title__icontains=query
            )

            agency_serializer= AgencyProfileSerializer(agency_results,many=True).data
            profession_serializer=ProfessionProfileSerializer(profession_results,many=True).data
            service_serializer= AgencyServicesSerializer(service_results,many=True).data

            data={
                'agency_results':agency_serializer,
                'profession_results':profession_serializer,
                'service_results':service_serializer
            }

            return map_response(message='Retrieved Data',data=data,success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)
class MultiModelSearchSuggestionView(APIView):
    def get(self,request,*args,**kwargs):
        try:
            query=request.query_params.get('quer').strip().lower()
            location=request.query_params.get('location','').strip().lower()

            if not query or len(query)<2:
                return map_response(message='Query length is too short',success=False)
            
            agency_search_filter =  Q(business_description__icontains=query) | \
                                    Q(business_name__icontains=query) | \
                                    Q(agencyservices__service__title__icontains=query)|\
                                    Q(category__title__icontains=query)
            gig_search_filter=  Q(title__icontains=query)| \
                                Q(description__icontains=query) | \
                                Q(gigselectedservice__skill__title__icontains=query)| \
                                Q(category_title__icontains=query)
            location_filter=Q(city__icontains=location)|\
                            Q(state__icontains=location)|\
                            Q(country__icontains=location)
            agency_results=AgencyProfile.objects.filter(agency_search_filter)

            gig_results=Gig.objects.filter(gig_search_filter,is_publish=True)

            if location:
                agency_results=agency_results.filter(location_filter)

            matched_results=set()

            #Collect Matches from Agency

            matched_results.update(
                agency_results.values_list('business_name',flat=True).distinct()
            )

            matched_results.update(
                agency_results.values_list('category_title',flat=True).distinct()
            )

            matched_results.update(
                agency_results.values_list('agencyservices__service__title',flat=True).distinct()
            )

            #Collect Matches from Gig

            matched_results.update(
                gig_results.values_list('title',flat=True).distinct()
            )

            matched_results.update(
                gig_results.values_list('gigselectedservice__service__title',flat=True).distinct()
            )
            matched_results.update(
                gig_results.values_list('category_title',flat=True).distinct
            )

            # Collect Matches from gig skills
            gig_skill_matches=gig_results.values_list(
                'gigselectedskill',flat=True
            ).distinct()
            matched_results.update(gig_skill_matches)

            # Return only distinct mactches containing the query
            filtered_results= [f'{match},{location}' for match in matched_results if match and query in match.lower()]
            return map_response(
                message='Search results retrieved successfully',
                success=True,data=filtered_results
            )
        except Exception as e:
            return map_response(message=str(e),success=False)


class AgencyProfileSearchView(APIView):
    @extra_schema(
        'AgencySearch',['query']
    )

    def get(self,request,*args,**kwargs):
        try:
            query=get_value(request,key='query')
            if not query:
                return map_response(message='search query is required',success=False)
            search_query= SearchQuery(query)

            #Agency Profile Search
            agency_profile_vector=(
                SearchVector('business_name',weight='A')+
                SearchVector('city',weight='B')+
                SearchVector('state',weight='B')+
                SearchVector('coutry',weight='C')+
                SearchVector('business_website',weight='D')+
                SearchVector('category_title',weight='A')
            )

            agency_results= AgencyProfile.objects.annotate(
                rank=SearchRank(agency_profile_vector,search_query),
                category_title=F('category_title')
            ).filter(rank__gte=0.1).order_by('-rank')
            agency_results= list(agency_results.values())

            return map_response(data=agency_results,message='Retrieved Data of Agency',success=True)
        except Exception as e:
            return map_response(message=str(e),success=False)
        

class ProfessionProfileSearchView(APIView):
    @extra_schema(
        'ProfessionProfile',['query']
    )

    def get(self,request,*args,**kwargs):
        try:
            query=get_value(request,key='query')
            if not query:
                return map_response(message='Search Query is required',success=False)
            
            search_query= SearchQuery(query)

            search_profile_vector=(
                SearchVector('first_name',weight='A')+
                SearchVector('city',weight='B')+
                SearchVector('state',weight='B')+
                SearchVector('email',weight='A')+
                SearchVector('category_title',weight='A')
            )
            profession_results=ProfessionProfile.objects.annotate(
                rank=SearchRank(search_profile_vector,search_query),
                category_title=F('category_title')
            ).filter(rank__gte=0.1).order_by('-rank')

            profession_results= list(profession_results.values())
            return map_response(message='Profession Profile Retrieved',success=True,data=profession_results)
        except Exception as e:
            return map_response(message=str(e),success=False)

class ServiceSuggestionView(APIView):
    def get(self,request):
        try:
            services= SubCategory.objects.all().order_by('-search_count')
            serializer_data=[]

            for service in services:
                serializer=SubcategorySerialzer(service).data
                serializer['category_title']=service.category.title
                serializer_data.append(serializer)

            return map_response(message='Service Suggestion',success=True,data=serializer_data)
        except Exception as e:
            return map_response(message=str(e),success=False)





                                
                            