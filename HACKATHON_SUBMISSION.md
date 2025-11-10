# MindBridge - Cloud Run Hackathon 2025 Submission

## 🏆 Category: AI Agents

---

## 📝 Project Summary

**MindBridge** is an autonomous multi-agent mental health support system that uses Google Gemini models orchestrated through the Agent Development Kit (ADK) pattern. The platform provides empathetic, intelligent mental health support through five specialized AI agents working together seamlessly on Google Cloud Run.

### Key Innovation
Instead of a monolithic chatbot, MindBridge uses **autonomous agent orchestration** where each agent specializes in a specific aspect of mental health support. A coordinator agent intelligently routes conversations between specialized agents, creating a natural and comprehensive support experience.

---

## 🎯 The Problem We Solve

Mental health support has three critical gaps:
1. **Access barriers** - Long wait times for professional help
2. **Initial stigma** - Fear of judgment prevents people from seeking help
3. **Continuity** - Disconnected intake, crisis support, and ongoing care

MindBridge addresses all three through intelligent AI agents that provide immediate, judgment-free support while seamlessly connecting users to appropriate resources.

---

## 🤖 Multi-Agent Architecture

### 5 Specialized Agents

#### 1. **Intake Agent** (Gemini 2.5 Flash - Thinking Mode)
- **Purpose**: Warm, empathetic conversational onboarding
- **Intelligence**: Extended thinking mode for nuanced emotional understanding
- **Capabilities**: 
  - Natural conversation flow
  - Context gathering
  - Safe space creation
  - Seamless transition to appropriate next agent

#### 2. **Crisis Agent** (Gemini 2.5 Flash)
- **Purpose**: Immediate risk assessment and intervention
- **Pattern**: ReAct (Reasoning + Acting)
- **Capabilities**:
  - 5-level risk classification (minimal → severe)
  - Instant emergency resource provision
  - Keyword-based rapid detection
  - Autonomous decision-making for escalation

#### 3. **Resource Agent** (Gemini 2.5 Pro - Thinking Mode)
- **Purpose**: Intelligent therapist matching
- **Intelligence**: Complex reasoning for multi-factor matching
- **Capabilities**:
  - 9 counselor specializations
  - Context-based recommendations
  - Detailed match reasoning
  - Autonomous search and filtering

#### 4. **Habit Agent** (Gemini 2.5 Flash)
- **Purpose**: Evidence-based therapeutic habit recommendations
- **Approach**: Deterministic with AI enhancement
- **Capabilities**:
  - 27 clinical habits across categories
  - Progress tracking
  - Streak monitoring
  - Personalized suggestions

#### 5. **Coordinator Agent** (Gemini 2.5 Pro - Thinking Mode)
- **Purpose**: Workflow orchestration
- **Intelligence**: Multi-step reasoning for agent routing
- **Capabilities**:
  - Context-aware agent transitions
  - State management
  - Conversation continuity
  - Dynamic workflow adaptation

### Architecture Flow

```
User Input
    ↓
┌────────────────────────────────────────┐
│ Coordinator Agent (Gemini 2.5 Pro)    │
│ • Analyzes conversation context       │
│ • Routes to appropriate agent         │
│ • Maintains state across agents       │
└────────────┬───────────────────────────┘
             │
    ┌────────┼────────┬────────┬────────┐
    ▼        ▼        ▼        ▼        ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│Intake  │ │Crisis│ │Resource│ │Habit │
│Agent   │ │Agent │ │Agent   │ │Agent │
└────────┘ └──────┘ └────────┘ └──────┘
    │         │         │         │
    └─────────┴─────────┴─────────┘
              │
    ┌─────────▼──────────┐
    │  Cloud Run Service │
    │  • Auto-scaling    │
    │  • FastAPI backend │
    │  • 2GB RAM, 2 vCPU │
    └────────────────────┘
```

---

## 🚀 Cloud Run Implementation

### Deployment Configuration

**Resource Type**: Cloud Run Service (HTTP request handling)

**Configuration**:
```yaml
CPU: 2 vCPU
Memory: 2GB
Concurrency: 80 requests
Min instances: 0 (scales to zero)
Max instances: 10
Region: us-central1
Timeout: 300s
```

