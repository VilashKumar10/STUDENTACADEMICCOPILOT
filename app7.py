import streamlit as st
import os
import sqlite3
import bcrypt
import re
from groq import Groq
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import pandas as pd
import datetime

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Student Academic Copilot", layout="wide")

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
api_key = os.getenv("GROQ_API_KEY")

def get_database_path():
    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        return os.path.join(BASE_DIR, "app6.db")

    if db_url.startswith("sqlite:///"):
        sqlite_path = db_url[len("sqlite:///"):]
        if sqlite_path.startswith("/"):
            sqlite_path = sqlite_path[1:]
        if os.path.isabs(sqlite_path):
            return sqlite_path
        return os.path.join(BASE_DIR, sqlite_path)

    return db_url

if not api_key:
    st.error("⚠️ Add GROQ_API_KEY in .env file")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect(get_database_path(), check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password BLOB
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    role TEXT,
    message TEXT,
    timestamp TEXT
)
""")

conn.commit()

# -----------------------------
# SECURITY
# -----------------------------
def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def strong_password(password):
    return len(password) >= 6

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# -----------------------------
# SAVE CHAT (UPDATED)
# -----------------------------
def save_chat(email, role, message, feature="chat"):
    cursor.execute("""
        INSERT INTO chats (email, role, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (email, role, f"[{feature.upper()}] {message}", str(datetime.datetime.now())))
    conn.commit()

# -----------------------------
# LOAD HISTORY
# -----------------------------
def load_history(email):
    cursor.execute("""
        SELECT role, message FROM chats
        WHERE email=? ORDER BY id DESC LIMIT 10
    """, (email,))
    rows = cursor.fetchall()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

def load_feature_history(email, feature, limit=10):
    cursor.execute("""
        SELECT role, message, timestamp FROM chats
        WHERE email=? AND message LIKE ? ORDER BY id DESC LIMIT ?
    """, (email, f"[{feature.upper()}]%", limit))
    rows = cursor.fetchall()
    history = []
    for r in reversed(rows):
        message = r[1]
        if "] " in message:
            message = message.split("] ", 1)[1]
        history.append({"role": r[0], "content": message, "timestamp": r[2]})
    return history

# -----------------------------
# SESSION
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# -----------------------------
# AUTH
# -----------------------------
if not st.session_state.logged_in:

    st.title("🎓 Student Academic Copilot ")

    if st.session_state.page == "login":
        st.subheader("📧 Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            cursor.execute("SELECT password FROM users WHERE email=?", (email,))
            result = cursor.fetchone()

            if result and check_password(password, result[0]):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

        if st.button("Create account"):
            st.session_state.page = "signup"
            st.rerun()

    else:
        st.subheader("📝 Signup")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Signup"):
            if not valid_email(email):
                st.warning("Enter valid email")
            elif not strong_password(password):
                st.warning("Password must be 6+ chars")
            else:
                cursor.execute("SELECT * FROM users WHERE email=?", (email,))
                if cursor.fetchone():
                    st.warning("User exists")
                else:
                    cursor.execute("INSERT INTO users VALUES (?, ?)",
                                   (email, hash_password(password)))
                    conn.commit()
                    st.success("Account created!")

        if st.button("Back"):
            st.session_state.page = "login"
            st.rerun()

    st.stop()

# -----------------------------
# MAIN UI
# -----------------------------
st.title("🎓 Student Academic Copilot")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Chat",
    "PDF Chat",
    "Summarizer",
    "Study Planner",
    "Image Explain",
    "History"
])

# -----------------------------
# LLM
# -----------------------------
def ask_llm(messages):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content
    except:
        return "⚠️ AI service unavailable"

history = load_history(st.session_state.email)

