import PyPDF2

def extract_text_from_pdf(uploaded_pdf):
    reader = PyPDF2.PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_questions(raw_text):
    questions = []
    parts = raw_text.strip().split("\n\n")
    for part in parts:
        lines = part.strip().split("\n")
        if len(lines) < 2:
            continue
        q_text = lines[0]
        options = lines[1:]
        questions.append({"question": q_text, "options": options})
    return questions

def parse_answer_key(raw_text):
    lines = raw_text.strip().split("\n")
    answers = {}
    for line in lines:
        if '.' in line:
            q_no, ans = line.split('.', 1)
            ans = ans.strip()
            if '(' in ans and ')' in ans:
                final = ans[ans.find('(')+1:ans.find(')')]
                answers[int(q_no.strip())] = final
    return answers