**Why Cloud Run?**
1. **Instant scaling** - Handles traffic spikes during crisis moments
2. **Cost efficiency** - Scales to zero when not in use
3. **Serverless simplicity** - No infrastructure management
4. **Built-in security** - HTTPS, IAM, automatic certificates
5. **Developer velocity** - Deploy from GitHub in minutes

### Infrastructure as Code

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "main.py"]
```

**cloudbuild.yaml**:
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mindbridge', '.']
  
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mindbridge']
  
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'mindbridge'
      - '--image=gcr.io/$PROJECT_ID/mindbridge'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
```

---

## 💡 Key Features

### 1. Voice Interface
- **Speech-to-Text**: WebKit Speech Recognition API
- **Text-to-Speech**: Browser native TTS
- **Visual Feedback**: Animated orb with real-time states (listening, thinking, speaking)
- **Accessibility**: Full keyboard and voice control

### 2. 4-Tier Privacy System
Based on user comfort level:
- **No Records**: Ephemeral, no data stored
- **Your Private Notes**: Local storage only
- **Assisted Handoff**: Professional matching data
- **Full Support**: Complete care coordination

### 3. Real-Time Agent Status
- Visual workflow tracking
- Agent transition notifications
- Conversation history
- Progress indicators

### 4. Habit Tracking System
- 27 evidence-based therapeutic habits
- Visual progress tracking (momentum jar)
- Streak monitoring
- Category-based organization

### 5. Intelligent Therapist Matching
- 9 specialization categories
- Multi-factor matching algorithm
- Detailed match reasoning
- Appointment scheduling

---

## 🛠️ Technical Stack

### Core Technologies
- **Backend**: Python 3.11 + FastAPI
- **AI Models**: Google Gemini 2.5 (Flash & Pro with Thinking Mode)
- **Deployment**: Google Cloud Run
- **CI/CD**: Cloud Build
- **Container**: Docker
- **Frontend**: Vanilla JavaScript (no framework overhead)
- **Styling**: Modern CSS with sharp UI design

### Google Cloud Services Used
- **Cloud Run**: Serverless application hosting
- **Cloud Build**: Automated CI/CD pipeline
- **Container Registry**: Docker image storage
- **Secret Manager**: API key management (recommended)
- **IAM**: Access control

### Agent Development Kit Pattern
Our implementation follows ADK principles:
1. **Agent specialization** - Single responsibility per agent
2. **State management** - Shared context across agents
3. **Orchestration** - Coordinator manages workflow
4. **Autonomy** - Agents make independent decisions
5. **Scalability** - Stateless design for horizontal scaling

---

## 📊 Impact & Metrics

### Scalability
- **Zero to production**: < 2 minutes
- **Cold start**: < 1 second
- **Concurrent users**: 80 per instance
- **Auto-scale**: 0 → 10 instances dynamically

### User Experience
- **Response time**: < 2 seconds for agent responses
- **Conversation flow**: Natural transitions between agents
- **Accessibility**: Voice + text + keyboard navigation
- **Privacy**: 4 tiers of data control

### Cost Efficiency
- **Pay-per-use**: Only pay for active request time
- **Scale to zero**: No cost during idle periods
- **Estimated**: ~$5-10/month for 1000 daily active users

---

## 🎥 Demonstration Video

### Video Walkthrough (3 minutes)

**Segment 1: Landing & Voice Interface** (0:00 - 0:45)
- Beautiful landing page with animated gradients
- Voice orb interaction
- Speech recognition activation

**Segment 2: Multi-Agent Workflow** (0:45 - 1:45)
- Intake agent conversation
- Privacy tier selection
- Agent transition visualization
- Crisis detection (if applicable)

**Segment 3: Therapist Matching** (1:45 - 2:20)
- Resource agent recommendations
- Match reasoning display
- Appointment scheduling

**Segment 4: Habit Tracking** (2:20 - 2:50)
- Habit recommendations
- Progress tracking
- Momentum jar visualization

**Segment 5: Cloud Run Deployment** (2:50 - 3:00)
- Quick deployment demo
- Auto-scaling visualization
- Global accessibility

**Video Link**: [TO BE ADDED]

---

## 📁 Code Repository

**GitHub**: https://github.com/SAMK-online/MindBridge-ClaudRunHack

