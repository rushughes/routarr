from django.db import models

class Tracker(models.Model):
    pattern = models.CharField(max_length=255, help_text="Tracker domain or pattern to match against torrent URLs")
    description = models.TextField(blank=True, help_text="Optional description for this tracker")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Tracker: {self.pattern}"
    
    class Meta:
        verbose_name = "Tracker"
        verbose_name_plural = "Trackers"

class DestinationFolder(models.Model):
    path = models.CharField(max_length=255, help_text="Full path to the qBittorrent watch folder")
    description = models.TextField(blank=True, help_text="Optional description for this destination")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Destination: {self.path}"
    
    class Meta:
        verbose_name = "Destination Folder"
        verbose_name_plural = "Destination Folders"

class Rule(models.Model):
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE, help_text="Select the tracker to match")
    destination = models.ForeignKey(DestinationFolder, on_delete=models.CASCADE, help_text="Select the destination folder")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rule: {self.tracker.pattern} → {self.destination.path}"
    
    class Meta:
        verbose_name = "Routing Rule"
        verbose_name_plural = "Routing Rules"

class Config(models.Model):
    default_destination = models.ForeignKey(DestinationFolder, on_delete=models.SET_NULL, null=True, blank=True, help_text="Default destination for unmatched torrents")
    
    def __str__(self):
        if self.default_destination:
            return f"Default: {self.default_destination.path}"
        return "Default: None"
    
    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configuration"
