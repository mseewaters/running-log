#!/usr/bin/env python3
"""
Minimal template generator for Vue.js + Python Lambda serverless applications.
Creates only the foundational framework files without app-specific content.
"""

import os
import re
import sys
from pathlib import Path

def create_minimal_template(project_name, destination_path):
    """Create a minimal serverless template with just the foundational files."""
    
    # Create project structure
    dest_dir = Path(destination_path) / project_name
    if dest_dir.exists():
        print(f"Error: Directory {dest_dir} already exists!")
        return False
    
    print(f"Creating minimal template '{project_name}' in {dest_dir}")
    
    # Project structure
    structure = {
        'frontend': {
            'src': {
                'components': {},
                'services': {},
                'stores': {},
                'router': {},
                'assets': {}
            },
            'public': {}
        },
        'backend': {
            'src': {
                project_name.replace('-', '_'): {
                    'models': {},
                    'dal': {},
                    'auth': {}
                }
            },
            'tests': {}
        }
    }
    
    # Create directory structure
    def create_dirs(base_path, structure):
        for name, subdirs in structure.items():
            dir_path = base_path / name
            dir_path.mkdir(parents=True, exist_ok=True)
            if subdirs:
                create_dirs(dir_path, subdirs)
    
    create_dirs(dest_dir, structure)
    
    # Frontend package.json
    frontend_package = f'''{{
  "name": "{project_name}-frontend",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test:unit": "vitest",
    "type-check": "vue-tsc --build",
    "lint": "eslint . --fix",
    "format": "prettier --write src/"
  }},
  "dependencies": {{
    "@headlessui/vue": "^1.7.23",
    "@heroicons/vue": "^2.2.0",
    "@vueuse/core": "^13.3.0",
    "axios": "^1.9.0",
    "pinia": "^3.0.1",
    "vue": "^3.5.13",
    "vue-router": "^4.5.0"
  }},
  "devDependencies": {{
    "@tsconfig/node22": "^22.0.1",
    "@types/jsdom": "^21.1.7",
    "@types/node": "^22.14.0",
    "@vitejs/plugin-vue": "^5.2.3",
    "@vitest/eslint-plugin": "^1.1.39",
    "@vue/eslint-config-prettier": "^10.2.0",
    "@vue/eslint-config-typescript": "^14.5.0",
    "@vue/test-utils": "^2.4.6",
    "@vue/tsconfig": "^0.7.0",
    "eslint": "^9.22.0",
    "eslint-plugin-vue": "~10.0.0",
    "jiti": "^2.4.2",
    "jsdom": "^26.0.0",
    "npm-run-all2": "^7.0.2",
    "prettier": "3.5.3",
    "typescript": "~5.8.0",
    "vite": "^6.2.4",
    "vite-plugin-vue-devtools": "^7.7.2",
    "vitest": "^3.1.1",
    "vue-tsc": "^2.2.8"
  }}
}}'''
    
    # Frontend main.ts
    frontend_main = '''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')'''
    
    # Frontend App.vue
    frontend_app = '''<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>'''
    
    # Frontend router
    frontend_router = '''import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../components/HomePage.vue')
    }
  ]
})

export default router'''
    
    # API service
    api_service = '''import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api'''
    
    # Basic HomePage component
    home_component = '''<template>
  <div class="home">
    <h1>Welcome to {{ projectName }}</h1>
    <p>Your serverless application is ready!</p>
  </div>
</template>

<script setup lang="ts">
const projectName = 'Your App'
</script>

<style scoped>
.home {
  padding: 2rem;
  text-align: center;
}
</style>'''
    
    # Vite config
    vite_config = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': new URL('./src', import.meta.url).pathname
    }
  }
})'''
    
    # Frontend index.html
    index_html = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>'''
    
    # Backend SAM template
    sam_template = f'''AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: {project_name} serverless backend

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.13
    Environment:
      Variables:
        ITEMS_TABLE: !Ref ItemsTable
        USERS_TABLE: !Ref UsersTable
        COGNITO_USER_POOL_ID: !Ref UserPool
        COGNITO_CLIENT_ID: !Ref UserPoolClient
        JWT_SECRET: "your-jwt-secret-key"
  Api:
    Cors:
      AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
      AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
      AllowOrigin: "'*'"

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/{project_name.replace("-", "_")}/
      Handler: app.lambda_handler
      Runtime: python3.13
      Events:
        RootApi:
          Type: Api
          Properties:
            Path: /
            Method: ANY
        ProxyApi:
          Type: Api
          Properties:
            Path: /{{proxy+}}
            Method: ANY
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref ItemsTable
        - DynamoDBCrudPolicy:
            TableName: !Ref UsersTable

  ItemsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${{AWS::StackName}}-Items"
      AttributeDefinitions:
        - AttributeName: user_id
          AttributeType: S
        - AttributeName: item_id
          AttributeType: S
      KeySchema:
        - AttributeName: user_id
          KeyType: HASH
        - AttributeName: item_id
          KeyType: RANGE
      BillingMode: PAY_PER_REQUEST

  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${{AWS::StackName}}-Users"
      AttributeDefinitions:
        - AttributeName: user_id
          AttributeType: S
        - AttributeName: email
          AttributeType: S
      KeySchema:
        - AttributeName: user_id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: email-index
          KeySchema:
            - AttributeName: email
              KeyType: HASH
          Projection:
            ProjectionType: ALL
      BillingMode: PAY_PER_REQUEST

  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: !Sub "${{AWS::StackName}}-user-pool"
      UsernameAttributes: [email]
      AutoVerifiedAttributes: [email]

  UserPoolClient:
    Type: AWS::Cognito::UserPoolClient
    Properties:
      UserPoolId: !Ref UserPool
      ClientName: !Sub "${{AWS::StackName}}-client"
      GenerateSecret: false
      ExplicitAuthFlows:
        - ALLOW_USER_PASSWORD_AUTH
        - ALLOW_REFRESH_TOKEN_AUTH

Outputs:
  ApiUrl:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${{ServerlessRestApi}}.execute-api.${{AWS::Region}}.amazonaws.com/Prod/"'''
    
    # Backend app.py
    backend_app = f'''import json
import os
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for {project_name} API
    """
    
    # CORS headers
    headers = {{
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
    }}
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {{
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }}
    
    # Basic health check
    if event.get('path') == '/' and event.get('httpMethod') == 'GET':
        return {{
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({{'message': '{project_name} API is running!'}})
        }}
    
    # Default response
    return {{
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({{'error': 'Not found'}})
    }}'''
    
    # Backend requirements.txt
    requirements = '''boto3==1.34.0
PyJWT==2.8.0
requests==2.31.0'''
    
    # Basic user model
    user_model = '''import uuid
from datetime import datetime
from typing import Optional

class User:
    def __init__(
        self,
        email: str,
        first_name: str,
        last_name: str,
        user_id: str = None
    ):
        self.user_id = user_id or str(uuid.uuid4())
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        user = cls(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_id=data.get('user_id')
        )
        if 'created_at' in data:
            user.created_at = data['created_at']
        return user'''
    
    # JWT middleware
    jwt_middleware = '''import jwt
from datetime import datetime

def extract_user_id_from_token(token: str, secret: str) -> str:
    """Extract user ID from JWT token"""
    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        return decoded.get('sub')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_auth_header(event: dict, secret: str) -> str:
    """Validate Authorization header and return user ID"""
    auth_header = event.get('headers', {}).get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    return extract_user_id_from_token(token, secret)'''
    
    # TypeScript configurations
    tsconfig_json = '''{
  "files": [],
  "references": [
    {
      "path": "./tsconfig.node.json"
    },
    {
      "path": "./tsconfig.app.json"
    },
    {
      "path": "./tsconfig.vitest.json"
    }
  ]
}'''
    
    tsconfig_app = '''{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "include": ["env.d.ts", "src/**/*", "src/**/*.vue"],
  "exclude": ["src/**/__tests__/*"],
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}'''
    
    tsconfig_node = '''{
  "extends": "@tsconfig/node22/tsconfig.json",
  "include": [
    "vite.config.*",
    "vitest.config.*",
    "cypress.config.*",
    "nightwatch.conf.*",
    "playwright.config.*",
    "eslint.config.*"
  ],
  "compilerOptions": {
    "noEmit": true,
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "types": ["node"]
  }
}'''
    
    tsconfig_vitest = '''{
  "extends": "./tsconfig.app.json",
  "include": ["src/**/__tests__/*", "env.d.ts"],
  "exclude": [],
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.vitest.tsbuildinfo",
    "lib": [],
    "types": ["node", "jsdom"]
  }
}'''
    
    # ESLint configuration
    eslint_config = '''import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import pluginVitest from '@vitest/eslint-plugin'
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  
  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },
  skipFormatting,
)'''
    
    # Vitest configuration
    vitest_config = '''import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
    },
  }),
)'''
    
    # Environment files
    env_development = f'''# Development environment variables
VITE_API_BASE_URL=http://localhost:3000
VITE_ENVIRONMENT=development'''
    
    env_production = f'''# Production environment variables  
VITE_API_BASE_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/Prod
VITE_ENVIRONMENT=production'''
    
    # Environment type definitions
    env_d_ts = '''/// <reference types="vite/client" />'''
    
    # SAM configuration
    samconfig_toml = f'''version = 0.1

# Development Environment
[dev.deploy.parameters]
stack_name = "{project_name}-dev"
resolve_s3 = true
s3_prefix = "{project_name}-dev"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
image_repositories = []
parameter_overrides = [
    "Environment=dev"
]

# Production Environment  
[prod.deploy.parameters]
stack_name = "{project_name}-prod"
resolve_s3 = true
s3_prefix = "{project_name}-prod"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
image_repositories = []
parameter_overrides = [
    "Environment=prod"
]

# Keep default as prod for backward compatibility
[default.deploy.parameters]
stack_name = "{project_name}"
resolve_s3 = true
s3_prefix = "{project_name}"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
image_repositories = []'''
    
    # Pytest configuration
    pytest_ini = '''[tool:pytest]
testpaths = tests backend/tests src/tests
python_paths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
addopts = -v --tb=short
filterwarnings =
    ignore::pytest.PytestDeprecationWarning
    ignore::DeprecationWarning:botocore.*
    ignore::DeprecationWarning:*datetime*'''
    
    # Root package.json for project-level scripts
    root_package = f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "private": true,
  "scripts": {{
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && sam local start-api",
    "build:frontend": "cd frontend && npm run build",
    "build:backend": "cd backend && sam build",
    "test:frontend": "cd frontend && npm run test:unit",
    "test:backend": "cd backend && pytest",
    "test": "npm run test:frontend && npm run test:backend",
    "deploy:dev": "cd backend && sam deploy --config-env dev",
    "deploy:prod": "cd backend && sam deploy --config-env prod",
    "setup": "cd frontend && npm install && cd ../backend && pip install -r src/{project_name.replace("-", "_")}/requirements.txt"
  }},
  "description": "{project_name} - Full-stack serverless application",
  "keywords": ["serverless", "vue", "lambda", "dynamodb"],
  "author": "",
  "license": "ISC"
}}'''
    
    # Write all files
    files_to_create = {
        # Root level files
        'package.json': root_package,
        
        # Frontend files
        'frontend/package.json': frontend_package,
        'frontend/index.html': index_html,
        'frontend/vite.config.ts': vite_config,
        'frontend/vitest.config.ts': vitest_config,
        'frontend/tsconfig.json': tsconfig_json,
        'frontend/tsconfig.app.json': tsconfig_app,
        'frontend/tsconfig.node.json': tsconfig_node,
        'frontend/tsconfig.vitest.json': tsconfig_vitest,
        'frontend/eslint.config.ts': eslint_config,
        'frontend/env.d.ts': env_d_ts,
        'frontend/.env.development': env_development,
        'frontend/.env.production': env_production,
        'frontend/src/main.ts': frontend_main,
        'frontend/src/App.vue': frontend_app,
        'frontend/src/router/index.ts': frontend_router,
        'frontend/src/services/api.ts': api_service,
        'frontend/src/components/HomePage.vue': home_component,
        
        # Backend files
        'backend/template.yaml': sam_template,
        'backend/samconfig.toml': samconfig_toml,
        'backend/pytest.ini': pytest_ini,
        f'backend/src/{project_name.replace("-", "_")}/app.py': backend_app,
        f'backend/src/{project_name.replace("-", "_")}/requirements.txt': requirements,
        f'backend/src/{project_name.replace("-", "_")}/models/user.py': user_model,
        f'backend/src/{project_name.replace("-", "_")}/auth/jwt_middleware.py': jwt_middleware,
    }
    
    for file_path, content in files_to_create.items():
        full_path = dest_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
    
    # Create empty __init__.py files for Python packages
    python_dirs = [
        f'backend/src/{project_name.replace("-", "_")}',
        f'backend/src/{project_name.replace("-", "_")}/models',
        f'backend/src/{project_name.replace("-", "_")}/dal',
        f'backend/src/{project_name.replace("-", "_")}/auth',
        'backend/tests'
    ]
    
    for py_dir in python_dirs:
        init_file = dest_dir / py_dir / '__init__.py'
        init_file.touch()
    
    # Create setup instructions
    setup_guide = f'''# {project_name} - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
