from django.shortcuts import render
from decouple import config
from django.views.generic import ListView, DetailView, TemplateView
from .models import Competition, Event, ScheduledSkater, Skater, Club
from django.db.models import Q
import logging
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


logger = logging.getLogger(__name__)

# Create your views here.
from django.http import HttpResponse

def ping(request):
    return HttpResponse(f"pong! {config('AWS_ACCESS_KEY_ID')}")


def competitions(request):
    return HttpResponse(f"Competitions")

class LandingPage(TemplateView):
    context_object_name = 'landing'
    template_name       = 'core/index.html'

class EventScheduleView(DetailView):
    model               = Event
    context_object_name = 'event'
    template_name       = 'core/event_schedule.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # related_name for ScheduledSkater → 'event'
        ctx['scheduled_skaters'] = (
            ScheduledSkater.objects
            .filter(event=self.object)
            .order_by('orderNumber')
        )
        return ctx


class EventResultsView(DetailView):
    model               = Event
    context_object_name = 'event'
    template_name       = 'core/event_results.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # always show schedule
        ctx['scheduled_skaters'] = (
            ScheduledSkater.objects
            .filter(event=self.object)
            .order_by('orderNumber')
        )

        # only show image if finished and has one+        
        ctx['has_results'] = bool(self.object.status == 'finished'and self.object.external_image_url)        
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
    paginate_by         = None

    def get_queryset(self):
        qs = (
            Event.objects
            .filter(competition_id=self.kwargs['pk'],display=True)
            .prefetch_related(
            'event__skater__club'
            )
            .distinct()
        )
        # Read GET parameters
        event_name = self.request.GET.get('event_name', '')
        skater_name = self.request.GET.get('skater_name', '')
        club_name = self.request.GET.get('club_name', '')

        logger.info(f"Filters: event_name={event_name}, skater_name={skater_name}, club_name={club_name}")
        
        if event_name:
            qs = qs.filter(name__icontains=event_name)

        if skater_name:
            qs = qs.filter(
                Q(event__skater__firstName__icontains=skater_name) |
                Q(event__skater__lastName__icontains=skater_name)
            )

        if club_name:
            qs = qs.filter(
                event__skater__club__name__icontains=club_name
            )

        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['competition'] = get_object_or_404(Competition, pk=self.kwargs['pk'])
        ctx['filters'] = {
            'event_name': self.request.GET.get('event_name', ''),
            'skater_name': self.request.GET.get('skater_name', ''),
            'club_name': self.request.GET.get('club_name', ''),
        }
        # Pass all clubs so we can build a dropdown or datalist
        from .models import Club
        ctx['clubs'] = Club.objects.order_by('name').values_list('name', flat=True)

        return ctx
    
    
def competition_event_statuses(request, pk):
    events = Event.objects.filter(competition_id=pk)
    data = []
    for e in events:
        data.append({
            'id': e.pk,
            'status': e.status,
            'has_results': bool(e.status == 'finished'  and e.external_image_url),
        })
    return JsonResponse({'events': data})