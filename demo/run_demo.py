"""
Part 4, Phase J — the live demo. Runs ONE row end-to-end and narrates
every stage, then prints the evaluation summary table.

Run with:
    python demo/run_demo.py
    python demo/run_demo.py --row-index 0
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from unihack.pipeline import run_pipeline  # noqa: E402
from unihack.part4_enrichment_qa.packaging import narrate_record, scope_pitch_notes  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--row-index", type=int, default=0)
    parser.add_argument("--n-rows-for-eval", type=int, default=25,
                         help="How many rows to run for the evaluation summary.")
    args = parser.parse_args()

    print("=" * 70)
    print("UniHack — Unilog Product Content Enrichment — Live Demo")
    print("=" * 70)

    results = run_pipeline(limit=max(args.row_index + 1, args.n_rows_for_eval))

    print("\n--- ONE ROW, END TO END ---\n")
    print(narrate_record(results[args.row_index]))

    print("\n--- SCOPE NOTES ---\n")
    print(scope_pitch_notes())

    print(f"\n--- SUMMARY ({len(results)} rows processed) ---")
    flagged = sum(r.needs_review for r in results)
    print(f"Flagged for review: {flagged}/{len(results)} ({flagged / len(results):.1%})")


if __name__ == "__main__":
    main()