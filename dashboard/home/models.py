from django.db import models

class NTDdata(models.Model):
    Date = models.CharField(max_length=200)
    High = models.FloatField()
    Low = models.FloatField()
    Close = models.FloatField()
    