# -----------------------------
# DASHBOARD
# -----------------------------
if menu == "Dashboard":

    st.subheader(f"👤 {st.session_state.email}")

    cursor.execute("SELECT COUNT(*) FROM chats WHERE email=?",
                   (st.session_state.email,))
    total = cursor.fetchone()[0]

    st.metric("Total Messages", total)

    df = pd.read_sql_query("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM chats WHERE email=?
        GROUP BY date
    """, conn, params=(st.session_state.email,))

    if not df.empty:
        st.subheader("📊 Daily Usage")
        st.line_chart(df.set_index("date"))

# -----------------------------
# CHAT
# -----------------------------
elif menu == "Chat":

    st.subheader("💬 Chat")

    chat_text = ""

    for msg in history:
        role = "You" if msg["role"] == "user" else "AI"
        st.chat_message(msg["role"]).write(msg["content"])
        chat_text += f"{role}: {msg['content']}\n\n"

    st.download_button("📥 Download Chat", chat_text, "chat.txt")

    user_input = st.chat_input("Ask something...")

    if user_input:
        save_chat(st.session_state.email, "user", user_input, "chat")
        updated = load_history(st.session_state.email)
        answer = ask_llm(updated)
        save_chat(st.session_state.email, "assistant", answer, "chat")
        st.rerun()

# -----------------------------
# PDF CHAT
# -----------------------------
elif menu == "PDF Chat":

    pdf_history = load_feature_history(st.session_state.email, "pdf")
    if pdf_history:
        with st.expander("PDF Chat History"):
            for item in pdf_history:
                role = "You" if item["role"] == "user" else "AI"
                st.write(f"**{item['timestamp']}** – {role}: {item['content']}")
    else:
        st.info("No PDF chat history yet.")

    pdf = st.file_uploader("Upload PDF", type="pdf")

    if pdf:
        reader = PdfReader(pdf)
        text = ""

        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

        question = st.text_input("Ask question")

        if st.button("Ask"):
            save_chat(st.session_state.email, "user", question, "pdf")

            answer = ask_llm([{
                "role": "user",
                "content": text[:3000] + question
            }])

            save_chat(st.session_state.email, "assistant", answer, "pdf")

            st.write(answer)
            st.download_button("📥 Download Answer", answer, "pdf_answer.txt")

# -----------------------------
# SUMMARIZER
# -----------------------------
elif menu == "Summarizer":

    summary_history = load_feature_history(st.session_state.email, "summary")
    if summary_history:
        with st.expander("Summarizer History"):
            for item in summary_history:
                role = "You" if item["role"] == "user" else "AI"
                st.write(f"**{item['timestamp']}** – {role}: {item['content']}")
    else:
        st.info("No summarizer history yet.")

    text = st.text_area("Paste text")

    if st.button("Summarize"):
        save_chat(st.session_state.email, "user", text[:200], "summary")

        summary = ask_llm([{
            "role": "user",
            "content": f"Summarize:\n{text}"
        }])

        save_chat(st.session_state.email, "assistant", summary, "summary")

        st.write(summary)
        st.download_button("📥 Download Summary", summary, "summary.txt")

# -----------------------------
# STUDY PLANNER
# -----------------------------
elif menu == "Study Planner":

    planner_history = load_feature_history(st.session_state.email, "planner")
    if planner_history:
        with st.expander("Study Planner History"):
            for item in planner_history:
                role = "You" if item["role"] == "user" else "AI"
                st.write(f"**{item['timestamp']}** – {role}: {item['content']}")
    else:
        st.info("No study planner history yet.")

    topic = st.text_input("Enter topic")

    if st.button("Generate"):
        save_chat(st.session_state.email, "user", topic, "planner")

        plan = ask_llm([{
            "role": "user",
            "content": f"Create study plan for {topic}"
        }])

        save_chat(st.session_state.email, "assistant", plan, "planner")

        st.write(plan)
        st.download_button("📥 Download Plan", plan, "study_plan.txt")

# -----------------------------
# IMAGE EXPLAIN
# -----------------------------
elif menu == "Image Explain":

    st.subheader("🖼️ Image Explanation AI")

    image_history = load_feature_history(st.session_state.email, "image")
    if image_history:
        with st.expander("Image Explain History"):
            for item in image_history:
                role = "You" if item["role"] == "user" else "AI"
                st.write(f"**{item['timestamp']}** – {role}: {item['content']}")
    else:
        st.info("No image explain history yet.")

    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        st.image(uploaded_image, width="stretch")

        question = st.text_input("Ask about image")

        if st.button("Explain Image"):
            save_chat(
                st.session_state.email,
                "user",
                question if question else "Explain image",
                "image"
            )

            prompt = question if question else "Describe this image clearly."

            answer = ask_llm([{
                "role": "user",
                "content": prompt
            }])

            save_chat(st.session_state.email, "assistant", answer, "image")

            st.write(answer)
            st.download_button("📥 Download Explanation", answer, "image_explanation.txt")

# -----------------------------
# HISTORY
# -----------------------------
elif menu == "History":

    st.subheader("📜 Full History")

    cursor.execute("""
    SELECT role, message, timestamp FROM chats
    WHERE email=? ORDER BY id DESC
    """, (st.session_state.email,))

    rows = cursor.fetchall()

    for r in rows:
        st.write(f"{r[2]} - {r[0]}: {r[1]}")