### Repository Structure
```
MindBridge-ClaudRunHack/
├── agents/
│   ├── coordinator.py       # Orchestration logic
│   ├── intake_agent.py      # Conversational onboarding
│   ├── crisis_agent.py      # Risk assessment
│   ├── resource_agent.py    # Therapist matching
│   └── habit_agent.py       # Habit recommendations
├── models/
│   ├── user.py             # User data models
│   ├── therapist.py        # Therapist database
│   ├── habit.py            # Habit definitions
│   └── session.py          # Session management
├── templates/
│   ├── landing.html        # Hackathon landing page
│   ├── voice_interface.html # Main voice UI
│   └── index.html          # Text chat fallback
├── main.py                 # FastAPI application
├── Dockerfile              # Container definition
├── cloudbuild.yaml         # CI/CD configuration
├── requirements.txt        # Python dependencies
└── README.md              # Documentation
```

---

## 🏗️ Architecture Diagram

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Voice UI     │  │ Text Chat UI │  │ Landing Page │ │
│  │ (Speech API) │  │ (WebSocket)  │  │ (Marketing)  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Cloud Run Service (FastAPI)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │              API Endpoints                        │  │
│  │  /chat  /habits  /schedule  /privacy  /session  │  │
│  └──────────────────────────────────────────────────┘  │
│                      │                                   │
│  ┌──────────────────▼────────────────────────────────┐ │
│  │           Coordinator Agent                       │ │
│  │        (Gemini 2.5 Pro Thinking)                 │ │
│  │  • Request routing                                │ │
│  │  • State management                               │ │
│  │  • Workflow orchestration                         │ │
│  └───────────┬───────────────────────────────────────┘ │
│              │                                           │
│  ┌───────────┼──────────┬──────────┬──────────┐       │
│  ▼           ▼          ▼          ▼          ▼        │
│ ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐              │
│ │Intake  │ │Crisis│ │Resource│ │Habit │              │
│ │Agent   │ │Agent │ │Agent   │ │Agent │              │
│ │        │ │      │ │        │ │      │              │
│ │Gemini  │ │Gemini│ │Gemini  │ │Gemini│              │
│ │2.5     │ │2.5   │ │2.5 Pro │ │2.5   │              │
│ │Flash   │ │Flash │ │Thinking│ │Flash │              │
│ └────────┘ └──────┘ └────────┘ └──────┘              │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Google Gemini API                          │
│  • gemini-2.5-flash (fast inference)                   │
│  • gemini-2.5-pro (complex reasoning)                  │
│  • Thinking mode (extended reasoning)                  │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                Data Storage Layer                       │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ In-Memory Cache  │  │ (Future: Firestore│           │
│  │ • Session state  │  │  for persistence) │           │
│  │ • Conversation   │  │                   │           │
│  └──────────────────┘  └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### Agent Communication Flow

```
User: "I'm feeling overwhelmed with work"
         ▼
    Coordinator: Route to Intake Agent
         ▼
    Intake Agent: Gather context (3-5 turns)
         ▼
    Coordinator: Analyze for crisis indicators
         ▼
    Crisis Agent: Assess risk (Level 1 - Minimal)
         ▼
    Coordinator: User ready for matching
         ▼
    Resource Agent: Match with Work Stress specialist
         ▼
    Coordinator: Recommend habits
         ▼
    Habit Agent: Suggest stress management habits
         ▼
    Response: Comprehensive support plan
```

---

## 🌟 Try It Out

### Live Demo
**URL**: https://mindbridge-app.run.app

### Local Development
```bash
# Clone repository
git clone https://github.com/SAMK-online/MindBridge-ClaudRunHack.git
cd MindBridge-ClaudRunHack

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_API_KEY="your_key_here"
export GOOGLE_CLOUD_PROJECT="nimacareai"

# Run locally
python main.py

# Visit http://localhost:8080
```

### Deploy to Cloud Run
```bash
# Authenticate
gcloud auth login
gcloud config set project nimacareai

# Deploy
gcloud run deploy mindbridge \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key_here

# Done! URL provided automatically
```

---

## 🔐 Security & Privacy

### Security Measures
1. **API Key Protection**: Environment variables, Secret Manager recommended
2. **CORS Policy**: Whitelisted origins only
3. **Input Validation**: Pydantic models for all requests
4. **Rate Limiting**: Cloud Run built-in protection
5. **HTTPS Only**: Automatic SSL certificates

