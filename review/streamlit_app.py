"""
Part 4, Phase H — minimal review view, sorted by lowest confidence.

Run with:
    streamlit run review/streamlit_app.py

This operationalizes "say when data is imperfect, don't hide it" — every
flagged field is visible with its reason, not buried in a log file.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from unihack.pipeline import run_pipeline  # noqa: E402
from unihack.part4_enrichment_qa.confidence import review_queue  # noqa: E402

st.set_page_config(page_title="UniHack — Review Queue", layout="wide")
st.title("Unilog Content Pipeline — Human Review Queue")
st.caption("Faucets category · sorted by lowest confidence first")

limit = st.sidebar.number_input("Rows to process", min_value=5, max_value=200, value=25, step=5)
run_button = st.sidebar.button("Run pipeline")

if run_button:
    with st.spinner(f"Processing {limit} rows..."):
        results = run_pipeline(limit=limit)
    st.session_state["results"] = results

results = st.session_state.get("results")

if not results:
    st.info("Set a row count and click **Run pipeline** in the sidebar to populate the review queue.")
else:
    flagged = review_queue(results)
    st.subheader(f"{len(flagged)} of {len(results)} rows flagged for review")

    for r in flagged:
        c = r.normalized_record.classified_record
        conf = r.overall_confidence or 0.0
        with st.expander(f"[{conf:.2f}] {c.input_row.mfg_part_num} — {c.input_row.part_desc[:60]}"):
            st.write(f"**Classpath:** {c.classification.classpath} (confidence {c.classification.confidence:.2f})")
            st.write(f"**Manufacturer:** {r.normalized_record.normalized_manufacturer or 'UNMATCHED'}")

            st.write("**Attributes**")
            for a in r.normalized_record.normalized_attributes + r.enriched_attributes:
                flag = " ⚠️ " + (a.review_reason or "") if a.needs_review else ""
                st.write(f"- {a.attribute}: {a.normalized_value or a.value}{flag}")

            if r.violations:
                st.write("**QA violations**")
                for v in r.violations:
                    st.write(f"- [{v.severity}] {v.type}: {v.field} — {v.issue}")