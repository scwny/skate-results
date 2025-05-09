from django.urls import path
from .views import CompetitionListView, CompetitionEventListView, EventScheduleView, ping, EventResultsView, competition_event_statuses, LandingPage


urlpatterns = [
    path('ping', ping, name='Ping'),

    path('',LandingPage.as_view(),name='landing_page'),

    # 1) New root → list of Competitions
    path('mayskate/',CompetitionListView.as_view(),name='competition_list'),

    # 2) Competition detail → its Events
    path('competition/<int:pk>/',CompetitionEventListView.as_view(),name='competition_events'),

    # 3) Individual Event schedule 
    path('event/<int:pk>/schedule/', EventScheduleView.as_view(), name='event_schedule'),
    
    # 4) Event Results
    path('event/<int:pk>/results/', EventResultsView.as_view(),  name='event_results'),

    # 5) Event Results
    path('competition/<int:pk>/statuses/',competition_event_statuses,name='competition_event_statuses'),
]