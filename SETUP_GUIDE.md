# NimaCare - Complete Setup Guide

This guide will help you recreate the entire NimaCare project on your local machine.

## Project Structure

```
MindBridge-ClaudRunHack/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── intake_agent.py
│   ├── crisis_agent.py
│   ├── resource_agent.py
│   ├── habit_agent.py
│   └── coordinator.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── therapist.py
│   ├── habit.py
│   └── session.py
├── templates/
│   └── index.html
├── .env
├── .env.example
├── .gitignore
├── .dockerignore
├── requirements.txt
├── main.py
├── Dockerfile
├── cloudbuild.yaml
└── README.md
```

## Step 1: Create the Project on Your Laptop

```bash
# On your laptop
mkdir MindBridge-ClaudRunHack
cd MindBridge-ClaudRunHack

# Initialize git
git init
git remote add origin https://github.com/SAMK-online/MindBridge-ClaudRunHack.git
```

## Step 2: Copy All Files

I'll provide each file below. Create them on your laptop in the structure shown above.

## Step 3: Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 4: Configure Environment

Create `.env` file with your API key:
```
GOOGLE_CLOUD_PROJECT=nimacareai
GOOGLE_CLOUD_PROJECT_NUMBER=283246315055
GOOGLE_API_KEY=your_working_api_key_here
```

## Step 5: Test Locally

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

Open http://localhost:8080

## Step 6: Push to GitHub

```bash
git add .
git commit -m "Initial NimaCare implementation with Gemini 2.5 multi-agent system"
git push -u origin main
```

---

**Continue reading below for the complete file contents...**
