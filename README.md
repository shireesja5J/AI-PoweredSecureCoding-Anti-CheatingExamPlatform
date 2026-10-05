# AI Secure Coding Exam Platform with Anti-Cheating OS Features

A production-ready, full-stack coding exam platform that combines secure browser-based proctoring, AI-powered behavioral analysis, and real-time code evaluation.

## 🎯 Overview

This platform provides:
- **Secure Exam Mode**: Full-screen lock with tab/window switching detection
- **AI Proctoring**: Real-time face detection, eye tracking, and risk scoring
- **Code Execution**: Java compilation and test case validation
- **Anti-Cheating**: Process monitoring, plagiarism detection, violation tracking
- **AI Feedback**: LLM-powered code optimization suggestions

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│  Java Backend    │◀────│  Python AI      │
│  (HTML/CSS/JS)  │     │  (Spring Boot)   │     │  (FastAPI)      │
│                 │◀────│                  │────▶│                 │
│ - Monaco Editor │     │ - REST APIs      │     │ - Face Detect   │
│ - Secure Mode   │     │ - Code Execution │     │ - Eye Tracking  │
│ - Timer         │     │ - Process Monitor│     │ - Risk Score    │
└─────────────────┘     │ - Report Gen     │     └─────────────────┘
                        └──────────────────┘
```

## 📁 Project Structure

```
ai-exam-platform/
├── backend-java/
│   ├── src/main/java/com/examplatform/
│   │   ├── controller/     # REST API controllers
│   │   ├── service/        # Business logic
│   │   ├── repository/    # Data access
│   │   ├── model/         # Entity classes
│   │   ├── security/       # JWT authentication
│   │   ├── monitoring/     # Process monitoring
│   │   ├── plagiarism/    # Plagiarism detection
│   │   ├── report/        # Report generation
│   │   └── ai/           # AI feedback integration
│   ├── src/main/resources/
│   │   └── application.properties
│   └── pom.xml
├── ai-service-python/
│   ├── app.py             # FastAPI application
│   ├── face_detection.py  # Face detection module
│   ├── eye_tracking.py    # Eye tracking module
│   ├── risk_engine.py     # Risk scoring engine
│   └── requirements.txt
├── frontend/
│   ├── login.html
│   ├── dashboard.html
│   ├── exam.html
│   ├── css/styles.css
│   └── js/
│       ├── auth.js
│       ├── dashboard.js
│       └── exam.js
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Java 17** or higher
- **Maven 3.8+**
- **Python 3.9+**
- **Node.js** (optional, for serving frontend)
- **Webcam** (for AI proctoring)

### 1. Start the Java Backend

```bash
cd backend-java

# Build the project
mvn clean install

# Initialize default users (candidate/password, admin/admin123)
curl -X POST http://localhost:8080/api/auth/init

# Run the application
mvn spring-boot:run
```

The Java backend will start on **port 8080**.

### 2. Start the Python AI Service

```bash
cd ai-service-python

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the AI service
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The AI service will start on **port 8000**.

### 3. Serve the Frontend

```bash
cd frontend

# Using Python's built-in server
python -m http.server 3000

# Or using Node.js http-server
npx http-server -p 3000
```

The frontend will be available at **http://localhost:3000**

## 🔧 Configuration

### Java Backend (application.properties)

```properties
# Server
server.port=8080

# JWT Secret (change in production!)
jwt.secret=your-secure-secret-key

# Database (H2 for development)
spring.datasource.url=jdbc:h2:file:./data/examdb

# LLM Integration (optional)
llm.api.url=https://api.openai.com/v1/chat/completions
llm.api.key=your-api-key
```

### Python AI Service

No configuration needed - uses default MediaPipe models.

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/init` - Initialize default users

### Exam
- `POST /api/exam/start` - Start exam session
- `GET /api/exam/questions` - Get coding questions
- `POST /api/exam/execute` - Execute Java code
- `POST /api/exam/violation` - Record security violation
- `POST /api/exam/submit` - Submit exam

### Monitoring
- `GET /api/monitoring/processes` - Check for suspicious processes
- `GET /api/monitoring/health` - Health check

### Reports
- `GET /api/reports/{sessionId}` - Get exam report (JSON)
- `GET /api/reports/{sessionId}/pdf` - Download PDF report

### AI Proctoring
- `POST /detect-face` - Detect faces in frame
- `POST /detect-multiple-faces` - Check for multiple faces
- `POST /eye-tracking` - Track eye gaze
- `POST /risk-score` - Calculate risk score
- `POST /analyze-frame` - Complete frame analysis

## 🔐 Security Features

### Browser-Level Security
- Full-screen mode enforcement
- Tab switching detection
- Window blur detection
- Keyboard shortcut blocking (F12, Ctrl+Shift+I, etc.)
- Right-click prevention
- Screenshot detection (PrintScreen key)

