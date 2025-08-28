# Running Log Template

This project serves as a template for creating new full-stack serverless applications with Vue.js frontend and Python Lambda backend.

## Template Features

- **Frontend**: Vue.js 3 + TypeScript + Vite + Pinia
- **Backend**: Python 3.13 Lambda functions with SAM
- **Database**: DynamoDB with proper indexing
- **Authentication**: AWS Cognito with JWT middleware
- **Testing**: Comprehensive test suites (vitest + pytest)
- **CI/CD Ready**: Structured for deployment pipelines

## Creating a New Project

Use the included template generator script:

```bash
python create-template.py <project-name> <destination-path>
```

**Example:**
```bash
# Create a new project called "expense-tracker" in the parent directory
python create-template.py expense-tracker ../

# Create a new project called "task-manager" in a specific directory
python create-template.py task-manager /path/to/projects/
```

## What Gets Replaced

The script automatically replaces:

- **Project names**: `running-log` → `your-project-name`
- **Entity names**: `runs`/`Runs` → `items`/`Items` (generic entities)
- **Activity context**: `running` → `tracking` (generic activity)
- **File/folder names**: Renames directories and files as needed

## Post-Generation Steps

After creating your new project:

1. **Review the `CUSTOMIZATION_GUIDE.md`** in your new project
2. **Install dependencies**:
   ```bash
   cd your-project-name/frontend && npm install
   cd ../backend && pip install -r requirements.txt
   ```
3. **Customize the data model** in `backend/src/items/models/`
4. **Update the frontend components** to match your domain
5. **Modify the DynamoDB schema** in `backend/template.yaml`
6. **Run tests** to ensure everything works: `npm run test:unit` and `pytest`

## Template Structure

```
running-log/
├── frontend/               # Vue.js application
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── services/       # API and auth services
│   │   ├── stores/         # Pinia stores
│   │   └── router/         # Vue Router setup
│   └── package.json
├── backend/                # Python Lambda backend
│   ├── src/runs/          # Main application code
│   │   ├── models/        # Data models
│   │   ├── dal/           # Data Access Layer
│   │   └── auth/          # Authentication middleware
│   ├── template.yaml      # SAM CloudFormation template
│   └── tests/             # Backend tests
├── helpers/               # Utility scripts
└── create-template.py     # Template generator script
```

## Template Benefits

- **Proven Architecture**: Based on a working MVP
- **Best Practices**: Follows modern development patterns
- **Full Authentication**: Complete Cognito setup with JWT
- **Comprehensive Testing**: Both frontend and backend tests
- **Mobile Ready**: Responsive design with bottom navigation
- **Serverless**: Cost-effective and scalable AWS deployment

## Customization Examples

**For an expense tracker:**
- `runs` → `expenses`
- `run_date` → `expense_date`
- `duration_seconds` → `amount`

**For a task manager:**
- `runs` → `tasks`
- `run_date` → `due_date`
- `duration_seconds` → `priority_level`

The template generator handles most of these replacements automatically, then you can fine-tune as needed.

## Contributing to Template

When making improvements to this template:

1. Keep code generic and reusable
2. Use clear, descriptive variable names
3. Maintain comprehensive tests
4. Update this README with any new features
5. Test the template generation process

## License

This template is provided as-is for creating new projects. Customize and use freely for your applications.