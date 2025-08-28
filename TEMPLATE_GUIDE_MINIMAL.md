# Minimal Template Generator

This approach creates a **clean foundation** with only the essential framework files, excluding all app-specific content.

## Two Template Options

### 1. Full Template (`create-template.py`)
- Copies everything and replaces running-specific terms
- Includes all your custom components and business logic
- Good for similar domain applications

### 2. Minimal Template (`create-minimal-template.py`) ⭐
- Creates only foundational framework files
- No app-specific components or business logic
- Clean slate for any type of application

## Minimal Template Contents

### What's Included (Foundation Only)
```
project-name/
├── package.json              # Root-level project scripts
├── README.md                 # Complete setup instructions
├── frontend/
│   ├── package.json          # Vue.js dependencies & scripts
│   ├── vite.config.ts        # Vite build configuration
│   ├── vitest.config.ts      # Vitest test configuration
│   ├── eslint.config.ts      # ESLint flat configuration
│   ├── tsconfig.json         # TypeScript project references
│   ├── tsconfig.app.json     # App-specific TypeScript config
│   ├── tsconfig.node.json    # Node tools TypeScript config
│   ├── tsconfig.vitest.json  # Test TypeScript config
│   ├── env.d.ts              # Environment type definitions
│   ├── .env.development      # Development environment vars
│   ├── .env.production       # Production environment vars
│   ├── index.html            # Basic HTML shell
│   └── src/
│       ├── main.ts           # Vue app initialization
│       ├── App.vue           # Root component (minimal)
│       ├── components/
│       │   └── HomePage.vue  # Basic welcome page
│       ├── router/
│       │   └── index.ts      # Vue Router setup
│       └── services/
│           └── api.ts        # Axios API client with auth
├── backend/
│   ├── template.yaml         # SAM CloudFormation (generic tables)
│   ├── samconfig.toml        # Multi-environment SAM deployment
│   ├── pytest.ini           # Python testing configuration
│   └── src/project-name/
│       ├── app.py            # Basic Lambda handler
│       ├── requirements.txt  # Python dependencies
│       ├── models/
│       │   └── user.py       # Generic user model
│       └── auth/
│           └── jwt_middleware.py  # JWT auth utilities
```

### What's NOT Included (App-Specific)
- Running-specific components (RunCalendar, ActivityPage, etc.)
- Business logic (progress calculations, metrics, etc.)
- Custom styling and branding
- Domain models (runs, targets, etc.)
- Test suites (you write your own)
- Helper scripts and data generators

## Usage

```bash
# Create a minimal foundation
python create-minimal-template.py expense-tracker ../

# Results in a clean project with:
# - Working authentication setup
# - Basic Vue.js + TypeScript structure
# - Lambda + DynamoDB foundation
# - No business logic to remove
```

## Benefits of Minimal Approach

1. **Clean Start**: No app-specific code to remove or modify
2. **Any Domain**: Works for any type of application
3. **Faster Setup**: Less code to understand and customize
4. **Best Practices**: Includes proven patterns without implementation details
5. **Complete Foundation**: Authentication, database, and deployment ready

## After Generation

Your minimal project includes:
- ✅ **Complete Frontend Tooling**: Vue.js 3 + TypeScript + Vite + ESLint + Vitest
- ✅ **Full TypeScript Configuration**: 4 tsconfig files for proper builds/testing
- ✅ **Environment Management**: Development and production .env files
- ✅ **AWS Lambda + SAM**: Multi-environment deployment configuration
- ✅ **Cognito Authentication**: Framework with JWT middleware ready
- ✅ **DynamoDB Tables**: Generic Items and Users tables configured
- ✅ **Testing Setup**: Vitest for frontend, pytest for backend
- ✅ **Root Scripts**: Convenient npm commands for the entire project
- ✅ **CORS and API**: Complete API setup with auth interceptors

You add:
- Your domain models and business logic
- Custom Vue components
- API endpoints for your data
- Tests for your specific features
- Styling and branding

## Comparison

| Feature | Full Template | Minimal Template |
|---------|---------------|------------------|
| Setup Time | Fast (copy & modify) | Very Fast (build from scratch) |
| Code Cleanup | Significant | None needed |
| Domain Flexibility | Limited to similar apps | Any application type |
| Learning Curve | Higher (understand existing code) | Lower (start fresh) |
| Best For | Running/fitness apps | Any serverless app |

The minimal template gives you a **proven architecture foundation** without the overhead of removing or understanding app-specific code.