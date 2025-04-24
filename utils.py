import PyPDF2
import re

def extract_text_from_pdf(uploaded_pdf):
    reader = PyPDF2.PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_questions(raw_text):
    questions = []
    pattern = r'(\d+\.\s.*?)(?=\n\d+\.|\Z)'  # Match Q. followed by options until next question
    matches = re.findall(pattern, raw_text, re.DOTALL)

    for match in matches:
        lines = match.strip().split('\n')
        if len(lines) < 5:
            continue  # Skip if not enough lines for 1 Q + 4 options
        q_text = lines[0].strip()
        options = [line.strip() for line in lines[1:] if line.strip() != '']
        if len(options) == 4:
            questions.append({"question": q_text, "options": options})
    return questions

def parse_answer_key(raw_text):
    lines = raw_text.strip().split('\n')
    answers = {}
    for line in lines:
        match = re.match(r'(\d+)\.\s*\((\d)\)', line)
        if match:
            q_no = int(match.group(1))
            opt_num = int(match.group(2))
            # Map 1–4 to A–D
            opt_letter = ['A', 'B', 'C', 'D'][opt_num - 1]
            answers[q_no] = opt_letter
    return answers