# Use the root package.json for convenience
npm run setup

# Or manually:
# cd frontend && npm install
# cd ../backend && pip install -r src/{project_name.replace("-", "_")}/requirements.txt
```

### 2. Development
```bash
# Frontend dev server
npm run dev:frontend

# Backend local API (in separate terminal)
npm run dev:backend

# Or manually:
# cd frontend && npm run dev
# cd backend && sam local start-api
```

### 3. Testing
```bash
# Run all tests
npm test

# Or individually:
npm run test:frontend  # Vue/Vitest tests
npm run test:backend   # Python/pytest tests
```

### 4. Deploy
```bash
# Development environment
npm run deploy:dev

# Production environment  
npm run deploy:prod

# Or manually:
# cd backend && sam deploy --config-env dev|prod
```

## Project Structure
- `package.json` - Root scripts for project management
- `frontend/` - Vue.js 3 + TypeScript application with full tooling
- `backend/` - Python Lambda functions with SAM
- Complete TypeScript, ESLint, and testing configuration
- Environment-based deployment ready

## What's Included
✅ **Frontend Tooling**: TypeScript, ESLint, Vitest, Vite  
✅ **Backend Configuration**: SAM, pytest, environment configs  
✅ **Authentication**: Cognito + JWT middleware ready  
✅ **Database**: DynamoDB tables configured  
✅ **Deployment**: Multi-environment SAM config  
✅ **Development**: Hot reload, local API, testing  

## Next Steps
1. Customize the data models in `backend/src/{project_name.replace("-", "_")}/models/`
2. Add your business logic to `backend/src/{project_name.replace("-", "_")}/app.py`
3. Create your Vue components in `frontend/src/components/`
4. Update the API service in `frontend/src/services/api.ts`
5. Configure your API URLs in `.env.development` and `.env.production`

This is a complete foundation with all tooling - focus on building your features!
'''
    
    (dest_dir / 'README.md').write_text(setup_guide, encoding='utf-8')
    
    print(f"✅ Minimal template '{project_name}' created successfully!")
    print(f"📍 Location: {dest_dir}")
    print(f"📖 Check README.md for setup instructions")
    
    return True

def main():
    if len(sys.argv) != 3:
        print("Usage: python create-minimal-template.py <project_name> <destination_path>")
        print("Example: python create-minimal-template.py my-app ../")
        sys.exit(1)
    
    project_name = sys.argv[1]
    destination_path = sys.argv[2]
    
    # Validate project name
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', project_name):
        print("Error: Project name must start with a letter and contain only letters, numbers, hyphens, and underscores")
        sys.exit(1)
    
    success = create_minimal_template(project_name, destination_path)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()