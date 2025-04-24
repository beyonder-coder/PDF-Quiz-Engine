let questions = [], answers = [], currentQuestion = 0;
let selectedAnswers = [], timerInterval;

const startBtn = document.getElementById("start-btn");
const questionInput = document.getElementById("question-pdf");
const answerInput = document.getElementById("answer-pdf");
const timerInput = document.getElementById("set-timer");
const quizContainer = document.getElementById("quiz-container");
const questionBox = document.getElementById("question-box");
const optionsList = document.getElementById("options-list");
const resultBox = document.getElementById("result-box");
const nextBtn = document.getElementById("next-btn");
const submitBtn = document.getElementById("submit-btn");
const timerDisplay = document.getElementById("timer-display");
const progressBar = document.getElementById("progress-bar");
const progressBarContainer = document.getElementById("progress-bar-container");

questionInput.addEventListener("change", checkFiles);
answerInput.addEventListener("change", checkFiles);

function checkFiles() {
  if (questionInput.files[0] && answerInput.files[0]) {
    startBtn.disabled = false;
  }
}

async function extractText(file, updateProgress) {
  const pdfData = new Uint8Array(await file.arrayBuffer());
  const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise;
  let text = "";
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const content = await page.getTextContent();
    text += content.items.map(item => item.str).join(" ") + "\n";
    updateProgress(i / pdf.numPages);
  }
  return text;
}

function parseQuestions(text) {
  const regex = /\d+\.\s*(.*?)\s*A\.?\s*(.*?)\s*B\.?\s*(.*?)\s*C\.?\s*(.*?)\s*D\.?\s*(.*?)(?=\d+\.|$)/gs;
  let match, result = [];
  while ((match = regex.exec(text)) !== null) {
    result.push({
      question: match[1].trim(),
      options: {
        A: match[2].trim(),
        B: match[3].trim(),
        C: match[4].trim(),
        D: match[5].trim(),
      }
    });
  }
  return result;
}

function parseAnswers(text) {
  return (text.match(/[A-D]/g) || []).map(a => a.trim());
}

function updateProgressBar(value) {
  progressBarContainer.style.display = "block";
  progressBar.style.width = `${value * 100}%`;
}

function showQuestion(index) {
  const q = questions[index];
  questionBox.textContent = `Q${index + 1}. ${q.question}`;
  optionsList.innerHTML = "";
  ["A", "B", "C", "D"].forEach(option => {
    const li = document.createElement("li");
    li.textContent = `${option}. ${q.options[option]}`;
    li.onclick = () => {
      selectedAnswers[index] = option;
      [...optionsList.children].forEach(opt => opt.classList.remove("selected"));
      li.classList.add("selected");
    };
    optionsList.appendChild(li);
  });
  nextBtn.style.display = index === questions.length - 1 ? "none" : "inline-block";
  submitBtn.classList.toggle("hidden", index !== questions.length - 1);
}

function startTimer(minutes) {
  let totalSeconds = minutes * 60;
  function updateTimer() {
    const m = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
    const s = String(totalSeconds % 60).padStart(2, "0");
    timerDisplay.textContent = `⏱️ ${m}:${s}`;
    if (--totalSeconds < 0) {
      clearInterval(timerInterval);
      showResult();
    }
  }
  updateTimer();
  timerInterval = setInterval(updateTimer, 1000);
}

function showResult() {
  let correct = 0, incorrect = 0;
  for (let i = 0; i < questions.length; i++) {
    if (selectedAnswers[i] === answers[i]) correct++;
    else incorrect++;
  }
  quizContainer.classList.add("hidden");
  resultBox.classList.remove("hidden");
  resultBox.textContent = `✅ Correct: ${correct} | ❌ Incorrect: ${incorrect}`;
}

startBtn.onclick = async () => {
  startBtn.disabled = true;
  updateProgressBar(0);

  const questionText = await extractText(questionInput.files[0], p => updateProgressBar(p * 0.5));
  const answerText = await extractText(answerInput.files[0], p => updateProgressBar(0.5 + p * 0.5));

  questions = parseQuestions(questionText);
  answers = parseAnswers(answerText);
  selectedAnswers = Array(questions.length).fill(null);

  if (!questions.length || !answers.length) {
    alert("❌ Failed to extract questions or answers. Please check PDF format.");
    return;
  }

  document.getElementById("progress-bar-container").style.display = "none";
  quizContainer.classList.remove("hidden");
  showQuestion(currentQuestion);
  startTimer(parseInt(timerInput.value) || 90);
};

nextBtn.onclick = () => {
  if (currentQuestion < questions.length - 1) {
    currentQuestion++;
    showQuestion(currentQuestion);
  }
};

submitBtn.onclick = showResult;