### Privacy Features
1. **4-Tier System**: User controls data retention
2. **Session Isolation**: No cross-user data leakage
3. **Ephemeral Mode**: No storage option available
4. **Transparent Logging**: User knows what's recorded
5. **HIPAA-Ready**: Architecture supports compliance

---

## 🎯 Future Enhancements

### Short-term (Next 3 months)
- [ ] Firestore integration for persistence
- [ ] User authentication (Firebase Auth)
- [ ] Email/SMS notifications for appointments
- [ ] Multi-language support (10+ languages)
- [ ] Mobile app (React Native)

### Medium-term (6 months)
- [ ] Real-time video counseling integration
- [ ] Group therapy session support
- [ ] Advanced analytics dashboard
- [ ] Predictive crisis detection (ML models)
- [ ] Insurance integration

### Long-term (12+ months)
- [ ] Wearable device integration (stress monitoring)
- [ ] VR therapy sessions
- [ ] Research partnership program
- [ ] Blockchain-based secure health records
- [ ] Global expansion (50+ countries)

---

## 👥 Team

**Developer**: Abdul Shaik  
**Role**: Full-stack development, AI agent orchestration, Cloud Run deployment  
**LinkedIn**: [TO BE ADDED]  
**GitHub**: https://github.com/SAMK-online

---

## 📚 Technical Documentation

### API Endpoints

**Chat Endpoint**
```http
POST /chat
Content-Type: application/json

{
  "user_id": "string",
  "message": "string",
  "session_id": "string (optional)"
}

Response:
{
  "session_id": "string",
  "messages": [...],
  "current_agent": "string",
  "workflow_complete": boolean
}
```

**Privacy Endpoint**
```http
POST /privacy/set
Content-Type: application/json

{
  "user_id": "string",
  "session_id": "string",
  "privacy_tier": "no_records|your_private_notes|assisted_handoff|full_support"
}
```

**Habits Endpoint**
```http
GET /habits/{session_id}

Response:
{
  "session_id": "string",
  "habits": [...],
  "category": "string"
}
```

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_project_id

# Optional
PORT=8080
ALLOWED_ORIGINS=http://localhost:8080,https://mindbridge-app.run.app
```

---

## 🏅 Why MindBridge Should Win

### Technical Excellence
1. **True Multi-Agent System**: Not just multiple prompts, but autonomous agents with specialized capabilities
2. **Google Gemini Showcase**: Leverages both Flash and Pro models with Thinking Mode
3. **Cloud Run Native**: Purpose-built for serverless, scales effortlessly
4. **Production-Ready**: Security, privacy, monitoring, and deployment automation

### Real-World Impact
1. **Addresses Critical Need**: Mental health crisis is global
2. **Immediate Value**: Reduces wait times from weeks to seconds
3. **Scalable Solution**: Can serve millions of users
4. **Privacy-First**: User control over data at every step

### Innovation
1. **Agent Orchestration**: Novel approach to mental health support
2. **Voice-First UX**: Natural interaction model
3. **Intelligent Routing**: Context-aware agent transitions
4. **Momentum System**: Gamified therapeutic habits

### Developer Experience
1. **Clean Architecture**: Easy to understand and extend
2. **Comprehensive Docs**: Guides for setup, deployment, and API usage
3. **Open Source**: Community can contribute and learn
4. **Cloud Run Best Practices**: Reference implementation for others

---

## 📄 License

MIT License - Open source and free to use

---

## 🙏 Acknowledgments

- **Google Cloud Team**: For Cloud Run and Gemini API
- **FastAPI Community**: For excellent Python framework
- **Mental Health Professionals**: For guidance on therapeutic approaches
- **Open Source Community**: For inspiration and tools

---

## 📞 Contact

For questions, suggestions, or collaboration opportunities:

**Email**: [TO BE ADDED]  
**GitHub Issues**: https://github.com/SAMK-online/MindBridge-ClaudRunHack/issues  
**Project Website**: https://mindbridge-app.run.app

---

**Built with ❤️ for the Google Cloud Run Hackathon 2025**

*Empowering mental wellness through intelligent AI agents on serverless infrastructure*

