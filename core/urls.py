from django.urls import path
from .views import EventListView, EventScheduleView, ping


urlpatterns = [
    path('ping', ping, name='Ping'),
    path('',                  EventListView.as_view(),      name='event_list'),
    path('event/<int:pk>/',   EventScheduleView.as_view(),  name='event_schedule'),
]
