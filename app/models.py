from django.db import models

class Tracker(models.Model):
    pattern = models.CharField(max_length=255)

class DestinationFolder(models.Model):
    path = models.CharField(max_length=255)

class Rule(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    destination = models.ForeignKey(DestinationFolder, on_delete=models.CASCADE)

class Config(models.Model):
    default_destination = models.ForeignKey(DestinationFolder, on_delete=models.SET_NULL, null=True)
