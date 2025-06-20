# Running Log Application

A full-stack running log application built with Vue.js frontend and Python FastAPI backend, deployed on AWS.

## 🏗️ Architecture

- **Frontend**: Vue 3 + TypeScript + Vite
- **Backend**: Python FastAPI + AWS Lambda
- **Database**: DynamoDB
- **Authentication**: AWS Cognito + JWT
- **Infrastructure**: AWS SAM (Serverless Application Model)

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.13+
- AWS CLI configured
- SAM CLI installed

### Backend Development
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest  # Run tests
sam build && sam deploy  # Deploy to AWS

### Frontend Development
cd frontend
npm install
npm run dev  # Development server
npm run test:unit  # Run tests
npm run build  # Production build

## ⚙️ Configuration & Environment Setup

### Required Environment Variables

**Backend (AWS SAM deploys these automatically):**
- `COGNITO_USER_POOL_ID` - AWS Cognito User Pool ID
- `COGNITO_CLIENT_ID` - AWS Cognito App Client ID
- `DYNAMODB_TABLE_NAME` - DynamoDB table name (auto-generated)
- `AWS_REGION` - AWS region (default: us-east-1)

**Frontend:**
- API endpoints are configured in `frontend/src/services/api.ts`
- No environment files needed for local development

### AWS Configuration

**Required AWS Services:**
- AWS CLI configured with appropriate permissions
- SAM CLI installed for deployment
- DynamoDB, Cognito, Lambda, API Gateway permissions

**SAM Configuration:**
- Environment configs in `backend/samconfig.toml`
- Separate dev/prod environments supported

### Secrets Management

**⚠️ Security Notes:**
- Never commit AWS credentials to git
- JWT secrets auto-generated by Cognito
- All sensitive config handled via AWS Parameter Store/SAM

