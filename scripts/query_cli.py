#!/usr/bin/env python3
"""
CLI for Transcript Intelligence.

Usage:
  python scripts/query_cli.py path/to/transcript.txt
  python scripts/query_cli.py https://youtube.com/watch?v=...
"""

import sys
import os
import readline

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.rag import RAGEngine
from backend.youtube import fetch_youtube_transcript

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"


def print_header():
    print(f"\n{BOLD}Transcript Intelligence CLI{RESET}")
    print(f"{DIM}{'─' * 40}{RESET}\n")


def load_source(engine: RAGEngine, source: str) -> dict:
    if source.startswith("http"):
        print(f"{DIM}Fetching YouTube transcript…{RESET}")
        text, title = fetch_youtube_transcript(source)
        return engine.load(text, source=title)
    else:
        if not os.path.exists(source):
            print(f"{RED}File not found: {source}{RESET}")
            sys.exit(1)
        with open(source) as f:
            text = f.read()
        return engine.load(text, source=os.path.basename(source))


def run_repl(engine: RAGEngine, collection_id: str):
    history = []
    print(f"\n{DIM}Type a question and press Enter. Ctrl+C to exit.{RESET}\n")

    while True:
        try:
            question = input(f"{CYAN}>{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Goodbye.{RESET}")
            break

        if not question:
            continue

        if question.lower() in ("exit", "quit", "q"):
            break

        result = engine.query(question, collection_id, top_k=3, history=history)

        print(f"\n{BOLD}{result['answer']}{RESET}\n")

        print(f"{DIM}─ Retrieved chunks ──────────────────────{RESET}")
        for i, chunk in enumerate(result["chunks"]):
            pct = int(chunk["relevance"] * 100)
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"  {YELLOW}[{i+1}]{RESET} {bar} {pct}%")
            print(f"      {DIM}{chunk['text'][:120]}…{RESET}\n")

        tokens = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
        print(f"{DIM}tokens: {tokens}{RESET}\n")

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": result["answer"]})

        rating = input(f"{DIM}Rate retrieval (g=good / b=bad / enter=skip): {RESET}").strip().lower()
        if rating in ("g", "good"):
            engine.log_feedback(result["query_id"], "good", collection_id)
        elif rating in ("b", "bad"):
            engine.log_feedback(result["query_id"], "bad", collection_id)
        print()


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python scripts/query_cli.py <file_or_youtube_url>")
        sys.exit(1)

    source = sys.argv[1]
    print_header()

    engine = RAGEngine()
    print(f"{DIM}Loading: {source}{RESET}")
    meta = load_source(engine, source)

    print(f"{GREEN}✓ Loaded{RESET} {meta['source']}")
    print(f"  {meta['word_count']:,} words · {meta['chunk_count']} chunks\n")

    run_repl(engine, meta["collection_id"])

    stats = engine.get_feedback_stats()
    if stats["total"] > 0:
        print(f"\n{DIM}Session feedback: {stats['good']}/{stats['total']} relevant ({stats['score']:.0%}){RESET}")


if __name__ == "__main__":
    main()
