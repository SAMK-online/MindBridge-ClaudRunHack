# MindBridge - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Prerequisites
- Python 3.11+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))
- Modern browser with microphone support

---

## 📦 Installation

### 1. Clone & Setup
```bash
git clone https://github.com/SAMK-online/MindBridge-ClaudRunHack.git
cd MindBridge-ClaudRunHack
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Run Locally
```bash
python main.py
```

Visit: **http://localhost:8080**

---

## 🎤 Using the Voice Interface

### First Time Setup:
1. **Allow Microphone Access** when prompted by your browser
2. You'll see the beautiful voice orb interface
3. Tap the orb or microphone button to start talking

### Features:
- **🎙️ Voice Input** - Tap orb to speak, it transcribes your words
- **🔊 Voice Output** - Nima speaks responses aloud
- **💬 Text Fallback** - Typed messages appear below the orb
- **📊 Habit Tracking** - Switch to "Habit Tracker" tab after completing conversation
- **🔒 Privacy Control** - Click privacy button to choose your data level

---

## 🧠 Conversation Flow

### What to Expect:

**1. Intake (Warm Welcome)**
- Nima greets you warmly
- Asks how you're feeling
- Listens without judgment
- Takes 3-4 exchanges

**2. Crisis Assessment**
- Evaluates if you need urgent help
- Suggests counselor category (e.g., Career, Anxiety)
- Shows privacy selection modal

**3. Therapist Matching**
- Presents matched counselors
- Shows specializations and experience
- You can choose or override category

**4. Habit Recommendations**
- Gets 3 evidence-based habits
- Tailored to your selected category
- Available in Habit Tracker tab

---

## 🎯 Try These Example Conversations

### Career Burnout:
```
You: "I've been feeling really burned out at work. I love what I do, 
but I'm questioning if this is the right path for me."

Nima: [Empathetic response, asks follow-ups]

[After 3-4 exchanges]
→ Suggests Career Counselor
→ Matches you with career specialist
→ Recommends work-life balance habits
```

### Anxiety:
```
You: "I've been having panic attacks lately and I don't know why."

Nima: [Supportive response, explores triggers]

→ Suggests Anxiety Specialist
→ Recommends breathing exercises
→ Tracks your daily progress
```

---

## 📊 Habit Tracker

After completing your conversation:

1. Click **"Habit Tracker"** tab at the top
2. See your personalized habits
3. Check off completed habits each day
4. Track your streak progress
5. View momentum jar with your current streak

**Habit Categories Available:**
- Depression, Anxiety, Career, Marriage
- ADHD, Trauma, Addiction, Grief, General

---

## 🔐 Privacy Tiers

Choose your comfort level:

### 🌟 Full Support (Most Features)
- AI tracks your progress
- Helps with therapist handoffs
- Keeps helpful notes

### 🤝 Assisted Handoff
- Helps connect you to therapist
- Smooth transitions
- Basic note keeping

### 📝 Your Private Notes (Default)
- High-level tracking only
- You control the details
- Balanced privacy

### 🔒 No Records (Maximum Privacy)
- Nothing saved
- Complete anonymity
- Just this conversation

---

## 🌐 API Access

### Chat Endpoint
```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "I need help with anxiety",
    "session_id": null
  }'
```

### Get Habits
```bash
curl http://localhost:8080/habits/session_abc123
```

### Complete Habit
```bash
curl -X POST http://localhost:8080/habits/complete \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_abc123",
    "habit_id": "anx_001",
    "completed": true
  }'
```

---

## 🐳 Docker Deployment

### Build & Run
```bash
docker build -t mindbridge:latest .
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY=your_key_here \
  mindbridge:latest
```

---

## ☁️ Cloud Run Deployment

### Deploy to Google Cloud Run
```bash
gcloud builds submit --config cloudbuild.yaml

# Or manually:
gcloud run deploy mindbridge \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

---

## 🔧 Troubleshooting

### Voice Not Working?
- **Check browser:** Use Chrome, Edge, or Safari
- **Check permissions:** Allow microphone access
- **Check HTTPS:** Voice requires HTTPS in production

### No Habits Showing?
- **Complete conversation first:** Habits appear after full intake → crisis → resource flow
- **Check tab:** Click "Habit Tracker" tab at top
- **Refresh:** Try refreshing the page

### API Errors?
- **Check API key:** Verify `GOOGLE_API_KEY` in .env
- **Check quota:** Ensure Gemini API quota not exceeded
- **Check logs:** View terminal for detailed errors

---

## 📚 Documentation

- **Full Features:** See `FEATURE_IMPLEMENTATION.md`
- **Architecture:** See `README.md`
- **Habits:** See `HABIT_AGENT_IMPLEMENTATION.md`

---

## 💡 Tips

1. **Speak naturally** - Nima understands conversational language
2. **Take your time** - No rush, 3-4 exchanges for intake
3. **Be honest** - More details = better therapist match
4. **Check habits daily** - Build consistency for best results
5. **Change privacy anytime** - Settings are flexible

---

## 🆘 Emergency Resources

**If you're in crisis:**
- 🚨 Call **988** (Suicide & Crisis Lifeline)
- 💬 Text **"HELLO" to 741741** (Crisis Text Line)
- 📞 Call **911** if in immediate danger

**Nima will always provide these resources if needed.**

---

## 🎉 What's Next?

After your first conversation:
1. ✅ View your matched counselors
2. ✅ Review your personalized habits
3. ✅ Set your privacy preference
4. ✅ Start tracking daily progress

**You're on your way to better mental wellness! 💙**

---

Built with ❤️ using Google Gemini  
Questions? Open an issue on GitHub