### AI Proctoring
- **Face Detection**: Real-time face presence validation
- **Multiple Face Detection**: Identifies if multiple people are present
- **Eye Tracking**: Detects looking away from screen
- **Head Pose Estimation**: Monitors head movement patterns
- **Risk Scoring**: Continuous 0-100 risk assessment

### System-Level Monitoring
- Suspicious process detection (TeamViewer, AnyDesk, Discord, etc.)
- Screen recording tool detection
- VM/container detection
- Browser instance monitoring

### Code Integrity
- Plagiarism detection using multiple algorithms
- Code similarity checking
- Token-based comparison
- Structure analysis

## 🎯 Exam Flow

1. **Login**: User authenticates with JWT
2. **Dashboard**: View exam instructions and start button
3. **Exam Mode**: 
   - Full-screen prompt with camera permission
   - Timer starts (30 minutes)
   - AI proctoring begins
   - Code editor (Monaco) loads
4. **During Exam**:
   - Write and run code
   - AI proctoring monitors continuously
   - Violations are logged automatically
5. **Submission**:
   - Manual submit or auto-submit on timeout/violations
   - Report generated with AI feedback

## 📝 Sample Questions Included

1. **Two Sum** (Medium)
   - Hash map optimization
   - O(n) time complexity

2. **Reverse Linked List** (Medium)
   - Pointer manipulation
   - Iterative/recursive approaches

## 📊 Cheating Detection

### Violation Severity Levels
- **CRITICAL** (30 points): Multiple faces, fullscreen exit, DevTools
- **HIGH** (15 points): Tab switch, face not detected, suspicious process
- **MEDIUM** (8 points): Looking away, window blur
- **LOW** (3 points): Minor anomalies

### Auto-Submit Triggers
- 3+ Critical violations
- Risk score >= 85
- Timer expiration

## 📄 Report Generation

Each exam generates:
- **Overall Score**: Percentage based on test cases
- **Test Case Results**: Pass/fail for each case
- **Time Taken**: Actual vs. allotted time
- **Risk Score**: 0-100 based on violations
- **Security Log**: All recorded violations with timestamps
- **AI Feedback**: Code optimization suggestions
- **Plagiarism Score**: Similarity percentage

## 🧪 Testing

### Test Users
- **Candidate**: `candidate` / `password`
- **Admin**: `admin` / `admin123`

### API Testing
```bash
# Login
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"candidate","password":"password"}'

# Check AI service health
curl http://localhost:8000/health
```

## 🛠️ Development

### Adding New Questions

Edit `QuestionService.java`:
```java
CodingQuestion.builder()
    .id(3L)
    .title("New Problem")
    .difficulty("Hard")
    .description("Problem description...")
    .starterCode("public class Solution {...}")
    .testCases(Arrays.asList(...))
    .build()
```

### Customizing AI Feedback

Configure LLM in `application.properties`:
```properties
llm.api.url=https://api.openai.com/v1/chat/completions
llm.api.key=sk-...
```

Without LLM, the system uses rule-based feedback.

### Extending Process Monitoring

Edit `ProcessMonitoringService.java`:
```java
private static final Set<String> SUSPICIOUS_PROCESSES = Set.of(
    "your-app",
    // ... existing apps
);
```

## 📦 Building for Production

### Java Backend
```bash
cd backend-java
mvn clean package
java -jar target/ai-exam-platform-1.0.0.jar
```

### Python AI Service
```bash
cd ai-service-python
pip install -r requirements.txt
python app.py
```

## 🔒 Security Considerations

1. **Change JWT Secret**: Update in `application.properties`
2. **Use HTTPS**: Enable SSL in production
3. **Database**: Switch from H2 to PostgreSQL/MySQL
4. **File Uploads**: Validate and sanitize if adding file uploads
5. **Rate Limiting**: Implement for API endpoints

## 🐛 Troubleshooting

### Java Backend Won't Start
- Check Java version: `java -version` (should be 17+)
- Check port 8080 is free
- Review logs in `logs/` directory

### AI Service Won't Start
- Ensure Python 3.9+ installed
- Check MediaPipe installation: `pip install mediapipe`
- Verify port 8000 is free

### Camera Not Working
- Grant browser camera permissions
- Check webcam is not in use by another app
- Try restarting the AI service

### Process Monitoring Not Working (Linux/Mac)
- Ensure `ps` command available
- Run with appropriate permissions

## 📜 License

MIT License - See LICENSE file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues and feature requests, please create a GitHub issue.

---

**Built with**: Java 17, Spring Boot 3, Python 3.9, FastAPI, OpenCV, MediaPipe, Monaco Editor
