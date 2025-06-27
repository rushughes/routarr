from django import forms
from django.contrib.admin import widgets
from django.utils.html import format_html
from django.urls import reverse
from .models import DestinationFolder


class DirectoryPathWidget(forms.TextInput):
    """Custom widget for directory path selection with file browser"""
    
    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs.update({
            'class': 'vTextField directory-path-input',
            'readonly': 'readonly',
            'style': 'background-color: #f8f9fa; cursor: pointer;'
        })
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with file browser button"""
        html = super().render(name, value, attrs, renderer)
        
        # Add file browser button and modal
        browser_html = format_html('''
            <div class="directory-path-container" style="display: flex; gap: 10px; align-items: center;">
                {input_html}
                <button type="button" class="directory-browser-btn" 
                        style="padding: 8px 16px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer;"
                        onclick="openDirectoryBrowser('{input_id}')">
                    📁 Browse
                </button>
            </div>
            
            <!-- Directory Browser Modal -->
            <div id="directoryModal" class="modal" style="display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);">
                <div class="modal-content" style="background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 600px; border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h3>Select Directory</h3>
                        <span class="close" onclick="closeDirectoryBrowser()" style="color: #aaa; font-size: 28px; font-weight: bold; cursor: pointer;">&times;</span>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <input type="text" id="currentPath" value="/" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 10px;">
                        <button onclick="navigateUp()" style="padding: 5px 10px; margin-right: 10px;">⬆️ Up</button>
                        <button onclick="refreshDirectory()" style="padding: 5px 10px;">🔄 Refresh</button>
                    </div>
                    
                    <div id="directoryList" style="border: 1px solid #ddd; height: 300px; overflow-y: auto; padding: 10px; background: white;">
                        <div style="text-align: center; color: #666; padding: 20px;">
                            Loading directories...
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px; text-align: right;">
                        <button onclick="closeDirectoryBrowser()" style="padding: 8px 16px; margin-right: 10px; background: #6c757d; color: white; border: none; border-radius: 4px;">Cancel</button>
                        <button onclick="selectCurrentDirectory()" style="padding: 8px 16px; background: #007cba; color: white; border: none; border-radius: 4px;">Select Directory</button>
                    </div>
                </div>
            </div>
            
            <script>
                let currentInputId = '';
                let currentDirectory = '/';
                
                function openDirectoryBrowser(inputId) {{
                    currentInputId = inputId;
                    document.getElementById('directoryModal').style.display = 'block';
                    loadDirectory(currentDirectory);
                }}
                
                function closeDirectoryBrowser() {{
                    document.getElementById('directoryModal').style.display = 'none';
                }}
                
                function loadDirectory(path) {{
                    currentDirectory = path;
                    document.getElementById('currentPath').value = path;
                    
                    const directoryList = document.getElementById('directoryList');
                    directoryList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">Loading...</div>';
                    
                    // Make AJAX call to get directory contents
                    fetch('{list_directories_url}?path=' + encodeURIComponent(path))
                        .then(response => response.json())
                        .then(data => {{
                            if (data.error) {{
                                directoryList.innerHTML = '<div style="text-align: center; color: #dc3545; padding: 20px;">Error: ' + data.error + '</div>';
                                return;
                            }}
                            
                            directoryList.innerHTML = '';
                            
                            if (data.directories.length === 0) {{
                                directoryList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">No directories found</div>';
                                return;
                            }}
                            
                            data.directories.forEach(dir => {{
                                const dirDiv = document.createElement('div');
                                dirDiv.style.cssText = 'padding: 8px; cursor: pointer; border-bottom: 1px solid #eee; display: flex; align-items: center;';
                                dirDiv.innerHTML = '📁 ' + dir.name;
                                dirDiv.onclick = () => loadDirectory(dir.path);
                                dirDiv.onmouseover = () => dirDiv.style.backgroundColor = '#f8f9fa';
                                dirDiv.onmouseout = () => dirDiv.style.backgroundColor = 'transparent';
                                
                                if (!dir.readable) {{
                                    dirDiv.style.opacity = '0.5';
                                    dirDiv.style.cursor = 'not-allowed';
                                    dirDiv.onclick = null;
                                }}
                                
                                directoryList.appendChild(dirDiv);
                            }});
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            directoryList.innerHTML = '<div style="text-align: center; color: #dc3545; padding: 20px;">Failed to load directories</div>';
                        }});
                }}
                
                function navigateUp() {{
                    const path = currentDirectory.split('/').slice(0, -1).join('/') || '/';
                    loadDirectory(path);
                }}
                
                function refreshDirectory() {{
                    loadDirectory(currentDirectory);
                }}
                
                function selectCurrentDirectory() {{
                    document.getElementById(currentInputId).value = currentDirectory;
                    closeDirectoryBrowser();
                }}
                
                // Close modal when clicking outside
                window.onclick = function(event) {{
                    const modal = document.getElementById('directoryModal');
                    if (event.target == modal) {{
                        closeDirectoryBrowser();
                    }}
                }}
            </script>
        ''', input_html=html, input_id=attrs.get('id', name), list_directories_url=reverse('list_directories'))
        
        return browser_html


class DestinationFolderForm(forms.ModelForm):
    """Custom form for DestinationFolder with directory browser"""
    
    class Meta:
        model = DestinationFolder
        fields = ['path', 'description']
        widgets = {
            'path': DirectoryPathWidget(),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        } 