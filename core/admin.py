from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Event, ScheduledSkater, Competition, Skater, Club
from .resources import (
    CompetitionResource,
    EventResource,
    ClubResource,
    SkaterResource,
    ScheduledSkaterResource,
)

class ScheduledSkaterInline(admin.TabularInline):
    model = ScheduledSkater
    extra = 1

@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_class = EventResource
    list_display  = ('name', 'date', 'status', 'display')
    list_filter   = ('status', 'date')
    list_editable = ('display',)
    inlines       = [ScheduledSkaterInline]

@admin.register(Competition)
class CompetitionAdmin(ImportExportModelAdmin):
    resource_class = CompetitionResource
    list_display   = ('name', 'date')
    search_fields  = ('name', 'date')

@admin.register(Club)
class ClubAdmin(ImportExportModelAdmin):
    resource_class = ClubResource
    list_display   = ('name',)
    search_fields  = ('name',)

@admin.register(Skater)
class SkaterAdmin(ImportExportModelAdmin):
    resource_class = SkaterResource
    list_display   = ('firstName', 'lastName', 'club')
    search_fields  = ('firstName', 'lastName', 'club')

@admin.register(ScheduledSkater)
class ScheduledSkaterAdmin(ImportExportModelAdmin):
    resource_class = ScheduledSkaterResource
    list_display   = ('event', 'skater', 'orderNumber')
    search_fields  = ('event__name', 'skater__firstName', 'skater__lastName')