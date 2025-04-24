import streamlit as st
from utils import extract_text_from_pdf, parse_questions, parse_answer_key

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .title {
        font-size: 40px !important;
        text-align: center;
        color: #4CAF50;
        font-weight: bold;
    }
    .subtitle {
        font-size: 20px !important;
        color: #333333;
        margin-bottom: 20px;
    }
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">📄 PDF Quiz Engine - NEET Style</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle center">Upload your test PDFs and start your quiz journey!</p>', unsafe_allow_html=True)

# State init
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "marked" not in st.session_state:
    st.session_state.marked = {}

st.markdown("### 📤 Upload Files")

col1, col2 = st.columns(2)
with col1:
    uploaded_q_pdf = st.file_uploader("📝 Questions PDF", type=["pdf"])
with col2:
    uploaded_a_pdf = st.file_uploader("✅ Answer Key PDF", type=["pdf"])

set_time = st.number_input("⏱️ Set Time Limit (minutes)", min_value=1, value=40)

progress_bar = st.progress(0)

if uploaded_q_pdf and uploaded_a_pdf:
    with st.spinner("🔍 Analyzing PDFs... Please wait"):
        raw_q_text = extract_text_from_pdf(uploaded_q_pdf)
        raw_a_text = extract_text_from_pdf(uploaded_a_pdf)

        st.session_state.questions = parse_questions(raw_q_text)
        st.session_state.answers = parse_answer_key(raw_a_text)
        progress_bar.progress(1.0)
        st.success("✅ Analysis Completed")

if st.session_state.questions and st.session_state.answers:
    st.markdown("---")
    col_start = st.columns(3)[1]
    with col_start:
        if st.button("🚀 Start Test", use_container_width=True):
            st.session_state.index = 0
            st.session_state.marked = {}
            st.session_state.started = True
            st.session_state.time_left = set_time * 60

if "started" in st.session_state and st.session_state.started:
    st.markdown("---")
    q = st.session_state.questions[st.session_state.index]
    st.subheader(f"Q{st.session_state.index + 1}: {q['question']}")

    if len(q['options']) >= 2:
    user_answer = st.radio("Choose your answer:", q['options'], index=-1, key=f"q{st.session_state.index}")
    if user_answer:
        st.session_state.marked[st.session_state.index + 1] = user_answer[1]
else:
    st.warning("⚠️ This question is not properly formatted or missing options. Skipping...")

    if user_answer:
        st.session_state.marked[st.session_state.index + 1] = user_answer[1]

    col1, col2 = st.columns(2)
    if st.session_state.index < len(st.session_state.questions) - 1:
        if col1.button("➡️ Next Question"):
            st.session_state.index += 1
    else:
        if col1.button("✅ Submit Test"):
            st.session_state.started = False
            correct = 0
            for i, ans in st.session_state.answers.items():
                if st.session_state.marked.get(i, '') == ans:
                    correct += 1
            total = len(st.session_state.questions)
            st.balloons()
            st.success(f"🎯 Final Result: ✅ Correct: {correct} / ❌ Incorrect: {total - correct}")
