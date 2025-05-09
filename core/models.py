from django.db import models


class Competition(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    logo =  models.ImageField(upload_to='Competitions/', blank=True, null=True)

    class Meta:
        ordering = ['date' , 'name']
    
    def __str__(self):
        return f"{self.name}"


class Event(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('finished',  'Finished'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name="competition",null=True, blank=True)
    eventNumber = models.IntegerField()
    name        = models.CharField(max_length=255)
    date        = models.DateField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    result_image = models.ImageField(upload_to='results/', blank=True, null=True)
    ocr_text    = models.TextField(blank=True, null=True)
    rink        = models.CharField(max_length=255, null=True)
    time        = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['date', 'eventNumber']

    def __str__(self):
        return f"{self.eventNumber} - {self.name}"

class Club(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2, default='US')      # ← new field
    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"


class Skater(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club" ,null=True, blank=True)
    
    class Meta:
        ordering = ['lastName', 'firstName']

    def __str__(self):
        return f"{self.firstName} {self.lastName} - {self.club}"

class ScheduledSkater(models.Model):
    event        = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event')
    skater       = models.ForeignKey(Skater, on_delete=models.CASCADE, related_name='skater')
    orderNumber  = models.PositiveIntegerField()

    class Meta:
        ordering = ['orderNumber']

    def __str__(self):
        return f"{self.orderNumber}. {self.skater}"
