import json
import re
import subprocess
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import language pack related modules
from languages import language_packs, prompt_descriptions

router = APIRouter()

def restart_services():
    """Restart services after prompt update"""
    services = ["api", "roundtable", "celery"]
    for service in services:
        try:
            subprocess.run([
                "supervisorctl", "-c", "supervisord.conf", "restart", service
            ], check=True, capture_output=True, text=True)
            print(f"Successfully restarted {service}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to restart {service}: {e}")
        except Exception as e:
            print(f"Error restarting {service}: {e}")

class PromptUpdateRequest(BaseModel):
    key: str
    content: str | dict
    content_type: str = "string"  # "string" or "dict"
    language: str = "en"

@router.get("/", response_class=HTMLResponse)
async def prompt_editor_page():
    """Display prompt editor page"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Prompt Editor - NexusAI</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            .header p {{
                font-size: 1.1rem;
                opacity: 0.9;
            }}
            .statistics {{
                background: #f8fafc;
                padding: 15px 30px;
                border-bottom: 1px solid #e2e8f0;
                color: #64748b;
                font-size: 14px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .search-bar {{
                padding: 20px 30px;
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }}
            .search-input {{
                width: 100%;
                padding: 12px 20px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.2s;
            }}
            .search-input:focus {{
                outline: none;
                border-color: #4f46e5;
            }}
            .prompts-container {{
                padding: 20px 30px;
                max-height: 70vh;
                overflow-y: auto;
            }}
            
            .group-container {{
                margin-bottom: 30px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                overflow: hidden;
            }}
            .group-header {{
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                padding: 20px 25px;
                font-size: 20px;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.2s;
            }}
            .group-header:hover {{
                background: linear-gradient(135deg, #5856eb 0%, #7c3aed 100%);
            }}
            .group-toggle {{
                font-size: 18px;
                transition: transform 0.2s;
            }}
            .group-toggle.expanded {{
                transform: rotate(90deg);
            }}
            .group-content {{
                background: #fafbff;
                padding: 15px;
                display: none;
            }}
            .group-content.show {{ display: block; }}
            
            .prompt-item {{
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-bottom: 12px;
                overflow: hidden;
                transition: all 0.2s;
                background: white;
            }}
            .prompt-item:hover {{
                border-color: #4f46e5;
                box-shadow: 0 4px 12px rgba(79, 70, 229, 0.1);
            }}
            .prompt-header {{
                background: #f8fafc;
                padding: 16px 20px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: background-color 0.2s;
            }}
            .prompt-header:hover {{
                background: #f1f5f9;
            }}
            .prompt-header.active {{
                background: #4f46e5;
                color: white;
            }}
            .prompt-title {{
                font-weight: 600;
                font-size: 16px;
            }}
            .prompt-toggle {{
                font-size: 18px;
                transition: transform 0.2s;
            }}
            .prompt-toggle.expanded {{
                transform: rotate(90deg);
            }}
            .prompt-content {{
                display: none;
                padding: 20px;
                background: white;
            }}
            .prompt-content.show {{ display: block; }}

            .textarea {{
                width: 100%;
                min-height: 200px;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 13px;
                line-height: 1.5;
                resize: vertical;
                transition: border-color 0.2s;
            }}
            .textarea:focus {{
                outline: none;
                border-color: #4f46e5;
            }}
            .save-button {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                margin-top: 10px;
                transition: all 0.2s;
            }}
            .save-button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            }}
            .save-button:disabled {{
                background: #9ca3af;
                transform: none;
                box-shadow: none;
                cursor: not-allowed;
            }}
            .message {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 1000;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s;
            }}
            .message.show {{
                opacity: 1;
                transform: translateX(0);
            }}
            .message.success {{
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            }}
            .message.error {{
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            }}
            .prompt-key-info {{
                margin-bottom: 15px;
                padding: 10px;
                background: #f0f9ff;
                border-radius: 6px;
                font-size: 12px;
                color: #0369a1;
            }}
            .dict-textarea {{
                border: 2px solid #e5e7eb;
                background: #fafafa;
            }}
            .dict-textarea:focus {{
                border-color: #6366f1;
                background: white;
            }}
            .string-textarea {{
                border: 2px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 NexusAI Prompt Editor</h1>
                <p>Built-in Prompt Quality Debugging Tool</p>
            </div>
            
            <div class="statistics">
                <div>Total Groups: <span id="totalGroups">0</span> | Total Prompts: <span id="totalPrompts">0</span></div>
                <div style="float: right;">
                    <select id="languageSelect" onchange="switchLanguage()" style="padding: 5px; border-radius: 4px; border: 1px solid #d1d5db;">
                        <option value="en">English</option>
                        <option value="zh">Chinese</option>
                    </select>
                </div>
            </div>
            
            <div class="search-bar">
                <input type="text" class="search-input" id="searchInput" placeholder="🔍 Search prompt function...">
            </div>
            
            <div class="prompts-container" id="promptsContainer">
                <!-- Groups and prompts will be loaded here -->
            </div>
        </div>
        
        <div id="message" class="message"></div>
        
        <script>
            let promptData = [];
            let currentLanguage = 'en';
            
            // Load prompt data
            async function loadPromptData() {{
                try {{
                    const response = await fetch('/prompt-editor/api/descriptions');
                    const data = await response.json();
                    promptData = data;
                    renderPrompts();
                    updateStatistics();
                    // Load prompt contents after rendering
                    await loadPromptContents();
                }} catch (error) {{
                    showMessage('❌ Failed to load prompt data', 'error');
                }}
            }}
            
            function renderPrompts() {{
                const container = document.getElementById('promptsContainer');
                const selectedLang = document.getElementById('languageSelect').value;
                const langData = promptData[selectedLang] || [];
                
                let html = '';
                langData.forEach((group, groupIndex) => {{
                    const groupId = `group-${{groupIndex}}`;
                    html += `
                        <div class="group-container" data-group-name="${{group.group_name.toLowerCase()}}">
                            <div class="group-header" onclick="toggleGroup('${{groupId}}')">
                                <div class="group-title">${{group.group_name}}</div>
                                <div class="group-toggle" id="toggle-${{groupId}}">▶</div>
                            </div>
                            <div class="group-content" id="content-${{groupId}}">
                    `;
                    
                    Object.entries(group.prompts).forEach(([key, description]) => {{
                        html += `
                            <div class="prompt-item" data-key="${{key}}" data-description="${{description.toLowerCase()}}">
                                <div class="prompt-header" onclick="togglePrompt('${{key}}')">
                                    <div class="prompt-title">${{description}}</div>
                                    <div class="prompt-toggle" id="toggle-${{key}}">▶</div>
                                </div>
                                <div class="prompt-content" id="content-${{key}}">
                                    <div class="prompt-key-info">
                                        <strong>Prompt Key:</strong> ${{key}}
                                    </div>
                                    
                                    <div id="textarea-container-${{key}}" style="margin-bottom: 15px;">
                                        <!-- Content will be loaded here -->
                                    </div>
                                    
                                    <button class="save-button" onclick="savePrompt('${{key}}')">💾 Save Prompt</button>
                                </div>
                            </div>
                        `;
                    }});
                    
                    html += `
                            </div>
                        </div>
                    `;
                }});
                
                container.innerHTML = html;
            }}
            
            function getPromptContent(key) {{
                // Get English content from language packs via API
                // For now, we'll fetch this separately
                return ''; // Will be populated by separate API call
            }}
            
            function escapeHtml(text) {{
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }}
            
            function toggleGroup(groupId) {{
                const content = document.getElementById('content-' + groupId);
                const toggle = document.getElementById('toggle-' + groupId);
                
                if (content.classList.contains('show')) {{
                    content.classList.remove('show');
                    toggle.classList.remove('expanded');
                }} else {{
                    content.classList.add('show');
                    toggle.classList.add('expanded');
                }}
            }}
            
            function togglePrompt(key) {{
                const content = document.getElementById('content-' + key);
                const toggle = document.getElementById('toggle-' + key);
                const header = content.previousElementSibling;
                
                if (content.classList.contains('show')) {{
                    content.classList.remove('show');
                    toggle.classList.remove('expanded');
                    header.classList.remove('active');
                }} else {{
                    content.classList.add('show');
                    toggle.classList.add('expanded');
                    header.classList.add('active');
                }}
            }}
            
            function switchLanguage() {{
                currentLanguage = document.getElementById('languageSelect').value;
                renderPrompts();
                loadPromptContents();
            }}
            
            function updateStatistics() {{
                const selectedLang = document.getElementById('languageSelect').value;
                const langData = promptData[selectedLang] || [];
                const totalGroups = langData.length;
                const totalPrompts = langData.reduce((sum, group) => sum + Object.keys(group.prompts).length, 0);
                
                document.getElementById('totalGroups').textContent = totalGroups;
                document.getElementById('totalPrompts').textContent = totalPrompts;
            }}
            
            async function loadPromptContents() {{
                const selectedLang = document.getElementById('languageSelect').value;
                const langData = promptData[selectedLang] || [];
                
                for (const group of langData) {{
                    for (const key of Object.keys(group.prompts)) {{
                        try {{
                            const response = await fetch(`/prompt-editor/api/content/${{key}}`);
                            const data = await response.json();
                            const container = document.getElementById(`textarea-container-${{key}}`);
                            
                            if (container && data.content !== undefined) {{
                                if (data.type === 'dict') {{
                                    // Dictionary type: show each sub-key as separate textarea
                                    let dictHtml = '';
                                    for (const [subKey, subValue] of Object.entries(data.content)) {{
                                        const escapedValue = escapeHtml(String(subValue));
                                        dictHtml += `
                                            <div style="margin-bottom: 10px;">
                                                <label style="display: block; font-weight: bold; margin-bottom: 5px; color: #374151;">
                                                    ${{subKey}}:
                                                </label>
                                                <textarea class="textarea dict-textarea" data-subkey="${{subKey}}" data-parentkey="${{key}}" rows="8">${{escapedValue}}</textarea>
                                            </div>
                                        `;
                                    }}
                                    container.innerHTML = dictHtml;
                                }} else {{
                                    // String type: show single textarea
                                    const escapedContent = escapeHtml(String(data.content));
                                    container.innerHTML = `
                                        <textarea class="textarea string-textarea" data-parentkey="${{key}}" rows="12">${{escapedContent}}</textarea>
                                    `;
                                }}
                            }}
                        }} catch (error) {{
                            console.warn(`Failed to load content for ${{key}}`);
                        }}
                    }}
                }}
            }}
            
            function showMessage(text, type = 'success') {{
                const messageEl = document.getElementById('message');
                messageEl.textContent = text;
                messageEl.className = `message ${{type}}`;
                messageEl.classList.add('show');
                
                setTimeout(() => {{
                    messageEl.classList.remove('show');
                }}, 3000);
            }}
            
            async function savePrompt(key) {{
                const button = event.target;
                const container = document.getElementById(`textarea-container-${{key}}`);
                
                button.disabled = true;
                button.textContent = 'Saving...';
                
                try {{
                    let content;
                    let contentType;
                    
                    // Check if it's a dict type (has multiple textareas with data-subkey)
                    const dictTextareas = container.querySelectorAll('.dict-textarea');
                    const stringTextarea = container.querySelector('.string-textarea');
                    
                    if (dictTextareas.length > 0) {{
                        // Dictionary type: collect all sub-keys
                        contentType = 'dict';
                        content = {{}};
                        dictTextareas.forEach(textarea => {{
                            const subKey = textarea.getAttribute('data-subkey');
                            content[subKey] = textarea.value;
                        }});
                    }} else if (stringTextarea) {{
                        // String type: single value
                        contentType = 'string';
                        content = stringTextarea.value;
                    }} else {{
                        throw new Error('No textarea found');
                    }}
                    
                    const response = await fetch('/prompt-editor/save', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            key: key,
                            content: content,
                            content_type: contentType,
                            language: 'en'
                        }})
                    }});
                    
                    const result = await response.json();
                    
                    if (response.ok) {{
                        showMessage(`✅ ${{key}} saved successfully!`, 'success');
                    }} else {{
                        showMessage(`❌ Save failed: ${{result.detail}}`, 'error');
                    }}
                }} catch (error) {{
                    showMessage(`❌ Save failed: ${{error.message}}`, 'error');
                }} finally {{
                    button.disabled = false;
                    button.textContent = '💾 Save Prompt';
                }}
            }}
            
            // Search functionality
            document.getElementById('searchInput').addEventListener('input', function(e) {{
                const searchTerm = e.target.value.toLowerCase();
                const groupContainers = document.querySelectorAll('.group-container');
                
                groupContainers.forEach(groupContainer => {{
                    const groupName = groupContainer.dataset.groupName;
                    const promptItems = groupContainer.querySelectorAll('.prompt-item');
                    let hasVisibleItems = false;
                    
                    promptItems.forEach(item => {{
                        const description = item.dataset.description;
                        const key = item.dataset.key.toLowerCase();
                        
                        if (description.includes(searchTerm) || key.includes(searchTerm) || groupName.includes(searchTerm)) {{
                            item.style.display = 'block';
                            hasVisibleItems = true;
                        }} else {{
                            item.style.display = 'none';
                        }}
                    }});
                    
                    // Show/hide group based on whether it has visible items
                    if (hasVisibleItems || groupName.includes(searchTerm)) {{
                        groupContainer.style.display = 'block';
                        // Auto-expand group if it has matching items
                        if (searchTerm && hasVisibleItems) {{
                            const groupContent = groupContainer.querySelector('.group-content');
                            const groupToggle = groupContainer.querySelector('.group-toggle');
                            groupContent.classList.add('show');
                            groupToggle.classList.add('expanded');
                        }}
                    }} else {{
                        groupContainer.style.display = 'none';
                    }}
                }});
            }});
            
            // Initialize page
            window.addEventListener('load', () => {{
                loadPromptData();
            }});
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/api/descriptions")
async def get_prompt_descriptions():
    """Get prompt descriptions for both languages"""
    return prompt_descriptions

@router.get("/api/content/{key}")
async def get_prompt_content(key: str):
    """Get prompt content for a specific key"""
    try:
        content = language_packs.get("en", {})
        
        # Handle nested keys
        keys = key.split('.')
        for k in keys:
            if isinstance(content, dict):
                content = content.get(k, "")
            else:
                content = ""
                break
        
        # Return different data based on type
        if isinstance(content, dict):
            return {
                "content": content,
                "type": "dict"
            }
        else:
            return {
                "content": str(content),
                "type": "string"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@router.post("/save")
async def save_prompt(request: PromptUpdateRequest):
    """Save single prompt to file"""
    try:
        from datetime import datetime
        
        # Read current languages.py file
        with open("languages.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        key = request.key
        lang = request.language
        new_content = request.content
        content_type = request.content_type
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"languages.py.backup_{timestamp}"
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Force use English since we only edit English prompts  
        lang = "en"
        
        if key not in language_packs[lang]:
            raise HTTPException(status_code=404, detail=f"Unable to locate key: {key} in language_packs[{lang}]")
        
        # Get original content
        original_content = language_packs[lang][key]
        
        # Find the key pattern and replace it
        # Use a simple approach: find the key line and replace its value
        lines = content.split('\n')
        new_lines = []
        i = 0
        found_key = False
        
        while i < len(lines):
            line = lines[i]
            # Look for the key definition (support both single and double quotes)
            if (f'"{key}":' in line or f"'{key}':" in line) and not found_key:
                found_key = True
                # Determine the indentation from the current line
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Determine the quote style used in the original key
                if f'"{key}":' in line:
                    key_quote = '"'
                else:
                    key_quote = "'"
                
                # Determine the triple quote style used in the original value
                original_triple_quote = '"""'  # default
                if line.strip().endswith("'''"):
                    original_triple_quote = "'''"
                elif line.strip().endswith('"""'):
                    original_triple_quote = '"""'
                
                # Build new value string based on content type using original quote style
                if content_type == "dict" and isinstance(new_content, dict):
                    # Dictionary type: format as Python dict with original triple quotes
                    dict_items = []
                    for sub_key, sub_value in new_content.items():
                        # Clean the value and wrap in original triple quotes
                        clean_value = str(sub_value).strip()
                        formatted_value = f'{original_triple_quote}\n            {clean_value}\n        {original_triple_quote}'
                        dict_items.append(f'            "{sub_key}": {formatted_value}')
                    new_value = "{\n" + ",\n".join(dict_items) + "\n        }"
                else:
                    # String type: wrap entire content in original triple quotes
                    clean_content = str(new_content).strip()
                    new_value = f'{original_triple_quote}\n            {clean_content}\n        {original_triple_quote}'
                
                # Check if the value starts on the same line or next line
                if line.strip().endswith('{') or line.strip().endswith('"""') or line.strip().endswith("'''"):
                    # Multi-line value, need to find the end
                    new_lines.append(f'{indent_str}{key_quote}{key}{key_quote}: {new_value},')
                    
                    # Skip until we find the end of the current value
                    i += 1
                    if content_type == "dict":
                        # For dict type, skip until we find the matching closing brace
                        # Need to be careful about braces inside triple quotes
                        brace_count = 1  # Start with 1 since we already have the opening brace
                        in_triple_quotes = False
                        quote_type = None
                        
                        while i < len(lines):
                            current_line = lines[i]
                            line_content = current_line.strip()
                            
                            # Check for triple quote start/end
                            if not in_triple_quotes:
                                if '"""' in current_line:
                                    in_triple_quotes = True
                                    quote_type = '"""'
                                elif "'''" in current_line:
                                    in_triple_quotes = True
                                    quote_type = "'''"
                            else:
                                # We're inside triple quotes, check for end
                                if quote_type in current_line:
                                    # Check if this line ends the triple quote
                                    if line_content.endswith(quote_type) or line_content.endswith(quote_type + ','):
                                        in_triple_quotes = False
                                        quote_type = None
                            
                            # Only count braces when not inside triple quotes
                            if not in_triple_quotes:
                                if '{' in current_line:
                                    brace_count += current_line.count('{')
                                if '}' in current_line:
                                    brace_count -= current_line.count('}')
                                
                                # Check if we've found the matching closing brace
                                if brace_count <= 0:
                                    # Found the end, stop here
                                    break
                            
                            i += 1
                    else:
                        # For string type, skip until we find the end of the matching triple quotes
                        while i < len(lines):
                            current_line = lines[i]
                            line_stripped = current_line.strip()
                            if line_stripped.endswith(original_triple_quote + ',') or \
                               line_stripped.endswith(original_triple_quote) or \
                               line_stripped == original_triple_quote + ',' or \
                               line_stripped == original_triple_quote:
                                # Found the ending line, stop here (don't increment i)
                                break
                            i += 1
                else:
                    # Single line value
                    new_lines.append(f'{indent_str}{key_quote}{key}{key_quote}: {new_value},')
            else:
                new_lines.append(line)
            i += 1
        
        if not found_key:
            raise HTTPException(status_code=404, detail=f"Unable to locate key: {key} in language_packs[{lang}]")
        
        # Write the modified content back to file
        new_content_file = '\n'.join(new_lines)
        with open("languages.py", "w", encoding="utf-8") as f:
            f.write(new_content_file)
        
        # Update language_packs in memory
        if content_type == "dict" and isinstance(new_content, dict):
            language_packs[lang][key] = new_content
        else:
            language_packs[lang][key] = new_content
        
        # Restart services after successful save
        # restart_services()
        
        return {"status": "success", "message": f"Prompt {key} ({lang}) saved successfully"}
        
    except Exception as e:
        # If error occurs, try to restore from backup
        try:
            with open(backup_file, "r", encoding="utf-8") as f:
                backup_content = f.read()
            with open("languages.py", "w", encoding="utf-8") as f:
                f.write(backup_content)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
