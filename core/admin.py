from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Event, ScheduledSkater, Competition, Skater, Club

class ScheduledSkaterInline(admin.TabularInline):
    model = ScheduledSkater
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'status')
    list_filter  = ('status', 'date')
    inlines      = [ScheduledSkaterInline]

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date' )  # Customize fields as needed
    search_fields = ('name', 'date')  

@admin.register(Skater)
class SkaterAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'club')
    search_fields = ('firstName', 'lastName', 'club')  

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)  