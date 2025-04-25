from django.urls import path
from .views import EventListView, EventScheduleView, ping, EventResultsView


urlpatterns = [
    path('ping', ping, name='Ping'),
    path('',                  EventListView.as_view(),      name='event_list'),
    path('event/<int:pk>/schedule/',      EventScheduleView.as_view(), name='event_schedule'),
    path('event/<int:pk>/results/',       EventResultsView.as_view(),  name='event_results'),
]
