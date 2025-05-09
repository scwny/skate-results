from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Competition, Event, Club, Skater, ScheduledSkater

class CompetitionResource(resources.ModelResource):
    class Meta:
        model = Competition
        import_id_fields = ['id']
        fields = ('id','name','date')
        skip_unchanged = True
        report_skipped  = True

class EventResource(resources.ModelResource):
    competition = fields.Field(
        column_name='competition_id',
        attribute='competition',
        widget=ForeignKeyWidget(Competition, 'id')
    )
    class Meta:
        model = Event
        import_id_fields = ['id']
        fields = (
            'id','competition','eventNumber','name',
            'date','rink','time'
        )
        skip_unchanged = True
        report_skipped  = True

class ClubResource(resources.ModelResource):
    class Meta:
        model = Club
        import_id_fields = ['id']
        fields = ('id','name','country')
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
    event  = fields.Field(
        column_name='event_id',
        attribute='event',
        widget=ForeignKeyWidget(Event, 'id')
    )
    skater = fields.Field(
        column_name='skater_id',
        attribute='skater',
        widget=ForeignKeyWidget(Skater, 'id')
    )
    class Meta:
        model = ScheduledSkater
        # we’ll use (event,skater) as our natural key to detect changes
        import_id_fields = ['event','skater']
        fields = ('event','skater','orderNumber')
        skip_unchanged = True
        report_skipped  = True
