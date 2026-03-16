import sys
import subprocess
import json
import requests
import re
import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
EVAL_MODEL = "llama3.2:3b"
LOG_FILE = "eval_history.jsonl"


def run_agent(topic):
    """Executes agent.py with the given topic and captures output."""
    try:
        result = subprocess.run(
            ["python", "agent.py", topic], capture_output=True, text=True, timeout=240
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout: The agent took more than 240 seconds.", 1
    except Exception as e:
        return "", str(e), 1


def extract_json_from_text(text):
    """Robustly extracts JSON even if the LLM wraps it in markdown blocks."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None


def evaluate_output(agent_output, topic, stderr, returncode):
    """Grades the agent's report using Llama 3.2 with a Fair Grading Rubric."""

    if returncode != 0:
        return (
            0,
            f"Critical System Error. The script crashed. Fix the following error:\n{stderr[-500:]}",
        )

    if not agent_output:
        return 0, "Critical Failure: The agent ran successfully but produced no output."

    if agent_output.strip() == "{}" or '"error":' in agent_output.lower():
        return (
            0,
            "Critical Failure: The report is completely empty or explicitly states it failed to fetch data.",
        )

    prompt = f"""
    You are a strict but fair Senior Financial Auditor evaluating an AI-generated equity research report about the asset/company: {topic}.
    
    GRADING CRITERIA:
    1. Zero Hallucination (Crucial): Every financial claim MUST have a source citation (e.g., [SOURCE 1]). Grouped citations like [SOURCE 1, 2] are acceptable.
    2. Factual Accuracy: Data must be specific to {topic}. It should mention realistic corporate metrics like Market Cap, Revenue, or Net Income based on the context.
    3. Completeness vs Reality: If a specific data point is genuinely not available, the agent stating "Data not found" is a GOOD behavior and should not result in a score of 0.
    
    SCORING GUIDE:
    - 90-100: Excellent report, accurate corporate data, sources cited clearly.
    - 60-89: Good report, but missed some available data or formatting is slightly messy.
    - 10-59: Severe issues, missing citations for major numbers, or hallucinated metrics.
    - 0: Completely empty JSON, crashed, or hallucinated numbers without any sources.
    
    You MUST output YOUR EVALUATION strictly as a JSON object matching this exact structure:
    {{
        "reasoning": "Explain your score. Acknowledge what the agent did right and what it missed.",
        "score": <integer between 0 and 100>,
        "actionable_feedback": "Give 1 clear instruction to the developer to improve."
    }}
    
    Report to evaluate:
    \"\"\"{agent_output}\"\"\"
    """

    payload = {"model": EVAL_MODEL, "prompt": prompt, "stream": False, "format": "json"}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_response = response.json()["response"]

        eval_data = extract_json_from_text(raw_response)
        if not eval_data:
            return 10, f"Evaluator failed to output valid JSON. Raw: {raw_response}"

        score = eval_data.get("score", 0)
        feedback = f"{eval_data.get('reasoning', '')} | ACTION REQUIRED: {eval_data.get('actionable_feedback', 'No feedback.')}"
        return score, feedback

    except Exception as e:
        return 0, f"Evaluator API Error: {e}"


def log_evaluation(topic, score, feedback, returncode):
    """Logs the run history."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "topic": topic,
        "score": score,
        "crashed": returncode != 0,
        "feedback": feedback,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python eval.py <Topic>")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    print(f"Running agent.py for topic: '{topic}'...")
    stdout, stderr, returncode = run_agent(topic)

    if stderr and returncode != 0:
        print(f"\n[!] Agent execution failed with return code {returncode}.")

    print("Evaluating output...")
    score, feedback = evaluate_output(stdout, topic, stderr, returncode)
    log_evaluation(topic, score, feedback, returncode)

    print(f"\n{'=' * 40}")
    print(f" EVALUATION RESULTS ")
    print(f"{'=' * 40}")
    print(f"SCORE: {score}/100")
    print(f"FEEDBACK: {feedback}")
    print(f"{'=' * 40}\n")
    with open(".last_score", "w") as f:
        f.write(str(score))
