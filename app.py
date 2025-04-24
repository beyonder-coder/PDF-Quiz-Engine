import streamlit as st
import time
from utils import extract_text_from_pdf, parse_merged_pdf

st.set_page_config(layout="wide")

# CSS
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
    .timer {
        font-size: 24px !important;
        color: #FF6347;
        font-weight: bold;
        text-align: right;
    }
    .dashboard-box {
        padding: 5px 10px;
        margin: 2px;
        border-radius: 8px;
        display: inline-block;
        font-weight: bold;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">📄 PDF Quiz Engine - NEET Style</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your merged test PDFs and start your quiz!</p>', unsafe_allow_html=True)

# Session state init
for key in ["questions", "answers", "marked", "started", "index", "review", "time_left"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key in ["marked", "review"] else False if key == "started" else []

# Upload
col1, col2 = st.columns(2)
with col1:
    uploaded_pdf = st.file_uploader("📝 Upload Merged PDF (Questions + Answer Key)", type=["pdf"])

set_time = st.number_input("⏱️ Set Time Limit (minutes)", min_value=1, value=40)
progress_bar = st.progress(0)

# Analyze
if uploaded_pdf:
    with st.spinner("🔍 Analyzing Merged PDF..."):
        raw_text = extract_text_from_pdf(uploaded_pdf)

        st.session_state.questions, st.session_state.answers = parse_merged_pdf(raw_text)

        progress_bar.progress(1.0)
        st.success("✅ Analysis Completed")

# Start Test
if st.session_state.questions and st.session_state.answers and not st.session_state.started:
    if st.button("🚀 Start Test"):
        st.session_state.index = 0
        st.session_state.marked = {}
        st.session_state.review = {}
        st.session_state.started = True
        st.session_state.time_left = int(set_time * 60)

# Countdown Timer
if st.session_state.started:
    mins, secs = divmod(st.session_state.time_left, 60)
    st.markdown(f'<p class="timer">⏳ Time Left: {mins:02}:{secs:02}</p>', unsafe_allow_html=True)
    st.session_state.time_left -= 1
    time.sleep(1)
    if st.session_state.time_left <= 0:
        st.warning("⏰ Time's up! Submitting your test...")
        st.session_state.started = False

# Summary Dashboard
if st.session_state.started:
    st.markdown("### 📊 Question Dashboard")
    dashboard = ""
    for i in range(1, len(st.session_state.questions) + 1):
        status = "⬜"
        if i in st.session_state.review:
            status = "🔖"
        elif i in st.session_state.marked:
            status = "✅"
        else:
            status = "⏭️"
        dashboard += f'<button onclick="window.location.href=\'#{i}\'" style="margin:2px;">{status} {i}</button>'
    st.markdown(dashboard, unsafe_allow_html=True)

    jump_q = st.number_input("🔢 Jump to Question:", min_value=1, max_value=len(st.session_state.questions), step=1, value=st.session_state.index + 1)
    st.session_state.index = jump_q - 1

# Quiz Interface
if st.session_state.started:
    st.markdown("---")
    q_idx = st.session_state.index
    q = st.session_state.questions[q_idx]
    st.subheader(f"Q{q_idx + 1}: {q['question']}")

    # Mark for review
    st.checkbox("🔖 Mark for Review", key=f"review_{q_idx}", on_change=lambda: st.session_state.review.update({q_idx + 1: True}))

    if len(q['options']) >= 2:
        options_with_skip = ["Skip this question"] + q['options']
        user_answer = st.radio("Choose your answer:", options_with_skip, key=f"q{q_idx}")

        if user_answer != "Skip this question":
            st.session_state.marked[q_idx + 1] = user_answer[0]
        else:
            st.session_state.marked.pop(q_idx + 1, None)

        # Show correct/incorrect
        correct_ans = st.session_state.answers.get(q_idx + 1)
        user_selected = st.session_state.marked.get(q_idx + 1)

        if user_selected:
            if user_selected == correct_ans:
                st.success(f"✅ Correct! Answer is {correct_ans}")
            else:
                st.error(f"❌ Incorrect. Your answer: {user_selected}, Correct: {correct_ans}")
    else:
        st.warning("⚠️ This question is not properly formatted or missing options.")

    # Navigation
    col1, col2, col3 = st.columns(3)
    if q_idx > 0:
        if col1.button("⬅️ Previous"):
            st.session_state.index -= 1
    if q_idx < len(st.session_state.questions) - 1:
        if col2.button("➡️ Next"):
            st.session_state.index += 1
    if col3.button("✅ Submit Test"):
        st.session_state.started = False
        correct = 0
        for i, ans in st.session_state.answers.items():
            if st.session_state.marked.get(i, '') == ans:
                correct += 1
        total = len(st.session_state.questions)
        marked_count = len(st.session_state.marked)
        skipped = total - marked_count
        review_count = len(st.session_state.review)
        st.balloons()
        st.success(f"🎯 Test Completed!\n\n✅ Correct: {correct}\n❌ Incorrect: {marked_count - correct}\n🔘 Skipped: {skipped}\n🔖 Marked for Review: {review_count}")
