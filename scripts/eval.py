#!/usr/bin/env python3
"""
Eval suite for the RAG pipeline.

Runs a set of question/expected-answer pairs against a transcript,
scores retrieval relevance and answer quality, prints a report.

Usage:
  python scripts/eval.py path/to/transcript.txt path/to/evals.json
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from anthropic import Anthropic
from backend.rag import RAGEngine

CLAUDE_MODEL = "claude-sonnet-4-20250514"

JUDGE_PROMPT = """You are evaluating a RAG system's answer quality.

Original question: {question}
Expected answer theme: {expected}
Actual answer: {actual}

Score the actual answer on two dimensions (1-5 each):
1. Relevance: Does it address the question?
2. Accuracy: Is it consistent with the expected theme?

Respond ONLY with valid JSON like: {{"relevance": 4, "accuracy": 3, "reasoning": "..."}}
"""


def judge_answer(client: Anthropic, question: str, expected: str, actual: str) -> dict:
    prompt = JUDGE_PROMPT.format(question=question, expected=expected, actual=actual)
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    try:
        return json.loads(text)
    except Exception:
        return {"relevance": 0, "accuracy": 0, "reasoning": "parse error"}


def run_eval(transcript_path: str, evals_path: str):
    with open(transcript_path) as f:
        text = f.read()

    with open(evals_path) as f:
        evals = json.load(f)

    engine = RAGEngine()
    client = Anthropic()

    meta = engine.load(text, source=os.path.basename(transcript_path))
    print(f"\nLoaded: {meta['source']} ({meta['chunk_count']} chunks)")
    print(f"Running {len(evals)} eval cases...\n")
    print(f"{'#':<4} {'Question':<40} {'Rel':>4} {'Acc':>4}")
    print("─" * 60)

    results = []
    for i, case in enumerate(evals):
        question = case["question"]
        expected = case["expected"]

        result = engine.query(question, meta["collection_id"], top_k=3)
        scores = judge_answer(client, question, expected, result["answer"])

        results.append({
            "question": question,
            "answer": result["answer"],
            "scores": scores,
            "top_chunk_relevance": result["chunks"][0]["relevance"] if result["chunks"] else 0,
        })

        rel = scores.get("relevance", 0)
        acc = scores.get("accuracy", 0)
        q_short = question[:38] + ".." if len(question) > 40 else question
        rel_str = f"\033[92m{rel}\033[0m" if rel >= 4 else f"\033[93m{rel}\033[0m" if rel >= 3 else f"\033[91m{rel}\033[0m"
        acc_str = f"\033[92m{acc}\033[0m" if acc >= 4 else f"\033[93m{acc}\033[0m" if acc >= 3 else f"\033[91m{acc}\033[0m"
        print(f"{i+1:<4} {q_short:<40} {rel_str:>4} {acc_str:>4}")

        time.sleep(0.5)

    avg_rel = sum(r["scores"].get("relevance", 0) for r in results) / len(results)
    avg_acc = sum(r["scores"].get("accuracy", 0) for r in results) / len(results)
    avg_chunk = sum(r["top_chunk_relevance"] for r in results) / len(results)

    print("─" * 60)
    print(f"\nResults:")
    print(f"  Avg relevance:       {avg_rel:.2f}/5")
    print(f"  Avg accuracy:        {avg_acc:.2f}/5")
    print(f"  Avg chunk relevance: {avg_chunk:.2%}")

    out_path = "eval_results.json"
    with open(out_path, "w") as f:
        json.dump({"summary": {"avg_relevance": avg_rel, "avg_accuracy": avg_acc}, "cases": results}, f, indent=2)
    print(f"\nFull results saved to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/eval.py <transcript.txt> <evals.json>")
        print("\nExample evals.json:")
        print(json.dumps([{"question": "What is the main topic?", "expected": "A high-level summary of the key theme"}], indent=2))
        sys.exit(1)
    run_eval(sys.argv[1], sys.argv[2])
