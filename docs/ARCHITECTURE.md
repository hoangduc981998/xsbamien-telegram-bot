# 🏗️ Architecture - XS Ba Miền Telegram Bot

This document describes the architecture and deployment infrastructure of the xsbamien-telegram-bot.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Deployment Architecture](#deployment-architecture)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Technology Stack](#technology-stack)
6. [Data Flow](#data-flow)

---

## Overview

The XS Ba Miền Telegram Bot is a serverless application deployed on Google Cloud Run, providing lottery results for Vietnamese users through Telegram.

### Key Characteristics:
- **Serverless**: Deployed on Google Cloud Run for automatic scaling
- **Event-driven**: Responds to Telegram updates via webhooks
- **Stateless**: No persistent state, uses external cache for temporary data
- **Containerized**: Docker-based deployment for consistency

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ User 1   │  │ User 2   │  │ User 3   │  │ User N   │       │
│  │ Telegram │  │ Telegram │  │ Telegram │  │ Telegram │       │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘       │
└────────┼─────────────┼─────────────┼─────────────┼─────────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │   Telegram Bot API        │
         │   (Telegram Servers)      │
         └─────────────┬─────────────┘
                       │ Updates
         ┌─────────────▼─────────────┐
         │                           │
┌────────┴──────────────────────────────────────────────────────┐
│                    Application Layer                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Google Cloud Run                             │ │
│  │  ┌────────────────────────────────────────────────────┐  │ │
│  │  │         xsbamien-telegram-bot                      │  │ │
│  │  │  ┌──────────────────────────────────────────────┐  │  │ │
│  │  │  │           Bot Application                     │  │  │ │
│  │  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │  │  │ │
│  │  │  │  │ Commands │  │Callbacks │  │  Errors  │   │  │  │ │
│  │  │  │  │ Handlers │  │ Handlers │  │ Handler  │   │  │  │ │
│  │  │  │  └────┬─────┘  └────┬─────┘  └────┬─────┘   │  │  │ │
│  │  │  │       │              │              │         │  │  │ │
│  │  │  │  ┌────▼──────────────▼──────────────▼─────┐  │  │  │ │
│  │  │  │  │        Business Logic Layer           │  │  │  │ │
│  │  │  │  │  ┌──────────┐      ┌──────────┐      │  │  │  │ │
│  │  │  │  │  │ Lottery  │      │  Cache   │      │  │  │  │ │
│  │  │  │  │  │ Service  │      │ Service  │      │  │  │  │ │
│  │  │  │  │  └────┬─────┘      └────┬─────┘      │  │  │  │ │
│  │  │  │  │       │                  │            │  │  │  │ │
│  │  │  │  │  ┌────▼────┐        ┌───▼────┐       │  │  │  │ │
│  │  │  │  │  │   API   │        │ Redis  │       │  │  │  │ │
│  │  │  │  │  │ Client  │        │(Future)│       │  │  │  │ │
│  │  │  │  │  └────┬────┘        └────────┘       │  │  │  │ │
│  │  │  │  └───────┼────────────────────────────┘  │  │  │ │
│  │  │  │          │                                │  │  │ │
│  │  │  │  ┌───────▼────────────────────────────┐  │  │  │ │
│  │  │  │  │       UI/UX Layer                  │  │  │  │ │
│  │  │  │  │  ┌──────────┐  ┌──────────┐       │  │  │  │ │
│  │  │  │  │  │Keyboards │  │Formatters│       │  │  │  │ │
│  │  │  │  │  └──────────┘  └──────────┘       │  │  │  │ │
│  │  │  │  └────────────────────────────────────┘  │  │  │ │
│  │  │  └──────────────────────────────────────────┘  │  │ │
│  │  └────────────────────────────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────┬───────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │                                       │
┌────────▼─────────┐                  ┌─────────▼────────┐
│  External APIs   │                  │  GCP Services    │
│  ┌─────────────┐ │                  │ ┌──────────────┐ │
│  │  MU88 API   │ │                  │ │Secret Manager│ │
│  │ Lottery Data│ │                  │ │  (Tokens)    │ │
│  └─────────────┘ │                  │ └──────────────┘ │
│                  │                  │ ┌──────────────┐ │
│                  │                  │ │Cloud Logging │ │
│                  │                  │ │              │ │
│                  │                  │ └──────────────┘ │
└──────────────────┘                  │ ┌──────────────┐ │
                                      │ │Cloud Monitor │ │
                                      │ │   (Metrics)  │ │
                                      │ └──────────────┘ │
                                      └──────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Source Code                            │  │
│  │               github.com/hoangduc981998/                  │  │
│  │              xsbamien-telegram-bot                        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼────────────────────────────────────────┘
                         │ Push to main
         ┌───────────────▼───────────────┐
         │  GitHub Actions               │
         │  ┌─────────────────────────┐  │
         │  │  CI/CD Pipeline         │  │
         │  │  1. Run Tests           │  │
         │  │  2. Build Docker Image  │  │
         │  │  3. Push to GCR         │  │
         │  │  4. Deploy to Cloud Run │  │
         │  └────────┬────────────────┘  │
         └───────────┼────────────────────┘
                     │ Deploy
         ┌───────────▼────────────────────────────────────────────┐
         │         Google Cloud Platform                          │
         │  ┌──────────────────────────────────────────────────┐ │
         │  │     Container Registry (GCR)                     │ │
         │  │  gcr.io/PROJECT_ID/xsbamien-telegram-bot        │ │
         │  └────────────────┬─────────────────────────────────┘ │
         │                   │ Pull Image                         │
         │  ┌────────────────▼─────────────────────────────────┐ │
         │  │           Cloud Run Service                      │ │
         │  │  ┌────────────────────────────────────────────┐  │ │
         │  │  │  xsbamien-telegram-bot                     │  │ │
         │  │  │  • Region: asia-southeast1                 │  │ │
         │  │  │  • Memory: 512Mi                           │  │ │
         │  │  │  • CPU: 1                                  │  │ │
         │  │  │  • Max instances: 10                       │  │ │
         │  │  │  • Port: 8080                              │  │ │
         │  │  └────────────────────────────────────────────┘  │ │
         │  └──────────────────────────────────────────────────┘ │
         │                                                        │
         │  ┌──────────────────────────────────────────────────┐ │
         │  │           Secret Manager                         │ │
         │  │  • TELEGRAM_BOT_TOKEN                           │ │
         │  └──────────────────────────────────────────────────┘ │
         │                                                        │
         │  ┌──────────────────────────────────────────────────┐ │
         │  │         Cloud Monitoring & Logging               │ │
         │  │  • Request logs                                  │ │
         │  │  • Error logs                                    │ │
         │  │  • Metrics (CPU, Memory, Latency)               │ │
         │  │  • Custom alerts                                 │ │
         │  └──────────────────────────────────────────────────┘ │
         └────────────────────────────────────────────────────────┘
```

---

## CI/CD Pipeline

### Test Workflow (Pull Requests)
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   PR Open   │────▶│  Run Tests   │────▶│   Quality   │
│             │     │  • Python    │     │   Checks    │
│             │     │    3.11, 3.12│     │  • Black    │
│             │     │  • Coverage  │     │  • Flake8   │
│             │     │    Report    │     │  • isort    │
│             │     │              │     │  • mypy     │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                         ┌───────▼──────┐
                                         │   Comment    │
                                         │   Coverage   │
                                         │   on PR      │
                                         └──────────────┘
```

### Deploy Workflow (Push to Main)
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Push to    │────▶│  Run Tests   │────▶│    Build    │
│    main     │     │  • All tests │     │   Docker    │
│             │     │  • Coverage  │     │   Image     │
│             │     │    ≥65%      │     │             │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                         ┌───────▼──────┐
                                         │   Push to    │
                                         │     GCR      │
                                         └──────┬───────┘
                                                │
                                         ┌──────▼───────┐
                                         │   Deploy to  │
                                         │  Cloud Run   │
                                         └──────┬───────┘
                                                │
                                         ┌──────▼───────┐
                                         │   Verify     │
                                         │  Deployment  │
                                         │ (Health ✓)   │
                                         └──────────────┘
```

---

## Technology Stack

### Core Technologies
- **Language**: Python 3.12
- **Framework**: python-telegram-bot 21.0
- **HTTP Client**: httpx 0.27.0
- **Data Validation**: Pydantic 2.6.0

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose (local), Cloud Run (production)
- **CI/CD**: GitHub Actions
- **Cloud Provider**: Google Cloud Platform

### Monitoring & Observability
- **Logging**: Cloud Logging
- **Metrics**: Cloud Monitoring
- **Health Checks**: Custom /health endpoints
- **Alerts**: Cloud Monitoring Alert Policies

### Development Tools
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8, isort, mypy
- **Version Control**: Git, GitHub

---

## Data Flow

### User Request Flow
```
1. User sends command (/start, /mb, etc.)
   │
   ▼
2. Telegram forwards update to bot
   │
   ▼
3. Bot receives update via Cloud Run
   │
   ▼
4. Command handler processes request
   │
   ├─▶ Check cache for data
   │   │
   │   ├─▶ Cache hit: Return cached result
   │   │
   │   └─▶ Cache miss: Fetch from API
   │       │
   │       ├─▶ Transform data
   │       │
   │       └─▶ Cache result
   │
   ▼
5. Format response with UI layer
   │
   ▼
6. Send message back to user via Telegram API
   │
   ▼
7. User receives formatted response
```

### Deployment Flow
```
1. Developer pushes code to GitHub
   │
   ▼
2. GitHub Actions triggers CI/CD pipeline
   │
   ├─▶ Run tests (must pass)
   │
   ├─▶ Build Docker image
   │
   ├─▶ Push to Google Container Registry
   │
   └─▶ Deploy to Cloud Run
       │
       ├─▶ Create new revision
       │
       ├─▶ Route traffic to new revision
       │
       └─▶ Verify health check
```

---

## Security Architecture

### Secrets Management
- **Bot Token**: Stored in GCP Secret Manager
- **API Keys**: Environment variables (if needed)
- **Service Account**: IAM-based authentication

### Network Security
- **HTTPS Only**: All communication encrypted
- **Cloud Run**: Managed infrastructure, automatic security patches
- **Container**: Non-root user, minimal base image

### Access Control
- **IAM Roles**: Principle of least privilege
- **Service Account**: Limited to required permissions only
- **Secrets**: Accessed only by authorized services

---

## Scalability

### Horizontal Scaling
- **Auto-scaling**: Cloud Run automatically scales based on traffic
- **Max Instances**: 10 (configurable)
- **Min Instances**: 0 (scale to zero when idle)

### Performance Optimization
- **Caching**: In-memory cache with TTL
- **Connection Pooling**: HTTP client reuses connections
- **Async I/O**: Non-blocking operations

### Resource Limits
- **Memory**: 512Mi per instance
- **CPU**: 1 vCPU per instance
- **Timeout**: 300s per request

---

## Monitoring & Alerting

### Key Metrics
- Request count
- Response latency
- Error rate
- CPU utilization
- Memory utilization
- Instance count

### Alerts
- High error rate (>5%)
- High latency (>2s)
- High memory usage (>80%)
- High CPU usage (>80%)
- Service down (no requests in 5 minutes)

### Logging
- Application logs
- Request/response logs
- Error logs
- Audit logs

---

## Future Enhancements

### Planned Features
- [ ] Redis integration for distributed caching
- [ ] WebSocket support for real-time updates
- [ ] PostgreSQL for persistent data
- [ ] Grafana dashboards
- [ ] Prometheus metrics
- [ ] Multi-region deployment
- [ ] A/B testing support

### Infrastructure
- [ ] Terraform for IaC
- [ ] Kubernetes migration (if needed)
- [ ] CDN for static assets
- [ ] Load balancing across regions

---

## References

- [Deployment Guide](DEPLOYMENT.md)
- [README](../README.md)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

**Last Updated**: 2025-10-15  
**Version**: 1.0.0  
**Maintained by**: @hoangduc981998
