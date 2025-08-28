#!/usr/bin/env python3
"""
Template generator for creating new projects from the running-log template.
This script creates a new project by copying the running-log structure and 
replacing project-specific names with new values.
"""

import os
import shutil
import sys
import re
from pathlib import Path

def replace_in_file(file_path, replacements):
    """Replace text in a file based on the replacements dictionary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for old, new in replacements.items():
            content = re.sub(old, new, content, flags=re.IGNORECASE)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Warning: Could not process {file_path}: {e}")

def create_project_from_template(template_path, new_project_name, destination_path):
    """Create a new project from the running-log template."""
    
    # Define replacements
    replacements = {
        r'running-log': new_project_name.lower().replace('_', '-'),
        r'running_log': new_project_name.lower().replace('-', '_'),
        r'RunningLog': ''.join(word.capitalize() for word in new_project_name.replace('-', '_').split('_')),
        r'RUNNING_LOG': new_project_name.upper().replace('-', '_'),
        r'runs': 'items',  # Generic term for data entities
        r'Runs': 'Items',
        r'RUNS': 'ITEMS',
        r'run_': 'item_',
        r'Run([A-Z])': r'Item\1',  # RunsTable -> ItemsTable
        r'running': 'tracking',  # Generic activity
        r'Running': 'Tracking',
    }
    
    # Create destination directory
    dest_dir = Path(destination_path) / new_project_name
    if dest_dir.exists():
        print(f"Error: Directory {dest_dir} already exists!")
        return False
    
    print(f"Creating new project '{new_project_name}' in {dest_dir}")
    
    # Copy the entire template directory
    shutil.copytree(template_path, dest_dir, ignore=shutil.ignore_patterns(
        '.git', '__pycache__', 'node_modules', '.aws-sam', 'dist', '.vite'
    ))
    
    # Files to process for text replacement
    text_files = [
        '**/*.py', '**/*.ts', '**/*.js', '**/*.vue', '**/*.json', 
        '**/*.yaml', '**/*.yml', '**/*.md', '**/*.txt', '**/*.toml',
        '**/*.html', '**/*.css'
    ]
    
    # Process files
    for pattern in text_files:
        for file_path in dest_dir.glob(pattern):
            if file_path.is_file():
                replace_in_file(file_path, replacements)
    
    # Rename specific directories and files
    rename_mapping = {
        'runs': 'items',
        'running-log': new_project_name.lower().replace('_', '-')
    }
    
    # Rename directories and files
    for root, dirs, files in os.walk(dest_dir, topdown=False):
        # Rename files
        for file in files:
            old_path = Path(root) / file
            new_name = file
            for old, new in rename_mapping.items():
                new_name = new_name.replace(old, new)
            if new_name != file:
                new_path = Path(root) / new_name
                old_path.rename(new_path)
        
        # Rename directories
        for dir_name in dirs:
            old_path = Path(root) / dir_name
            new_name = dir_name
            for old, new in rename_mapping.items():
                new_name = new_name.replace(old, new)
            if new_name != dir_name:
                new_path = Path(root) / new_name
                old_path.rename(new_path)
    
    # Create a customization guide
    guide_content = f"""# {new_project_name} - Customization Guide

This project was generated from the running-log template. Here's what you need to customize:

## 1. Backend Customization (backend/src/items/)
- Update the data models in `models/` to match your domain
- Modify the DAL (Data Access Layer) in `dal/` for your data operations
- Customize the API endpoints in `app.py`

## 2. Frontend Customization (frontend/src/)
- Update components to match your application's purpose
- Modify the navigation and routing in `router/index.ts`
- Customize the UI components in `components/`
- Update the API service in `services/api.ts`

## 3. Database Schema (backend/template.yaml)
- Modify the DynamoDB table schemas to match your data model
- Update the table names and attributes

## 4. Authentication
- The Cognito setup is ready to use
- Customize user attributes in the CloudFormation template if needed

## 5. Deployment
- Update `backend/samconfig.toml` with your stack name
- Configure your AWS credentials
- Run `sam deploy --guided` for initial deployment

## Next Steps
1. Install dependencies: `npm install` in frontend/, `pip install -r requirements.txt` in backend/
2. Run tests: `npm run test:unit` and `pytest`
3. Start development: `npm run dev` for frontend
4. Deploy: `sam deploy` for backend

Happy coding!
"""
    
    with open(dest_dir / 'CUSTOMIZATION_GUIDE.md', 'w') as f:
        f.write(guide_content)
    
    print(f"✅ Project '{new_project_name}' created successfully!")
    print(f"📍 Location: {dest_dir}")
    print(f"📖 Check CUSTOMIZATION_GUIDE.md for next steps")
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python create-template.py <new_project_name> <destination_path>")
        print("Example: python create-template.py my-tracker-app ../")
        sys.exit(1)
    
    new_project_name = sys.argv[1]
    destination_path = sys.argv[2]
    
    # Validate project name
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', new_project_name):
        print("Error: Project name must start with a letter and contain only letters, numbers, hyphens, and underscores")
        sys.exit(1)
    
    # Get the template path (current directory)
    template_path = Path(__file__).parent
    
    success = create_project_from_template(template_path, new_project_name, destination_path)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()