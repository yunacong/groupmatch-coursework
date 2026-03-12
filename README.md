# GroupMatch – Coursework Group Matching & Project Management Platform

GroupMatch is a Django web application for university students working on group coursework.
It supports project creation, student recruitment, application approval, task management,
visible contribution tracking, and lightweight collaboration through comments.

## Stack
- Python 3 / Django 5
- Django templates + HTML/CSS
- Vanilla JavaScript + AJAX for interactive task updates
- SQLite for local coursework demo

## Setup
```bash
cd groupmatch_project
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Demo accounts
After loading sample data:
- leader / pass12345
- student / pass12345
- designer / pass12345

## Running tests
```bash
python manage.py test
```

## Key accessibility features
- Skip link and semantic landmarks
- Explicit labels and clear error states on login/project forms
- Keyboard-operable task board with visible focus outlines
- `aria-live` status region for feedback messages

## Sustainability/performance notes
The optimised version removes heavy decorative images from critical pages, keeps CSS and
JavaScript separated, uses a small custom stylesheet, and updates task status with AJAX so
the interface does not require a full page refresh for each micro-interaction.

## Repository / deployment
Add your public repository URL and deployed URL to the PDF report before submission.
