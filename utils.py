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
    parts = raw_text.strip().split("\n\n")
    option_prefixes = ['A', 'B', 'C', 'D']

    for part in parts:
        lines = part.strip().split("\n")
        if len(lines) < 2:
            continue

        q_text = lines[0].strip()
        options = []
        
        # Use regex to detect option format
        for line in lines[1:]:
            line = line.strip()
            match = re.match(r"^(\d+|[A-Da-d])[).]\s*(.*)", line)
            if match:
                option_label = match.group(1)
                option_text = match.group(2).strip()
            else:
                option_text = line

            options.append(option_text)

        formatted_options = [f"{label}) {text}" for label, text in zip(option_prefixes, options)]
        questions.append({"question": q_text, "options": formatted_options})
    
    return questions

def parse_answer_key(raw_text):
    lines = raw_text.strip().split("\n")
    answers = {}
    num_to_letter = { "1": "A", "2": "B", "3": "C", "4": "D" }

    for line in lines:
        line = line.strip()
        if ')' in line:
            parts = line.split(')', 1)
            if len(parts) == 2:
                q_no = parts[0].strip()
                ans_raw = parts[1].strip().upper()

                if '(' in ans_raw and ')' in ans_raw:
                    ans = ans_raw[ans_raw.find('(')+1:ans_raw.find(')')].strip()
                else:
                    ans = ans_raw.strip()

                final = num_to_letter.get(ans, ans)

                if q_no.isdigit():
                    answers[int(q_no)] = final
    return answers
