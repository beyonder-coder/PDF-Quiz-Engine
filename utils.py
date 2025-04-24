import PyPDF2
import re

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_pdf):
    reader = PyPDF2.PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to parse questions and answers from merged PDF
def parse_merged_pdf(raw_text):
    # Split the raw text into two parts: Questions and Answers
    sections = raw_text.strip().split("\f")  # Assuming \f is the page break, adjust if needed
    question_section = sections[0].strip()
    answer_section = sections[-1].strip()

    # Parse the questions and options
    questions = []
    option_prefixes = ['A', 'B', 'C', 'D']
    blocks = question_section.split("\n\n")
    
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue  # Skip empty or malformed blocks

        # First line should be the question
        question_text = lines[0].strip()
        options = []
        
        # Parse the options
        for line in lines[1:]:
            line = line.strip()
            match = re.match(r"^(\d+|[A-Da-d])[).]\s*(.*)", line)
            if match:
                option_text = match.group(2).strip()
            else:
                option_text = line
            options.append(option_text)

        # Format the options (A, B, C, D)
        formatted_options = [f"{label}) {text}" for label, text in zip(option_prefixes, options)]
        
        # Add the question to the list
        questions.append({"question": question_text, "options": formatted_options})

    # Parse the answer section
    answers = {}
    answer_lines = answer_section.split("\n")
    
    for answer_line in answer_lines:
        answer_line = answer_line.strip()
        match = re.match(r"^(\d+)\)\s*([A-Da-d])", answer_line)
        if match:
            q_num = int(match.group(1))  # Get the question number
            answer = match.group(2).upper()  # Get the answer (A, B, C, D)
            answers[q_num] = answer  # Store the answer in the answers dictionary

    return questions, answers

# Example Usage
uploaded_pdf = "path_to_merged_pdf.pdf"  # Replace this with actual file upload path
raw_text = extract_text_from_pdf(uploaded_pdf)
questions, answers = parse_merged_pdf(raw_text)

# Print the parsed questions and answers for debugging
print("Questions:")
for q in questions:
    print(f"{q['question']} - {q['options']}")
print("\nAnswers:")
print(answers)
