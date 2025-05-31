import React, { useState } from 'react';

// Generic AI Call Function (reused from previous apps)
const callGeminiAPI = async (prompt) => {
  const chatHistory = [{ role: "user", parts: [{ text: prompt }] }];
  const payload = { contents: chatHistory };
  const apiKey = ""; // Canvas will provide this at runtime
  const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();

    if (result.candidates && result.candidates.length > 0 &&
        result.candidates[0].content && result.candidates[0].content.parts &&
        result.candidates[0].content.parts.length > 0) {
      return result.candidates[0].content.parts[0].text;
    } else {
      console.error("Unexpected API response structure:", result);
      return "Error: Could not get a valid response from AI. Please try again.";
    }
  } catch (error) {
    console.error("Error calling Gemini API:", error);
    return "Error: Failed to connect to AI. Please check your network or try again later.";
  }
};

// Main App component for the Structured Problem-Solver
const App = () => {
  const [currentStep, setCurrentStep] = useState(1); // 1: Problem, 2: Questions, 3: Events, 4: Result
  const [problemStatement, setProblemStatement] = useState('');
  const [aiGeneratedQuestions, setAiGeneratedQuestions] = useState('');
  const [userAnswersToQuestions, setUserAnswersToQuestions] = useState('');
  const [supportingEvents, setSupportingEvents] = useState('');
  const [finalSolution, setFinalSolution] = useState('');
  const [finalFeedback, setFinalFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleProblemSubmit = async () => {
    if (!problemStatement.trim()) {
      setErrorMessage("Please describe your problem to proceed.");
      return;
    }
    setLoading(true);
    setErrorMessage('');
    // AI generates questions based on the initial problem
    const prompt = `As a student, I have the following problem: "${problemStatement}". To help me understand this problem better and find a solution, please ask me 3-5 concise, insightful follow-up questions. Format them as a numbered list.`;
    const response = await callGeminiAPI(prompt);
    setAiGeneratedQuestions(response);
    setLoading(false);
    setCurrentStep(2);
  };

  const handleQuestionsAnswered = () => {
    if (!userAnswersToQuestions.trim()) {
      setErrorMessage("Please answer the questions to proceed.");
      return;
    }
    setErrorMessage('');
    setCurrentStep(3);
  };

  const handleEventsSubmitted = async () => {
    if (!supportingEvents.trim()) {
      setErrorMessage("Please provide some relevant events or details to proceed.");
      return;
    }
    setLoading(true);
    setErrorMessage('');

    // Consolidate all information for the final AI call
    full_context_prompt = (
    "As a student, I need help solving a problem. Here's a structured overview of my situation:\n\n"
    f"Problem: \"{problem}\"\n\n"
    f"My answers to follow-up questions:\n\"{answers}\"\n\n"
    f"Relevant events or specific details:\n\"{events}\"\n\n"
    "Based on ALL this information, please do two things:\n"
    "1. Provide a clear, actionable solution.\n"
    "2. Provide constructive feedback to improve my problem-solving approach."
)


Problem: "${problemStatement}"

My answers to follow-up questions that clarify the problem:
"${userAnswersToQuestions}"

Relevant events or specific details that happened:
"${supportingEvents}"

Based on ALL this information, please do two things:
1. Provide a clear, actionable solution or a set of steps to address my problem.
2. Provide constructive feedback on my overall understanding of the problem and the clarity of the information I provided, suggesting how I could further refine my problem-solving approach in the future.`;

    const response = await callGeminiAPI(fullContextPrompt);
    // Attempt to split solution and feedback (heuristic)
    const solutionStartIndex = response.toLowerCase().indexOf("solution:");
    const feedbackStartIndex = response.toLowerCase().indexOf("feedback:");

    if (solutionStartIndex !== -1 && feedbackStartIndex !== -1) {
      if (solutionStartIndex < feedbackStartIndex) {
        setFinalSolution(response.substring(solutionStartIndex + "solution:".length, feedbackStartIndex).trim());
        setFinalFeedback(response.substring(feedbackStartIndex + "feedback:".length).trim());
      } else { // Feedback came first
        setFinalFeedback(response.substring(feedbackStartIndex + "feedback:".length, solutionStartIndex).trim());
        setFinalSolution(response.substring(solutionStartIndex + "solution:".length).trim());
      }
    } else if (solutionStartIndex !== -1) {
        setFinalSolution(response.substring(solutionStartIndex + "solution:".length).trim());
        setFinalFeedback("No explicit feedback section found, but consider the solution's clarity.");
    } else if (feedbackStartIndex !== -1) {
        setFinalFeedback(response.substring(feedbackStartIndex + "feedback:".length).trim());
        setFinalSolution("No explicit solution section found, but consider the feedback for your problem-solving.");
    } else {
        # Fallback if AI doesn't use "Solution:" and "Feedback:" exactly
        setFinalSolution("AI generated response (could not parse into specific solution/feedback sections):\n" + response);
        setFinalFeedback("");
    }

    setLoading(false);
    setCurrentStep(4);
  };

  const handleRestart = () => {
    setCurrentStep(1);
    setProblemStatement('');
    setAiGeneratedQuestions('');
    setUserAnswersToQuestions('');
    setSupportingEvents('');
    setFinalSolution('');
    setFinalFeedback('');
    setErrorMessage('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 sm:p-8 flex flex-col items-center">
      <header className="w-full max-w-4xl bg-white shadow-lg rounded-xl p-6 mb-8 text-center">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4 tracking-tight">
          Structured AI Problem-Solver
        </h1>
        <p className="text-lg text-gray-600">
          A step-by-step assistant to help students define, understand, and solve problems with AI guidance.
        </p>
      </header>

      <main className="w-full max-w-4xl bg-white shadow-xl rounded-xl p-6 sm:p-8">
        {errorMessage && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative mb-6" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> {errorMessage}</span>
          </div>
        )}

        {/* Step 1: Identify Your Problem */}
        {currentStep === 1 && (
          <div className="p-6 border border-gray-200 rounded-lg bg-gray-50 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Step 1: Identify Your Problem</h2>
            <p className="text-gray-700 mb-4">
              Start by clearly stating the problem or challenge you are facing. Be as specific as possible.
            </p>
            <label htmlFor="problemStatement" className="block text-gray-700 text-sm font-bold mb-2">
              My Problem Is:
            </label>
            <textarea
              id="problemStatement"
              className="shadow appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-400 h-32 resize-y"
              placeholder="e.g., I'm consistently late submitting my assignments because I procrastinate."
              value={problemStatement}
              onChange={(e) => setProblemStatement(e.target.value)}
            ></textarea>
            <button
              onClick={handleProblemSubmit}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg focus:outline-none focus:shadow-outline transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
              disabled={loading}
            >
              {loading ? 'Asking AI for Questions...' : 'Submit Problem & Get Clarifying Questions'}
            </button>
            <p className="mt-4 text-sm text-gray-600">
              **Skill Development Tip:** Clearly defining the problem is half the solution. This step helps you practice precision in articulation.
            </p>
          </div>
        )}

        {/* Step 2: Brainstorm for Understanding (AI asks questions) */}
        {currentStep === 2 && (
          <div className="p-6 border border-gray-200 rounded-lg bg-gray-50 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Step 2: Brainstorm for Understanding</h2>
            <p className="text-gray-700 mb-4">
              The AI has generated some questions to help you think more deeply about your problem. Please answer them to provide more context.
            </p>
            {loading ? (
              <p className="text-gray-600">AI is generating questions...</p>
            ) : (
              aiGeneratedQuestions && (
                <div className="mb-4 p-4 bg-blue-50 rounded-lg shadow-inner border border-blue-200">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">AI's Clarifying Questions:</h3>
                  <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: aiGeneratedQuestions.replace(/\n/g, '<br>') }} />
                </div>
              )
            )}
            <label htmlFor="userAnswersToQuestions" className="block text-gray-700 text-sm font-bold mb-2 mt-4">
              Your Answers:
            </label>
            <textarea
              id="userAnswersToQuestions"
              className="shadow appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-400 h-48 resize-y"
              placeholder="Provide detailed answers to the AI's questions here."
              value={userAnswersToQuestions}
              onChange={(e) => setUserAnswersToQuestions(e.target.value)}
            ></textarea>
            <button
              onClick={handleQuestionsAnswered}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg focus:outline-none focus:shadow-outline transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
              disabled={loading}
            >
              Continue to Events
            </button>
            <p className="mt-4 text-sm text-gray-600">
              **Skill Development Tip:** Answering probing questions enhances your analytical and self-reflection skills, leading to a deeper understanding of the root cause.
            </p>
          </div>
        )}

        {/* Step 3: Provide Supporting Events */}
        {currentStep === 3 && (
          <div className="p-6 border border-gray-200 rounded-lg bg-gray-50 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Step 3: Provide Supporting Events/Context</h2>
            <p className="text-gray-700 mb-4">
              Describe specific events, scenarios, or situations where this problem occurs or is particularly noticeable. This helps the AI understand the real-world context.
            </p>
            <label htmlFor="supportingEvents" className="block text-gray-700 text-sm font-bold mb-2">
              Relevant Events/Details:
            </label>
            <textarea
              id="supportingEvents"
              className="shadow appearance-none border rounded-lg w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-indigo-400 h-48 resize-y"
              placeholder="e.g., 'Last week, I missed a deadline because I spent hours on social media instead of studying.' or 'I often feel overwhelmed when I have multiple assignments due in the same week.'"
              value={supportingEvents}
              onChange={(e) => setSupportingEvents(e.target.value)}
            ></textarea>
            <button
              onClick={handleEventsSubmitted}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg focus:outline-none focus:shadow-outline transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
              disabled={loading}
            >
              {loading ? 'Getting Solution & Feedback...' : 'Get Solution & Feedback'}
            </button>
            <p className="mt-4 text-sm text-gray-600">
              **Skill Development Tip:** Providing concrete examples strengthens your ability to identify patterns and specific triggers related to a problem.
            </p>
          </div>
        )}

        {/* Step 4: Solution and Feedback */}
        {currentStep === 4 && (
          <div className="p-6 border border-gray-200 rounded-lg bg-gray-50 shadow-sm">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Step 4: AI's Solution & Feedback</h2>
            <p className="text-gray-700 mb-4">
              Based on all the information you provided, here is the AI's suggested solution and feedback on your problem-solving process.
            </p>
            {loading ? (
              <p className="text-gray-600">Generating solution and feedback...</p>
            ) : (
              <>
                {finalSolution && (
                  <div className="mb-6 p-4 bg-green-50 rounded-lg shadow-inner border border-green-200">
                    <h3 className="text-xl font-semibold text-gray-800 mb-3">Suggested Solution:</h3>
                    <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: finalSolution.replace(/\n/g, '<br>') }} />
                    <p className="mt-4 text-sm text-gray-600">
                      **Skill Development Tip:** Evaluate this solution. Is it realistic? What are the first three steps you would take to implement it? This develops your practical implementation skills.
                    </p>
                  </div>
                )}
                {finalFeedback && (
                  <div className="p-4 bg-yellow-50 rounded-lg shadow-inner border border-yellow-200">
                    <h3 className="text-xl font-semibold text-gray-800 mb-3">Feedback on Your Process:</h3>
                    <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: finalFeedback.replace(/\n/g, '<br>') }} />
                    <p className="mt-4 text-sm text-gray-600">
                      **Skill Development Tip:** Reflect on the feedback. What did you do well? What could you improve in your next problem-solving attempt? Continuous self-assessment is key to mastery.
                    </p>
                  </div>
                )}
              </>
            )}
            <button
              onClick={handleRestart}
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg focus:outline-none focus:shadow-outline transition-colors duration-300 mt-6"
            >
              Start New Problem
            </button>
          </div>
        )}
      </main>

      <footer className="w-full max-w-4xl text-center text-gray-600 mt-8">
        <p>&copy; 2025 Structured AI Problem-Solver. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;

