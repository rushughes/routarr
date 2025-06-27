from django.core.management.base import BaseCommand
from app.models import Tracker, DestinationFolder, Rule, Config
from urllib.parse import urlparse
import os, time, bencodepy

WATCH_DIR = '/incoming'

class Command(BaseCommand):
    help = 'Routarr daemon'

    def handle(self, *args, **options):
        while True:
            for file in os.listdir(WATCH_DIR):
                if file.endswith('.torrent'):
                    full_path = os.path.join(WATCH_DIR, file)
                    trackers = self.get_trackers(full_path)
                    matched = False
                    for rule in Rule.objects.all():
                        for tracker in trackers:
                            if self.is_tracker_matched(tracker, [rule.tracker.pattern]):
                                dest = rule.destination.path
                                os.rename(full_path, os.path.join(dest, file))
                                matched = True
                                self.stdout.write(f"Moved {file} to {dest} (matched {rule.tracker.pattern})")
                                break
                        if matched:
                            break
                    if not matched:
                        config = Config.objects.first()
                        if config and config.default_destination:
                            dest = config.default_destination.path
                            os.rename(full_path, os.path.join(dest, file))
                            self.stdout.write(f"Moved {file} to default destination {dest}")
                        else:
                            self.stdout.write(f"No rule or default destination found for {file}")
            time.sleep(5)

    def get_trackers(self, torrent_path):
        trackers = []
        with open(torrent_path, 'rb') as f:
            meta = bencodepy.decode(f.read())
            if b'announce' in meta:
                trackers.append(meta[b'announce'].decode())
            if b'announce-list' in meta:
                for tier in meta[b'announce-list']:
                    for url in tier:
                        trackers.append(url.decode())
        return trackers

    def is_tracker_matched(self, tracker_url, existing_patterns):
        """
        Check if a tracker URL matches any existing patterns using proper domain matching.
        
        Args:
            tracker_url: The full tracker URL (e.g., "https://tracker.torrentleech.org/announce")
            existing_patterns: List of existing tracker patterns in the database
        
        Returns:
            bool: True if the tracker matches any existing pattern
        """
        try:
            # Parse the tracker URL to extract the domain
            parsed_url = urlparse(tracker_url)
            tracker_domain = parsed_url.netloc.lower()
            
            # Check each existing pattern
            for pattern in existing_patterns:
                pattern_lower = pattern.lower()
                
                # If the pattern is a domain (contains dots), do exact domain matching
                if '.' in pattern_lower:
                    if tracker_domain == pattern_lower:
                        return True
                else:
                    # If the pattern is a simple string, check if it's contained in the domain
                    # but only as a complete word to avoid partial matches
                    if pattern_lower in tracker_domain:
                        # Check if it's a complete word (not part of another word)
                        import re
                        if re.search(r'\b' + re.escape(pattern_lower) + r'\b', tracker_domain):
                            return True
            
            return False
            
        except Exception:
            # If URL parsing fails, fall back to simple substring matching
            tracker_lower = tracker_url.lower()
            return any(pattern.lower() in tracker_lower for pattern in existing_patterns)
