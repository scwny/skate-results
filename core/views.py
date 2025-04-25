from django.shortcuts import render
from decouple import config
from django.views.generic import ListView, DetailView
from .models import Competition, Event

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
    paginate_by         = 500

class EventScheduleView(DetailView):
    model               = Event
    context_object_name = 'event'
    template_name       = 'core/event_schedule.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # related_name for ScheduledSkater → 'event'
        ctx['scheduled_skaters'] = self.object.event.all()
        return ctx


class EventResultsView(DetailView):
    model               = Event
    context_object_name = 'event'
    template_name       = 'core/event_results.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # always show schedule
        ctx['scheduled_skaters'] = self.object.event.all()
        # only show image if finished and has one
        ctx['has_results'] = bool(self.object.status == 'finished' and self.object.result_image)
        return ctx

class CompetitionListView(ListView):
    model               = Competition
    context_object_name = 'competitions'
    template_name       = 'core/competition_list.html'
    paginate_by         = 20  # optional

class CompetitionEventListView(ListView):
    model               = Event
    context_object_name = 'events'
    template_name       = 'core/event_list.html'
    paginate_by         = 25

    def get_queryset(self):
        return Event.objects.filter(competition_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # so your event_list.html can show the parent competition
        ctx['competition'] = Competition.objects.get(pk=self.kwargs['pk'])
        return ctx