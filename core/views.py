from django.shortcuts import render
from decouple import config
from django.views.generic import ListView, DetailView
from .models import Event

# Create your views here.
from django.http import HttpResponse

def ping(request):
    return HttpResponse(f"pong! {config('AWS_ACCESS_KEY_ID')}")


def competitions(request):
    return HttpResponse(f"Competitions")

class EventListView(ListView):
    model               = Event
    context_object_name = 'events'
    template_name       = 'core/event_list.html'
    paginate_by         = 25

class EventScheduleView(DetailView):
    model               = Event
    context_object_name = 'event'
    template_name       = 'core/event_schedule.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # related_name for ScheduledSkater → 'event'
        ctx['scheduled_skaters'] = self.object.event.all()
        return ctx