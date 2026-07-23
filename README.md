# E-Rakshak

E-Rakshak is an enterprise-grade public safety, incident response management, and analysis platform designed for communities, dispatchers, field officers, and administrators. 

This repository houses the blueprint and codebase for the E-Rakshak system, built using a clean layered architecture with a modern, secure technology stack.

## Technical Documents

The repository contains three foundational design artifacts:

1. 📖 **[E-Rakshak V1.0 Architecture Blueprint](file:///C:/Users/DELL/.gemini/antigravity-ide/brain/6cdc0b42-77e7-432d-a947-e2ec2e11c5ea/e_rakshak_architecture_blueprint.md)**: Details full system databases, API specifications, and background worker logic.
2. 🛠️ **[E-Rakshak Development & Coding Standards Handbook](file:///C:/Users/DELL/.gemini/antigravity-ide/brain/6cdc0b42-77e7-432d-a947-e2ec2e11c5ea/e_rakshak_development_handbook.md)**: Defines folder responsibilities, naming rules, configurations, data science layouts, and testing structures.
3. 🗄️ **[E-Rakshak Database & Schema Blueprint](file:///C:/Users/DELL/.gemini/antigravity-ide/brain/6cdc0b42-77e7-432d-a947-e2ec2e11c5ea/e_rakshak_database_architecture.md)**: Outlines details on 3NF schema tables, attributes, constraints, index mapping, and SQLAlchemy relations.

## Technology Stack

- **Backend**: Python 3.13+, Flask, Flask Blueprints, Gunicorn
- **REST API**: JSON, OpenAPI, Swagger
- **Database**: PostgreSQL, SQLAlchemy 2.x, Alembic
- **Authentication**: JWT (JSON Web Tokens), Bcrypt hashing, Role-Based Access Control (RBAC)
- **Validation**: Marshmallow
- **Background Tasks**: Celery, Redis Broker
- **Data Science**: Pandas, NumPy, SciPy, Scikit-Learn, Plotly, Matplotlib
- **Frontend**: React, Vite, Tailwind CSS, Axios, React Router

## Core Directories (To Be Generated)

- `backend/`: Flask controllers, service layer, repository database layer, marshmallow schemas, and scikit-learn analytics.
- `frontend/`: React components, views, context controllers, and visual plotting widgets.
- `docs/`: API specifications (OpenAPI) and design diagrams.
- `scripts/`: Seeding and deployment helper scripts.

---
*Created by the Chief System Architect.*
