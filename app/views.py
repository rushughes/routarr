from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Tracker, DestinationFolder, Rule, Config
import os
import bencodepy
import tempfile
from urllib.parse import urlparse


def upload_torrent(request):
    """Main page for uploading torrents and viewing trackers"""
    if request.method == 'POST':
        if 'torrent_file' in request.FILES:
            torrent_file = request.FILES['torrent_file']
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.torrent') as temp_file:
                for chunk in torrent_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Extract trackers from torrent
                trackers = extract_trackers(temp_path)
                
                # Get existing trackers for comparison
                existing_trackers = list(Tracker.objects.values_list('pattern', flat=True))
                
                # Prepare tracker data
                tracker_data = []
                for tracker in trackers:
                    tracker_data.append({
                        'url': tracker,
                        'exists': is_tracker_matched(tracker, existing_trackers)
                    })
                
                context = {
                    'trackers': tracker_data,
                    'torrent_name': torrent_file.name
                }
                
                # Clean up temp file
                os.unlink(temp_path)
                
                return render(request, 'app/upload_torrent.html', context)
                
            except Exception as e:
                messages.error(request, f'Error processing torrent file: {str(e)}')
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
    
    return render(request, 'app/upload_torrent.html')


def extract_trackers(torrent_path):
    """Extract tracker URLs from a torrent file"""
    trackers = []
    try:
        with open(torrent_path, 'rb') as f:
            meta = bencodepy.decode(f.read())
            if b'announce' in meta:
                trackers.append(meta[b'announce'].decode())
            if b'announce-list' in meta:
                for tier in meta[b'announce-list']:
                    for url in tier:
                        trackers.append(url.decode())
    except Exception as e:
        raise Exception(f"Failed to parse torrent file: {str(e)}")
    
    return list(set(trackers))  # Remove duplicates


def is_tracker_matched(tracker_url, existing_patterns):
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


@csrf_exempt
@require_http_methods(["POST"])
def add_tracker(request):
    """Add a tracker to the database via AJAX"""
    try:
        tracker_url = request.POST.get('tracker_url')
        if not tracker_url:
            return JsonResponse({'success': False, 'error': 'No tracker URL provided'})
        
        # Create a pattern from the tracker URL (extract domain)
        parsed = urlparse(tracker_url)
        pattern = parsed.netloc
        
        # Check if tracker already exists
        if Tracker.objects.filter(pattern=pattern).exists():
            return JsonResponse({'success': False, 'error': 'Tracker already exists'})
        
        # Create new tracker
        tracker = Tracker.objects.create(pattern=pattern)
        
        return JsonResponse({
            'success': True, 
            'tracker_id': tracker.id,
            'pattern': tracker.pattern
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def list_directories(request):
    """List directories in the filesystem for the directory browser"""
    try:
        path = request.GET.get('path', '/')
        
        # Security: prevent directory traversal attacks
        if '..' in path or path.startswith('/etc') or path.startswith('/proc'):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        if not os.path.exists(path):
            return JsonResponse({'error': 'Path does not exist'}, status=404)
        
        if not os.path.isdir(path):
            return JsonResponse({'error': 'Path is not a directory'}, status=400)
        
        # Get directories in the path
        directories = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    directories.append({
                        'name': item,
                        'path': item_path,
                        'readable': os.access(item_path, os.R_OK)
                    })
        except PermissionError:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Sort directories alphabetically
        directories.sort(key=lambda x: x['name'].lower())
        
        return JsonResponse({
            'directories': directories,
            'current_path': path,
            'parent_path': os.path.dirname(path) if path != '/' else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def dashboard(request):
    """Dashboard showing current trackers, destinations, and rules"""
    trackers = Tracker.objects.all()
    destinations = DestinationFolder.objects.all()
    rules = Rule.objects.all()
    config = Config.objects.first()
    
    context = {
        'trackers': trackers,
        'destinations': destinations,
        'rules': rules,
        'config': config
    }
    
    return render(request, 'app/dashboard.html', context) 