import argparse
import json
from pathlib import Path
from .config import Settings
from .runtime import build

def main():
    parser = argparse.ArgumentParser(description="Agricultural evidence assistant")
    parser.add_argument("question")
    parser.add_argument("--lexical", action="store_true", help="Explicit TF-IDF fallback, not semantic retrieval")
    parser.add_argument("--baseline", action="store_true", help="Disable hybrid rank fusion")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    settings = Settings.from_env()
    if args.lexical:
        from dataclasses import replace
        settings = replace(settings, backend="lexical", threshold=.05)
    agent = build(settings, persist=True)
    result = agent.run(args.question, hybrid=not args.baseline)
    print(result["answer"])
    print(json.dumps({k:result[k] for k in ["trace","verification","elapsed_ms","tool_calls"]}, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result["answer"], encoding="utf-8")

if __name__ == "__main__": main()
