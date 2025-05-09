from import_export import resources, fields
from import_export.widgets import (
    ForeignKeyWidget,
    DateWidget,
    TimeWidget
)
from .models import Competition, Event, Club, Skater, ScheduledSkater

class CompetitionResource(resources.ModelResource):
    class Meta:
        model = Competition
        import_id_fields = ['id']
        fields = ('id','name','date')
        skip_unchanged = True
        report_skipped  = True

class ClubResource(resources.ModelResource):
    class Meta:
        model = Club
        import_id_fields = ['id']
        fields = ('id','name')
        skip_unchanged = True
        report_skipped  = True

class SkaterResource(resources.ModelResource):
    club = fields.Field(
        column_name='club_id',
        attribute='club',
        widget=ForeignKeyWidget(Club, 'id')
    )
    class Meta:
        model = Skater
        import_id_fields = ['id']
        fields = ('id','firstName','lastName','club')
        skip_unchanged = True
        report_skipped  = True

class ScheduledSkaterResource(resources.ModelResource):
    event = fields.Field(
        column_name='event_id',
        attribute='event',
        widget=ForeignKeyWidget(Event, 'id')
    )
    skater = fields.Field(
        column_name='skater_id',
        attribute='skater',
        widget=ForeignKeyWidget(Skater, 'id')
    )
    orderNumber = fields.Field(
        column_name='orderNumber',
        attribute='orderNumber'
    )
    scratch = fields.Field(
        column_name='scratch',
        attribute='scratch'
    )
    class Meta:
        model = ScheduledSkater
        import_id_fields = ['event','skater']
        fields = ('event','skater','orderNumber','scratch')
        skip_unchanged = True
        report_skipped  = True

class EventResource(resources.ModelResource):
    competition = fields.Field(
        column_name='competition_id',
        attribute='competition',
        widget=ForeignKeyWidget(Competition, 'id')
    )
    date = fields.Field(
        column_name='date',
        attribute='date',
        widget=DateWidget(format='%Y-%m-%d')
    )
    rink = fields.Field(
        column_name='rink',
        attribute='rink'
    )
    time = fields.Field(
        column_name='time',
        attribute='time',
        widget=TimeWidget(format='%H:%M:%S')
    )
    status = fields.Field(
        column_name='status',
        attribute='status'
    )
    class Meta:
        model = Event
        import_id_fields = ['id']
        fields = (
            'id',
            'competition',
            'eventNumber',
            'name',
            'date',
            'rink',
            'time',
            'status',
        )
        skip_unchanged = True
        report_skipped  = True
