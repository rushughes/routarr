from django.contrib import admin
from .models import Tracker, DestinationFolder, Rule, Config

admin.site.register(Tracker)
admin.site.register(DestinationFolder)
admin.site.register(Rule)
admin.site.register(Config)
