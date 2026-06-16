# 🎓 Student Academic Copilot

An AI-powered academic assistant built with Streamlit and Groq LLM that helps students learn, organize, and manage their studies efficiently. The application provides intelligent chat support, PDF question answering, text summarization, study plan generation, image explanation, and user activity tracking in a secure environment.

## 🚀 Features

### 🔐 User Authentication

* Secure user registration and login system
* Password hashing using bcrypt
* Session management for personalized access

### 💬 AI Chat Assistant

* Interactive chatbot powered by Groq LLM
* Context-aware conversations
* Chat history storage and retrieval
* Download chat conversations

### 📄 PDF Chat

* Upload PDF documents
* Ask questions based on PDF content
* AI-generated answers from document text
* Download responses for future reference

### 📝 Text Summarizer

* Convert lengthy content into concise summaries
* AI-powered text analysis
* Save and view summary history
* Download summarized content

### 📚 Study Planner

* Generate personalized study plans
* Topic-based learning schedules
* AI-assisted academic planning
* Export study plans

### 🖼️ Image Explanation

* Upload images for analysis
* Ask questions about uploaded images
* Receive AI-generated explanations
* Download generated insights

### 📊 Dashboard Analytics

* User activity tracking
* Daily usage statistics
* Message count metrics
* Visual activity reports

### 📜 History Management

* Complete conversation history
* Feature-specific history tracking
* Timestamped records for all interactions

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **Database:** SQLite
* **AI Model:** Groq (Llama 3.1 8B Instant)
* **Authentication:** bcrypt
* **PDF Processing:** PyPDF2
* **Data Analysis:** Pandas
* **Environment Management:** python-dotenv

## 📦 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/student-academic-copilot.git
cd student-academic-copilot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
DATABASE_URL=sqlite:///app6.db
```

4. Run the application:

```bash
streamlit run app.py
```

## 🎯 Use Cases

* Academic research assistance
* Document-based learning
* Study schedule creation
* Quick content summarization
* Educational Q&A
* Learning resource organization

## 🔒 Security Features

* Hashed password storage
* Secure user authentication
* Session-based access control
* Protected user data management

## 📈 Future Enhancements

* Multi-file PDF support
* Advanced image understanding
* Voice-based interaction
* Export reports in multiple formats
* Personalized learning recommendations
* Cloud database integration

## 👨‍💻 Author

Developed as an AI-powered educational platform to enhance student productivity and learning efficiency.

---

