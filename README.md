# LedgerGuard-TransactSure

> Automated Data Quality Controls for Fintech & Banking Operations

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Overview

LedgerGuard-TransactSure is a data quality automation platform designed for Fintech and Banking domains. It detects anomalies, inconsistencies, and business rule violations across financial datasets using SQL-based quality controls exposed through a REST API.

The core value is not the API itself — it is the **10 SQL data quality controls** that demonstrate senior-level expertise in referential integrity, range validation, deduplication, reconciliation, and domain-specific business logic.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Data Generation | Faker |
| Configuration | python-dotenv |

---

## Project Roadmap

### ✅ Sprint 1 — Infrastructure & Data (In Progress)
- PostgreSQL database setup with dedicated user and permissions
- SQLAlchemy connection layer with environment-based configuration
- Data models: `customers`, `accounts`, `transactions`, `policies`, `claims`
- 100K realistic records generated with Faker

### ⏳ Sprint 2 — SQL Intelligence
- 10 SQL data quality controls covering:
  - Referential integrity violations
  - Balance reconciliation
  - Duplicate transaction detection
  - Out-of-range value validation
  - Business rule enforcement (CTEs, Window Functions)

### ⏳ Sprint 3 — API Exposure
- REST API with FastAPI to execute controls in real time
- JSON responses with violation counts and affected records
- Endpoint documentation via Swagger UI

### ⏳ Sprint 4 — Cloud & Audit
- Log storage in AWS S3 using Boto3
- Audit trail for every control execution

---

## Project Structure
```
LedgerGuard-TransactSure/
├── app/
│   ├── database.py          # SQLAlchemy engine and session factory
│   ├── models.py            # Database table definitions
│   ├── main.py              # FastAPI application entry point
│   ├── transactions/        # Transaction domain logic
│   └── insurance/           # Insurance domain logic
├── data/
│   └── seed_data.py         # 100K record generation with Faker
├── sql_validations/         # SQL quality control scripts
├── .env                     # Environment variables (not committed)
├── requirements.txt         # Pinned dependencies
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.14+
- PostgreSQL 16
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/LeoQuintero/LedgerGuard-TransactSure.git
cd LedgerGuard-TransactSure

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### Environment Variables
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ledgerguard
DB_USER=your_user
DB_PASSWORD=your_password
```

---

## Future Improvements

- **Observability:** Integration with Datadog or OpenTelemetry for real-time log monitoring and alerting on quality control failures
- **Scheduling:** Automated control execution with Apache Airflow or cron-based triggers
- **Dashboard:** Visual reporting layer for quality control results over time

---

## License

MIT License — see [LICENSE](LICENSE) for details.
