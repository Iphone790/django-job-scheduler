📌 Django Background Job Scheduler:
-----------------------------------

A production-style background job scheduler built with Django that supports one-time and interval-based task execution with retry handling, state management, and safe database locking.

📌 Table of Contents:
---------------------

1: About The Project
2: Architecture Overview
3: Features
4: Built With
5: Getting Started
6: Environment Setup
7: Running the Worker
8: Job Lifecycle
9: Database Design
10: Docker Setup


📖 About The Project:
--------------------

I built a Django-based Background Job Scheduler to understand how task processing systems work internally without relying on external tools like Celery or Redis.
This project simulates a production-style background worker that continuously listens for scheduled jobs, safely executes them, and manages their lifecycle using database-driven state transitions.

The scheduler supports:
---------------------

One-time tasks
Interval-based recurring tasks
Automatic retry mechanism
Job status tracking
Crash recovery handling
Safe concurrent execution using database row locking
The worker runs in a polling loop and fetches due jobs using select_for_update(skip_locked=True) to prevent duplicate execution and ensure consistency.
Retry mechanisms
Worker architecture design

🏗 Architecture Overview
Client / Admin / API
        │
        ▼
    Job Created
 (status = SCHEDULED)
        │
        ▼
Background Worker Loop
        │
        ▼
Fetch Due Jobs (with DB locking)
        │
        ▼
Scheduled --> RUNNING --> COMPLETED / FAILED

Worker Strategy
Polling-based execution
Uses select_for_update(skip_locked=True) for safe locking
Prevents duplicate job execution
Handles crash recovery
Supports retry logic

✨ Features:
------------

✅ One-time task execution

✅ Interval-based recurring tasks

✅ Retry mechanism with max retries

✅ Automatic crash recovery

✅ Status tracking (SCHEDULED, RUNNING, COMPLETED, FAILED)

✅ Safe database row locking

✅ Docker-compatible worker

✅ Minimal logging of state transitions

🛠 Built With:
-------------

Language: Python 3.x

Framework: Django

Database: PostgreSQL

Containerization: Docker

Version Control: Git + GitHub

🚀 Getting Started
🔹 Clone Repository
git clone git@github.com:Iphone790/django-job-scheduler.git
cd django-job-scheduler
🔹 Create Virtual Environment
python -m venv venv
source venv/bin/activate
🔹 Install Dependencies
pip install -r requirements.txt
🔹 Apply Migrations
python manage.py migrate
▶ Running the Worker

Start the background worker:

python manage.py run_worker

Worker behavior:

Poll interval: 5 seconds

Batch size: 5 jobs

Executes due scheduled tasks

Handles retry logic

Updates job status

🔄 Job Lifecycle:
-----------------

🟢 One-Time Job
SCHEDULED → RUNNING → COMPLETED
Runs once and stops permanently.

🟡 Interval Job
SCHEDULED → RUNNING → SCHEDULED → RUNNING → ...
Automatically reschedules itself based on interval_seconds.

🧠 Retry Logic:
---------------

If a job fails:
retry_count increments
If retry_count < max_retries → rescheduled
Else → marked as FAILED

🗂 Database Model Overview:
--------------------------

Key fields in the Job model:
Field	Purpose
id	Unique identifier (UUID)
name	Task name
payload	JSON data
schedule_type	one_time / interval
interval_seconds	Recurring interval
max_retries	Max retry attempts
retry_count	Current retry count
status	Job state
next_run_at	Next execution time
created_at	Creation timestamp
🔒 Concurrency & Safety

The worker uses:
---------------

.select_for_update(skip_locked=True)
This ensures:
No race conditions
No duplicate execution
Safe multi-worker scaling (if expanded later)

🐳 Running with Docker:
-----------------------

Build and run:

docker-compose up --build

Worker logs will display job state transitions inside the container.

📈 Future Improvements

Add cron-based scheduling

Add pause/resume functionality

Add job cancellation

Add execution metrics tracking

Add distributed worker scaling

Integrate Redis + Celery for event-driven scheduling

Add REST API for job creation

🎯 Learning Outcomes:
--------------------

This project demonstrates understanding of:

Background worker architecture
Polling-based scheduling
State machine design
Database locking mechanisms
Retry handling
Production-style logging
Docker-based deployment

📬 Contact:
-----------

Aditya Verma
GitHub: https://github.com/Iphone790

 interviews

Tell me your goal 🚀
