# NimaAI - AI-Powered Mental Health Support 🧠

> **Democratizing mental health support through Google Gemini-powered multi-agent AI system**

[![Built with Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Cloud Run](https://img.shields.io/badge/Cloud-Run-4285F4?style=for-the-badge&logo=google-cloud)](https://cloud.google.com/run)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-00C853?style=for-the-badge&logo=google-cloud)](https://mindbridge-283246315055.us-central1.run.app)

**Cloud Run Hackathon Submission - AI Agents Category**

## 🌐 Live Demo

**🚀 [Try NimaAI Live](https://mindbridge-283246315055.us-central1.run.app)** - Experience the multi-agent AI system in action!

- **Landing Page**: https://mindbridge-283246315055.us-central1.run.app/
- **Voice Interface**: https://mindbridge-283246315055.us-central1.run.app/app
- **API Docs**: https://mindbridge-283246315055.us-central1.run.app/docs

---

## 🎯 Mission

Every year, millions struggle with mental health challenges but can't access professional support due to cost, availability, or stigma. **NimaAI** bridges this gap by connecting people who can't afford therapy with volunteer therapists—guided by an autonomous AI support system powered by Google Gemini.

## ✨ What Makes NimaAI Different

NimaAI demonstrates **true autonomous multi-agent AI**:

- 🤝 **Empathetic Intake** - Warm conversational onboarding that builds trust
- 🚨 **Instant Crisis Detection** - Gemini-powered reasoning detects risk indicators in real-time
- 🔍 **Intelligent Therapist Matching** - Autonomous search and matching based on specialization
- 📈 **Adaptive Habit Tracking** - Personalized therapeutic habits with progress monitoring
- 🔒 **Privacy-First Design** - User-controlled privacy tiers (No Records → Full Support)

## 🏗️ Multi-Agent Architecture

```
┌─────────────────────────────────────────────────┐
│ Coordinator Agent (Gemini 2.0 Flash Thinking)  │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┼────────┬───────────┬──────────┐
    ▼        ▼        ▼           ▼          ▼
┌──────────┐┌────────┐┌──────────┐┌────────┐
│ Intake   ││Crisis  ││Resource  ││Habit   │
│ Agent    ││Agent   ││Agent     ││Agent   │
│(Thinking)││(2.0)   ││(Thinking)││(2.0)   │
└──────────┘└────────┘└──────────┘└────────┘
```

### Agent Responsibilities

| Agent | Model | Purpose |
|-------|-------|---------|
| **Coordinator** | Gemini 2.5 Pro | Orchestrates workflow and agent coordination |
| **Intake Agent** | Gemini 2.5 Pro | Conducts empathetic, emotionally-aware conversations with deep understanding |
| **Crisis Agent** | Gemini 2.5 Flash | ReAct-based risk assessment (5 levels: NONE → IMMEDIATE) |
| **Resource Agent** | Gemini 2.5 Pro | Autonomous therapist search and intelligent matching from 20-person database |
| **Habit Agent** | Gemini 2.5 Flash | Adaptive habit recommendations and tracking |
| **Support Group Agent** | Gemini 2.5 Flash | Smart peer matching across 11 support groups |

## 🚀 Tech Stack

### AI & Models
- **Google Gemini 2.5 Pro** - Complex reasoning for coordination, intake, and therapist matching
- **Google Gemini 2.5 Flash** - Fast, efficient responses for crisis assessment, habits, and support groups
- **Multi-Agent Pattern** - 6 coordinated autonomous agents

### Backend
- **Python 3.11** - Core backend language
- **FastAPI** - High-performance async API framework
- **Pydantic** - Data validation and settings management

### Deployment
- **Google Cloud Run** - Serverless container deployment
- **Cloud Build** - Automated CI/CD pipeline
- **Docker** - Containerization

### Data & State
- **Pydantic Models** - Type-safe data validation
- **In-memory sessions** - Demo (use Firestore/Redis in production)

## 📦 Project Structure

```
NimaCare/
├── agents/              # AI agent implementations
│   ├── base_agent.py    # Base class with Gemini integration
│   ├── intake_agent.py  # Conversational intake
│   ├── crisis_agent.py  # Crisis detection (ReAct)
│   ├── resource_agent.py # Therapist matching
│   ├── habit_agent.py   # Habit tracking
│   └── coordinator.py   # Multi-agent orchestration
├── models/              # Data models (Pydantic)
│   ├── user.py
│   ├── therapist.py
│   ├── habit.py
│   └── session.py
├── main.py              # FastAPI application
├── Dockerfile          # Container definition
├── cloudbuild.yaml     # Cloud Build configuration
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.11+**
- **Google Cloud Project** with billing enabled
- **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/SAMK-online/MindBridge-ClaudRunHack.git
cd MindBridge-ClaudRunHack
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_gemini_api_key_here
# GOOGLE_CLOUD_PROJECT=your_project_id
```

5. **Run locally**
```bash
python main.py
```

The API will be available at `http://localhost:8080`

### API Endpoints

**Health Check:**
```bash
GET /
GET /health
```

**Chat with Multi-Agent System:**
```bash
POST /chat
{
  "user_id": "user_123",
  "message": "I've been feeling really anxious lately",
  "session_id": "optional_session_id"
}
```

**Get Session State:**
```bash
GET /session/{session_id}
```

## ☁️ Deploy to Cloud Run

### Option 1: Using Cloud Build (Recommended)

1. **Set up Cloud Build**
```bash
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions _GOOGLE_API_KEY="your_api_key"
```

### Option 2: Manual Deployment

1. **Build container**
```bash
docker build -t gcr.io/nimacareai/nimacare:latest .
```

2. **Push to Container Registry**
```bash
docker push gcr.io/nimacareai/nimacare:latest
```

3. **Deploy to Cloud Run**
```bash
gcloud run deploy nimacare-api \
  --image gcr.io/nimacareai/nimacare:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your_api_key"
```

## 🎨 Key Features Explained

### 1. Privacy Tiers
Users control how much AI assistance they receive:
- **No Records** - Complete anonymity
- **Your Private Notes** - User-encrypted only (default)
- **Assisted Handoff** - Platform helps transitions
- **Full Support** - Complete AI assistance

### 2. Autonomous Crisis Detection
Uses ReAct (Reason + Act) pattern:
```
THOUGHT → ACTION → OBSERVATION → DECISION
```
- Detects 5 risk levels: NONE → IMMEDIATE
- Auto-escalates to emergency resources
- Continuous monitoring during sessions

### 3. Intelligent Therapist Matching
When therapists are needed, the system:
1. Searches internal database
2. Matches based on specialization + availability
3. Can autonomously search web for new volunteers (extensible)
4. Provides personalized recommendations

### 4. Habit Tracking System
- Deterministic recommendations based on user context
- Streak tracking and progress monitoring
- Adaptive difficulty adjustment
- Integration with therapist sessions

## 📊 Demo Scenarios

### Scenario 1: Anxiety Support
```
User: "I've been feeling really anxious about work..."
→ Intake Agent: Warm conversation, gathers context
→ Crisis Agent: Assesses LOW risk level
→ Resource Agent: Matches with anxiety specialist
→ Habit Agent: Recommends breathing exercises
```

### Scenario 2: Crisis Intervention
```
User: "I can't do this anymore..."
→ Intake Agent: Detects crisis language immediately
→ Crisis Agent: IMMEDIATE risk level
→ Emergency resources surfaced (988, Crisis Text Line)
→ Expedited therapist match + continuous monitoring
```

## 🏆 Cloud Run Hackathon - AI Agents Category

### Requirements Met

✅ **Multi-Agent System**: 6 autonomous agents coordinated via Gemini
✅ **Gemini Models**: Uses both Gemini 2.5 Pro and Flash
✅ **Cloud Run Deployment**: Fully containerized, auto-scaling
✅ **Real-World Problem**: Addresses mental health accessibility crisis
✅ **Agent Communication**: Coordinator orchestrates sequential workflow

### Bonus Points

✅ **Multiple Gemini Models**: 2.5 Pro for complex reasoning, 2.5 Flash for speed
✅ **Production-Ready**: Environment configs, error handling, health checks
✅ **Scalable Architecture**: Stateless agents, container-based deployment
✅ **Voice Interface**: Natural speech-to-text and text-to-speech integration
✅ **Interactive UI**: Professional modal-based booking flow

## 🤝 Contributing

This project was built for the Google Cloud Run Hackathon. Contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- **Google Gemini** for powerful AI models
- **Cloud Run** for seamless serverless deployment
- **FastAPI** for excellent developer experience
- **Mental health advocates** fighting to make support accessible to all

---

**Built with ❤️ for the Cloud Run Hackathon**

🔗 **Links:**
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

*Making mental health support accessible, one conversation at a time.*
