from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Tracker, DestinationFolder, Rule, Config


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('pattern', 'id', 'created_at')
    search_fields = ('pattern',)
    ordering = ('pattern',)
    
    fieldsets = (
        ('Tracker Information', {
            'fields': ('pattern',),
            'description': 'Enter the tracker domain or pattern to match against torrent tracker URLs.'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at',)
        return ()
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new object
            from django.utils import timezone
            obj.created_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(DestinationFolder)
class DestinationFolderAdmin(admin.ModelAdmin):
    list_display = ('path', 'id', 'description', 'created_at')
    search_fields = ('path', 'description')
    ordering = ('path',)
    
    fieldsets = (
        ('Folder Information', {
            'fields': ('path', 'description'),
            'description': 'Enter the full path to the qBittorrent watch folder where torrents should be moved.'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at',)
        return ()
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new object
            from django.utils import timezone
            obj.created_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('tracker', 'destination', 'id', 'created_at')
    list_filter = ('tracker', 'destination')
    search_fields = ('tracker__pattern', 'destination__path')
    ordering = ('tracker__pattern',)
    
    fieldsets = (
        ('Routing Rule', {
            'fields': ('tracker', 'destination'),
            'description': 'Create a rule that routes torrents from a specific tracker to a destination folder.'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('created_at',)
        return ()
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new object
            from django.utils import timezone
            obj.created_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('default_destination', 'id')
    
    fieldsets = (
        ('Default Configuration', {
            'fields': ('default_destination',),
            'description': 'Set the default destination folder for torrents that don\'t match any rules.'
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one config object
        return not Config.objects.exists()


# Customize the admin site
admin.site.site_header = "🚀 Routarr Administration"
admin.site.site_title = "Routarr Admin"
admin.site.index_title = "Welcome to Routarr Administration"

# Add a custom admin template to include dashboard link
class RoutarrAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('dashboard')
        return super().index(request, extra_context)

# Override the default admin site
admin.site.__class__ = RoutarrAdminSite
