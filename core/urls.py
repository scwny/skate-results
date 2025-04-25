from django.urls import path
from .views import CompetitionListView, CompetitionEventListView, EventScheduleView, ping, EventResultsView


urlpatterns = [
    path('ping', ping, name='Ping'),
        
    # 1) New root → list of Competitions
    path('',CompetitionListView.as_view(),name='competition_list'),

    # 2) Competition detail → its Events
    path('competition/<int:pk>/',CompetitionEventListView.as_view(),name='competition_events'),

    # 3) Individual Event schedule 
    path('event/<int:pk>/schedule/', EventScheduleView.as_view(), name='event_schedule'),
    
    # 4) Event Results
    path('event/<int:pk>/results/', EventResultsView.as_view(),  name='event_results'),
]