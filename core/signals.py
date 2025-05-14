# core/signals.py

from django.db import transaction
from django.dispatch import receiver
from import_export.signals import post_import
from .resources import EventResource, ScheduledSkaterResource
from .models import Event, ScheduledSkater

@receiver(post_import, sender=EventResource)
def delete_event_orphans(sender, **kwargs):
    """
    After importing Events, delete any Event whose id
    was NOT in the imported CSV.
    """
    dataset = kwargs.get('dataset')  # Tablib Dataset
    imported_ids = {row['id'] for row in dataset.dict}

    # wrap in a transaction so import + delete is atomic
    with transaction.atomic():
        Event.objects.exclude(id__in=imported_ids).delete()


@receiver(post_import, sender=ScheduledSkaterResource)
def delete_scheduled_skaters_orphans(sender, **kwargs):
    """
    After importing ScheduledSkaters, delete any ScheduledSkater
    whose (event_id, skater_id) pair was NOT in the CSV.
    """
    dataset = kwargs.get('dataset')
    imported_pairs = {
        (row['event_id'], row['skater_id'])
        for row in dataset.dict
    }

    with transaction.atomic():
        # We can’t bulk‐delete easily on a composite key, so loop
        for ss in ScheduledSkater.objects.all():
            if (ss.event_id, ss.skater_id) not in imported_pairs:
                ss.delete()
