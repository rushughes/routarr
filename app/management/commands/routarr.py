from django.core.management.base import BaseCommand
from app.models import Tracker, DestinationFolder, Rule, Config
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
                            if rule.tracker.pattern in tracker:
                                dest = rule.destination.path
                                os.rename(full_path, os.path.join(dest, file))
                                matched = True
                                break
                        if matched:
                            break
                    if not matched:
                        config = Config.objects.first()
                        if config:
                            dest = config.default_destination.path
                            os.rename(full_path, os.path.join(dest, file))
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
