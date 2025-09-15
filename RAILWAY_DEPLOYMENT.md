# 🚂 BharatLawAI Railway Deployment Guide

## Overview
This guide covers deploying the BharatLawAI backend to Railway with optimized Docker configuration.

## 📋 Prerequisites
- Railway account
- PostgreSQL database on Railway
- Pinecone account with vector database
- Voyage AI API key
- OpenRouter API key

## 🐳 Docker Optimizations

### Key Improvements Made:
1. **Multi-stage build** for smaller image size
2. **Railway-specific environment variables** (`PORT`, etc.)
3. **Optimized health checks** with proper Railway endpoints
4. **Non-root user** for security
5. **Proper file structure** for Railway deployment
6. **Connection pooling** for database efficiency

### Build Optimizations:
- `.dockerignore` excludes unnecessary files
- Virtual environment for dependency isolation
- Minimal runtime dependencies
- Railway-specific startup commands

## 🚀 Deployment Steps

### 1. Environment Variables Setup
Set these in Railway dashboard:

```bash
# Database
DATABASE_URL=postgresql://...

# Security (Required)
SECRET_KEY=your-secure-secret-key

# AI Services
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=bharatlaw-index
VOYAGE_API_KEY=...
OPENROUTER_API_KEY=...

# OAuth (Required for Railway)
OAUTH_REDIRECT_URI=https://your-railway-app.com

# Frontend
FRONTEND_URL=https://your-vercel-app.vercel.app
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:5173

# Optional
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
```

### 2. Railway Configuration
The `railway.toml` file configures:
- Dockerfile builder
- Health check settings
- Restart policies
- Environment-specific variables

### 3. Deploy to Railway
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the Dockerfile
3. Set environment variables in Railway dashboard
4. Deploy!

## 🔍 Health Checks

### Endpoints:
- `/health` - Railway health check (lightweight)
- `/` - Full application health with RAG status

### Health Check Configuration:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 60 seconds
- **Retries**: 3

## 📊 Performance Optimizations

### Database:
- Connection pooling with 10 connections
- 20 max overflow connections
- 30-second timeout
- 1-hour connection recycle

### Application:
- Single worker (Railway optimized)
- uvloop for async performance
- Gzip compression
- Proper CORS configuration

## 🛡️ Security Features

### Railway-Specific:
- Non-root user execution
- Minimal attack surface
- Environment variable isolation
- Secure health check endpoints

### Application Security:
- JWT token authentication
- OAuth integration
- Password hashing with bcrypt
- SQL injection prevention
- XSS protection headers

## 📁 File Structure

```
/app/
├── langchain_rag_engine/     # Main application
├── data/                     # Legal documents
├── uploads/                  # User uploads
├── logs/                     # Application logs
└── .env                      # Environment variables
```

## 🔧 Troubleshooting

### Common Issues:

1. **Port Issues**:
   - Railway uses `PORT` environment variable
   - Default fallback is 8000

2. **Database Connection**:
   - Ensure `DATABASE_URL` is correct
   - Check Railway database credentials

3. **Health Check Failures**:
   - Check `/health` endpoint manually
   - Verify database connectivity
   - Check application logs

4. **Memory Issues**:
   - Railway has memory limits
   - Monitor with Railway metrics
   - Consider Railway Volumes for large data

### Logs:
```bash
# View Railway logs
railway logs

# View specific service logs
railway logs --service your-service-name
```

## 📈 Monitoring

### Railway Dashboard:
- CPU and memory usage
- Request/response metrics
- Error rates
- Health check status

### Application Metrics:
- Database connection status
- RAG system health
- API response times
- Error logging

## 🚀 Scaling Considerations

### Railway Plans:
- **Hobby**: 1 CPU, 1GB RAM
- **Pro**: 2-8 CPUs, 2-32GB RAM
- **Team**: Custom configurations

### Optimization Tips:
1. Use Railway Volumes for large datasets
2. Implement caching for frequent queries
3. Monitor memory usage
4. Use connection pooling
5. Optimize database queries

## 🔗 Integration Points

### Frontend (Vercel):
- CORS configured for Vercel domain
- OAuth redirect handling
- API endpoint communication

### External Services:
- **Pinecone**: Vector database
- **Voyage AI**: Embeddings
- **OpenRouter**: LLM API
- **Railway Postgres**: Database

## 📝 Environment-Specific Configurations

### Production:
```toml
[environments.production.variables]
ENVIRONMENT = "production"
LOG_LEVEL = "INFO"
```

### Staging:
```toml
[environments.staging.variables]
ENVIRONMENT = "staging"
LOG_LEVEL = "DEBUG"
```

## 🎯 Success Metrics

After deployment, monitor:
- ✅ Application starts successfully
- ✅ Health checks pass
- ✅ Database connections work
- ✅ RAG system initializes
- ✅ API endpoints respond
- ✅ OAuth flows work
- ✅ File uploads function
- ✅ Logging works properly

## 📞 Support

For Railway-specific issues:
- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Status Page: https://railway.app/status

For application issues:
- Check Railway logs
- Verify environment variables
- Test API endpoints manually
- Review application error logs