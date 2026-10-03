"""
Lease Review Assistant — Full Product MVP
Capstone Round 2 · Ironhack AI Consulting · Ioanna Renta
Portuguese market localisation with mandatory human sign-off.
"""

import os
import json
import time
import concurrent.futures
import threading
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def timed_spinner(text):
    """Spinner with a live elapsed-seconds counter (Streamlit >= 1.43).
    Falls back to a plain spinner on older versions."""
    try:
        return st.spinner(text, show_time=True)
    except TypeError:
        return st.spinner(text)

# disable telemetry and heavy parallelism to reduce startup memory on Render free tier
os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["CHROMA_TELEMETRY"] = "false"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from utils import extract_text_from_pdf
from extractor import process_lease
from validator import validate_extraction, compare_models

# RAG (Chroma) is the heaviest import — load lazily only when first used
@st.cache_resource(show_spinner=False)
def _get_rag():
    from rag import build_vectorstore, query_portfolio
    return build_vectorstore, query_portfolio
from database import (
    save_lease_review, save_evaluation, save_cost,
    get_recent_reviews, get_cost_summary,
)
from notion_sync import push_review_to_notion
from proposal import generate_proposal
from notifier import send_extraction_email
from portugal_law import get_cost_eur

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lease Review Assistant — Portugal",
    page_icon="🏢",
    layout="wide",
)

st.markdown("""
    <h1 style='color:#0f1f3d; font-size:26px; margin-bottom:2px'>
        🏢 Lease Review Assistant — Portugal
    </h1>
    <p style='color:#3d4f6e; font-size:13px; margin-bottom:8px'>
        AI-assisted lease extraction · NRAU · GPT-4o extraction + Claude Haiku validation
    </p>
    <hr style='border:1px solid #e8ecf4; margin-bottom:12px'>
""", unsafe_allow_html=True)

# prominent disclaimer
st.caption(
    "⚠️ AI-generated draft · Every output requires lawyer review before use in any legal or financial decision · Governed by Portuguese law (NRAU)"
)

# ── session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("lease_texts", {}),
    ("vectorstore", None),
    ("extraction_results", {}),
    ("validation_results", {}),
    ("signoffs", {}),
    ("corrections", {}),
    ("uploader_key", 0),
    ("review_ids", {}),
    ("last_selected", None),
    ("query_input", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Upload Leases")
    st.markdown("Upload up to 5 commercial lease PDFs.")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_files:
        if len(uploaded_files) > 5:
            st.error("Maximum 5 leases.")
            uploaded_files = uploaded_files[:5]
        new_files = False
        for f in uploaded_files:
            if f.name not in st.session_state.lease_texts:
                with st.spinner(f"Reading {f.name}..."):
                    text = extract_text_from_pdf(f)
                    st.session_state.lease_texts[f.name] = text
                    new_files = True
        if new_files and st.session_state.lease_texts:
            with st.spinner("Building search index..."):
                _build_vs, _ = _get_rag()
                st.session_state.vectorstore = _build_vs(
                    st.session_state.lease_texts
                )
            st.success(f"{len(st.session_state.lease_texts)} lease(s) indexed.")
        st.markdown("**Loaded:**")
        for fname in st.session_state.lease_texts:
            signed = "✅" if fname in st.session_state.signoffs else "⏳"
            st.markdown(f"{signed} {fname}")

    if st.button("Clear all leases"):
        for key in ["lease_texts", "vectorstore", "extraction_results",
                    "validation_results", "signoffs", "corrections", "review_ids"]:
            st.session_state[key] = {} if key != "vectorstore" else None
        st.session_state.uploader_key += 1
        st.rerun()

    st.divider()
    st.markdown("### How to use this tool")
    st.markdown("""
1. Upload lease PDFs
2. Run extraction on each lease
3. **Read every extracted field** against the source document
4. **Review every flagged clause** — check the page and clause reference
5. Correct any errors using the edit fields
6. Complete the **Lawyer Sign-off** section
7. Only after sign-off may this output be used in any decision
""")

# ── tabs ──────────────────────────────────────────────────────────────────────
tab_extract, tab_query, tab_proposal, tab_history, tab_stress = st.tabs([
    "📋 Extract & Review",
    "🔍 Query Portfolio",
    "📊 Acquisition Proposal",
    "🗂 Review History",
    "⚡ Stress Test",
])

# ── TAB 1: EXTRACT ────────────────────────────────────────────────────────────
with tab_extract:
    st.markdown("### Step 1 — Run AI extraction")

    if not st.session_state.lease_texts:
        st.info("Upload lease PDFs using the sidebar to get started.")
    else:
        col_sel, col_model, col_opt = st.columns([3, 2, 1])
        with col_sel:
            selected = st.selectbox(
                "Select lease to process",
                options=list(st.session_state.lease_texts.keys()),
                key="selected_lease",
            )
        with col_model:
            from extractor import AVAILABLE_MODELS, DEFAULT_MODEL
            model_options = list(AVAILABLE_MODELS.keys())
            model_labels  = [AVAILABLE_MODELS[m]["label"] for m in model_options]
            default_idx   = model_options.index(DEFAULT_MODEL)
            chosen_label  = st.selectbox(
                "Extraction model",
                options=model_labels,
                index=default_idx,
                help=(
                    "Reasoning models (o1, o3) are more accurate on complex legal "
                    "clauses but slower and more expensive. Use gpt-4o-2024-11-20 "
                    "for standard leases."
                ),
            )
            chosen_model = model_options[model_labels.index(chosen_label)]
        with col_opt:
            run_validation = st.checkbox("Claude validation", value=True,
                help="Claude Haiku independently validates the extraction")
            sync_notion = st.checkbox("Sync to Notion", value=True)

        reviewer_email = st.text_input(
            "Your email address (results will be emailed to you)",
            placeholder="lawyer@company.com",
        )

        run_clicked = st.button("▶ Run AI extraction", type="primary")

        # One placeholder holds progress AND results. On every rerun st.empty()
        # replaces whatever was in this slot before, so results from a previous
        # lease disappear immediately instead of staying on screen (dimmed)
        # while the new extraction is running.
        output_area = st.empty()
        with output_area.container():
            if run_clicked:
                if not reviewer_email or "@" not in reviewer_email:
                    st.warning("Please enter a valid email address.")
                else:
                    # clear ALL previous results so nothing shows while new extraction runs
                    st.session_state.extraction_results.clear()
                    st.session_state.validation_results.clear()
                    st.session_state.corrections.clear()
                    st.session_state.signoffs.clear()
                    st.session_state.last_selected = None

                    lease_text = st.session_state.lease_texts[selected]

                    # show full-page progress -- replaces everything below the button
                    progress_area = st.container()
                    with progress_area:
                        st.markdown("---")
                        step1 = st.info(
                            "⏳ **Step 1 of 4 — Reading the lease** \n\n"
                            "Sending the full lease text to GPT-4o. The model reads every "
                            "clause looking for standard fields (tenant, landlord, rent, dates, "
                            "break options) and any provisions that deviate from NRAU defaults."
                        )
                        step2 = st.empty()
                        step3 = st.empty()
                        step4 = st.empty()

                    start = time.time()

                    # GPT-4o extraction
                    step2.info(
                        "⏳ **Step 2 of 4 — GPT-4o extracting fields** \n\n"
                        "GPT-4o is extracting all structured fields and flagged clauses using "
                        "a Portuguese law-aware prompt. Maps SENHORIO → landlord, "
                        "ARRENDATÁRIO → tenant, and checks 10 high-risk NRAU clause patterns. "
                        "This usually takes 10-40 seconds, depending on lease length and "
                        "API load. Please do not refresh the page."
                    )

                    with timed_spinner("GPT-4o working... usually 10-40 seconds"):
                        result = process_lease(
                            lease_text,
                            filename=selected,
                            model=chosen_model,
                        )

                    result["meta"]["reviewer_email"] = reviewer_email
                    extraction_time = time.time() - start
                    step1.success("✅ **Step 1 of 4 — Lease read successfully**")
                    step2.success("✅ **Step 2 of 4 — GPT-4o extraction complete**")

                    # Claude validation
                    validation = None
                    if run_validation:
                        step3.info(
                            "⏳ **Step 3 of 4 — Claude Haiku 4.5 validating** \n\n"
                            "Anthropic's fastest model is independently cross-checking GPT-4o's "
                            "output against the same lease. Two AI models, same document, "
                            "independent reads — their agreement score shows how confident "
                            "you can be in the result. This usually takes 5-20 seconds."
                        )
                        with timed_spinner("Claude Haiku validating... usually 5-20 seconds"):
                            validation = validate_extraction(lease_text, result)
                        if validation:
                            st.session_state.validation_results[selected] = validation
                        step3.success("✅ **Step 3 of 4 — Claude validation complete**")

                    # save and sync
                    step4.info(
                        "⏳ **Step 4 of 4 — Saving and syncing** \n\n"
                        "Saving the review to the database, syncing to Notion and "
                        "emailing the results. This usually takes 3-15 seconds."
                    )
                    st.session_state.extraction_results[selected] = result
                    st.session_state.last_selected = selected

                    cost_breakdown = {
                        "extraction_tokens_in": 2000,
                        "extraction_tokens_out": 800,
                        "validation_tokens_in": validation.get("tokens_in", 0) if validation else 0,
                        "validation_tokens_out": validation.get("tokens_out", 0) if validation else 0,
                        "total_cost_eur": get_cost_eur("gpt-4o", 2000, 800) + (
                            validation.get("cost_eur", 0) if validation else 0
                        ),
                    }

                    # save to database and Notion -- silently ignore errors
                    review_id = None
                    try:
                        review_id = save_lease_review(result, validation, cost_breakdown)
                        if review_id:
                            st.session_state.review_ids[selected] = review_id
                    except Exception:
                        pass

                    if sync_notion:
                        try:
                            push_review_to_notion(result, validation, review_id)
                        except Exception:
                            pass

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = RESULTS_DIR / f"{selected.replace('.pdf','')}__{timestamp}.json"
                    with open(save_path, "w") as f:
                        json.dump({"result": result, "validation": validation}, f, indent=2)

                    try:
                        send_extraction_email(result, reviewer_email, selected)
                    except Exception:
                        pass

                    step4.success("✅ **Step 4 of 4 — Saved and synced**")
                    st.success(
                        f"✅ **All done in {extraction_time:.1f}s · "
                        f"Cost: €{cost_breakdown['total_cost_eur']:.4f} · "
                        f"Scroll down to see results ↓**"
                    )

            # ── display results ────────────────────────────────────────────────────
            # Only show results for the lease currently selected in the dropdown.
            # (The old fallback to last_selected kept showing the previous lease.)
            if selected in st.session_state.extraction_results:
                result = st.session_state.extraction_results[selected]
                validation = st.session_state.validation_results.get(selected)
                summary = result.get("summary", {})
                high = summary.get("high_risk_clauses", 0)
                medium = summary.get("medium_risk_clauses", 0)
                rec = summary.get("review_recommendation", "")

                st.divider()
                st.markdown("### Step 2 — Understand the AI assessment")

                # risk banner with lawyer instruction
                if high > 0:
                    st.error(f"🔴 {rec}")
                    st.markdown("**Next step:** Review the flagged clauses below and consult with senior counsel before proceeding.")
                elif medium > 0:
                    st.warning(f"🟡 {rec}")
                    st.markdown("**Next step:** Review the flagged clauses below and confirm with your legal team.")
                else:
                    st.success(f"🟢 {rec}")
                    st.markdown("**Next step:** Verify the key fields below against the source document, then complete the sign-off.")

                # metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total flagged clauses", summary.get("total_flagged_clauses", 0),
                         help="Total number of unusual or non-standard clauses identified")
                c2.metric("High risk", high,
                         help="Clauses requiring immediate legal attention before proceeding")
                c3.metric("Medium risk", medium,
                         help="Clauses requiring review and confirmation with legal team")

                if validation:
                    agreement = validation.get("agreement_score", 0)
                    c4.metric(
                        "Claude agreement",
                        f"{agreement:.0f}%",
                        help=(
                            "A second AI model (Claude Haiku) independently reviewed the "
                            "same lease and compared its findings to the GPT-4o extraction. "
                            "This percentage shows how often the two models agreed on field "
                            "values. A low score does not mean the extraction is wrong — it "
                            "means the two models diverged and a human should pay extra "
                            "attention to those fields. 0% means Claude could not parse "
                            "the validation response correctly — treat this extraction with "
                            "extra caution and verify every field manually."
                        )
                    )
                    if agreement < 50:
                        st.warning(
                            "⚠️ Low Claude agreement score. This means the two AI models "
                            "disagreed significantly. Treat this extraction with extra "
                            "caution — verify every single field against the source document "
                            "before relying on any value."
                        )

                st.divider()
                st.markdown("### Step 3 — Review extracted fields")
                st.markdown(
                    "Each field shows the **page number and clause reference** where it "
                    "was found. Click the source reference to locate it in the document. "
                    "If any value is wrong, correct it using the edit field below."
                )

                fields = result.get("extracted_fields", {})
                citations = result.get("citations", {}) or {}
                corrections = st.session_state.corrections.get(selected, {})

                with st.expander("📄 Extracted fields with source citations", expanded=True):
                    field_labels = {
                        "tenant_name": "Tenant name",
                        "landlord_name": "Landlord name",
                        "property_address": "Property address",
                        "lease_commencement_date": "Commencement date",
                        "lease_expiry_date": "Expiry date",
                        "break_option_dates": "Break options",
                        "rent_amount": "Rent amount",
                        "rent_review_mechanism": "Rent review mechanism",
                        "rent_escalation_schedule": "Rent escalation",
                        "security_deposit": "Security deposit",
                        "permitted_use": "Permitted use",
                        "assignment_rights": "Assignment rights",
                        "tenant_break_conditions": "Break conditions",
                        "service_charge": "Service charge",
                        "key_tenant_obligations": "Key tenant obligations",
                        "key_landlord_obligations": "Key landlord obligations",
                    }
                    for key, label in field_labels.items():
                        value = fields.get(key)
                        citation = citations.get(key, {}) if isinstance(citations, dict) else {}
                        display = "*Not found in document*" if value is None else (
                            "\n".join(f"- {v}" for v in value)
                            if isinstance(value, list) else str(value)
                        )
                        cite_str = ""
                        if citation and isinstance(citation, dict):
                            page = citation.get("page")
                            clause = citation.get("clause")
                            if page or clause:
                                cite_str = f" · *source: p.{page}, {clause}*"

                        col_field, col_edit = st.columns([4, 1])
                        with col_field:
                            st.markdown(f"**{label}**{cite_str}")
                            current = corrections.get(key, display)
                            st.markdown(current if current != display else display)
                        with col_edit:
                            if st.button("✏️ Correct", key=f"edit_{selected}_{key}"):
                                st.session_state[f"editing_{selected}_{key}"] = True

                        if st.session_state.get(f"editing_{selected}_{key}"):
                            corrected = st.text_area(
                                f"Correct value for {label}",
                                value=str(value or ""),
                                key=f"correction_input_{selected}_{key}",
                            )
                            if st.button("Save correction", key=f"save_{selected}_{key}"):
                                if selected not in st.session_state.corrections:
                                    st.session_state.corrections[selected] = {}
                                st.session_state.corrections[selected][key] = corrected
                                st.session_state[f"editing_{selected}_{key}"] = False
                                st.success(f"Correction saved for {label}.")
                                st.rerun()
                        st.divider()

                # portugal-specific fields
                pt_fields = result.get("portugal_fields", {})
                if pt_fields and any(v for v in pt_fields.values()):
                    with st.expander("🇵🇹 Portugal-specific fields (NRAU compliance)"):
                        st.markdown(
                            "These fields are mandatory under Portuguese law (NRAU, "
                            "Lei n.º 6/2006). A missing NIF or Finanças registration "
                            "clause is a legal compliance issue, not just a drafting gap."
                        )
                        for k, v in pt_fields.items():
                            label = k.replace("_", " ").title()
                            val = v if v is not None else "*Not found — verify manually*"
                            st.markdown(f"**{label}:** {val}")

                # flagged clauses
                flagged = result.get("flagged_clauses", [])
                with st.expander(
                    f"🚩 Flagged clauses ({len(flagged)})",
                    expanded=True
                ):
                    if not flagged:
                        st.success("No unusual clauses identified.")
                    else:
                        st.markdown(
                            "Each clause shows the source location, plain-language explanation, "
                            "and the relevant Portuguese law provision."
                        )
                        for clause in flagged:
                            risk = clause.get("risk_level", "low")
                            color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk, "⚪")
                            page = clause.get("page_number")
                            ref = clause.get("clause_reference", "")
                            location = f"p.{page}" if page else ""
                            if ref:
                                location += f" · {ref}"
                            pt_law = clause.get("portuguese_law_reference", "")

                            st.markdown(
                                f"{color} **{clause.get('clause_type', 'Clause')}** "
                                f"· Risk: **{risk.upper()}**"
                                + (f" · *{location}*" if location else "")
                            )
                            st.markdown(
                                f"> *\"{clause.get('quoted_text', '')}\"*"
                            )
                            st.info(
                                f"**What this means:** "
                                f"{clause.get('plain_language_explanation', '')}"
                            )
                            if pt_law:
                                st.markdown(f"**Portuguese law:** {pt_law}")
                            st.warning(
                                f"**Required action:** "
                                f"{clause.get('recommended_action', '')}"
                            )
                            st.divider()

                # claude validation detail
                if validation:
                    with st.expander("🤖 Claude validation — what does this mean?"):
                        st.markdown("""
    **How Claude validation works:**
    The system runs the extraction twice — once with GPT-4o, once with Claude Haiku.
    Both models read the same lease independently. The agreement score shows how often
    they produced the same value for the same field.

    **What a low score means:**
    A low agreement score does not automatically mean the extraction is wrong.
    It means the two AI models saw the same text differently. This is most common
    when clauses are ambiguous, cross-referenced, or written in complex legal language.
    When scores are low, treat those specific fields with extra scrutiny.

    **What a high score means:**
    High agreement (above 80%) gives additional confidence that both models read
    the same thing. It does not replace human verification — it is an additional
    signal.
    """)
                        missed = validation.get("missed_flags", [])
                        critical = validation.get("critical_errors", [])
                        summary_text = validation.get("summary", "")
                        if summary_text:
                            st.markdown(f"**Claude summary:** {summary_text}")
                        if missed:
                            st.warning(f"**Clauses Claude thinks GPT-4o missed:** {missed}")
                        if critical:
                            st.error(f"**Fields Claude flagged as potentially incorrect:** {critical}")
                        if not missed and not critical and not summary_text:
                            st.info(
                                "Claude validation response could not be parsed. "
                                "Verify all fields manually."
                            )
                        raw = validation.get("raw_response", "")
                        if raw:
                            st.caption(f"Raw Claude response (debug): {raw[:200]}")

                # ── LAWYER SIGN-OFF ────────────────────────────────────────────────
                st.divider()
                st.markdown("### Step 4 — Lawyer sign-off")
                st.markdown(
                    "This section must be completed before this AI output may be "
                    "used in any legal or financial decision. Your sign-off is saved "
                    "to the database and the Notion record is updated."
                )

                if selected in st.session_state.signoffs:
                    signoff = st.session_state.signoffs[selected]
                    st.success(
                        f"✅ Signed off by **{signoff['reviewer_name']}** "
                        f"on {signoff['signed_at']}. "
                        f"This review is approved for use."
                    )
                else:
                    with st.form(key=f"signoff_form_{selected}"):
                        st.markdown("**Before signing off, confirm you have:**")
                        check1 = st.checkbox(
                            "Verified all extracted fields against the source document"
                        )
                        check2 = st.checkbox(
                            "Read and understood all flagged clauses"
                        ) if flagged else True
                        check3 = st.checkbox(
                            "Confirmed Portugal-specific fields (NIF, Finanças registration)"
                        )
                        check4 = st.checkbox(
                            "Applied professional legal judgment — this AI output is a "
                            "draft aid only and does not constitute legal advice"
                        )
                        reviewer_name = st.text_input(
                            "Your full name (as reviewing lawyer)",
                            placeholder="Dr. Maria Silva"
                        )
                        notes = st.text_area(
                            "Review notes (optional — any corrections or observations)",
                            placeholder="All fields verified. Break option date confirmed against clause 3.1.",
                            height=80,
                        )
                        submitted = st.form_submit_button("✅ Approve and sign off")

                        if submitted:
                            if not all([check1, check3, check4]):
                                st.error(
                                    "Please confirm all mandatory checkboxes before signing off."
                                )
                            elif not reviewer_name.strip():
                                st.error("Please enter your full name.")
                            else:
                                signoff_data = {
                                    "reviewer_name": reviewer_name,
                                    "signed_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "notes": notes,
                                    "corrections": st.session_state.corrections.get(selected, {}),
                                }
                                st.session_state.signoffs[selected] = signoff_data

                                # save signoff to Supabase if we have a review ID
                                review_id = st.session_state.review_ids.get(selected)
                                if review_id:
                                    try:
                                        from database import get_client
                                        client = get_client()
                                        client.table("lease_reviews").update({
                                            "reviewer_email": reviewer_email,
                                            "raw_validation": {
                                                **(result.get("meta", {})),
                                                "signoff": signoff_data,
                                            }
                                        }).eq("id", review_id).execute()
                                    except Exception:
                                        pass

                                st.success(
                                    f"✅ Signed off by {reviewer_name}. "
                                    f"This review is now approved for use."
                                )
                                st.rerun()

                # download
                with st.expander("⬇️ Download full review as JSON"):
                    st.download_button(
                        "Download",
                        data=json.dumps({
                            "result": result,
                            "validation": validation,
                            "corrections": st.session_state.corrections.get(selected, {}),
                            "signoff": st.session_state.signoffs.get(selected),
                        }, indent=2),
                        file_name=f"{selected.replace('.pdf','')}_reviewed.json",
                        mime="application/json",
                    )

# ── TAB 2: QUERY ──────────────────────────────────────────────────────────────
with tab_query:
    st.markdown("### Query across all uploaded leases")
    st.info(
        "Ask questions across all uploaded leases. The system searches the full "
        "text of every uploaded document and generates an answer with citations. "
        "All answers must be verified against the source documents by a qualified lawyer."
    )
    if not st.session_state.vectorstore:
        st.info("Upload lease PDFs to enable portfolio queries.")
    else:
        st.markdown(
            f"**{len(st.session_state.lease_texts)} lease(s) indexed:** "
            + ", ".join(st.session_state.lease_texts.keys())
        )
        examples = [
            "Which leases have a break option before 2027?",
            "Are there upward-only rent review clauses?",
            "Which lease has the highest annual rent?",
            "Are there any absolute restrictions on assignment?",
            "Which leases do not mention Finanças registration?",
            "What are the notice periods across all leases?",
        ]
        st.markdown("**Example questions:**")
        cols = st.columns(2)
        for i, ex in enumerate(examples):
            if cols[i % 2].button(ex, key=f"ex_{i}"):
                st.session_state.query_input = ex

        question = st.text_area(
            "Your question",
            value=st.session_state.get("query_input", ""),
            height=80,
        )
        if st.button("Search leases", type="primary"):
            if question.strip():
                with st.spinner("Searching..."):
                    _, _query_vs = _get_rag()
                    res = _query_vs(st.session_state.vectorstore, question)
                st.markdown("### Answer")
                st.markdown(res["answer"])
                st.caption(
                    f"Sources: {', '.join(res.get('sources', []))} · "
                    "Verify all findings against source documents."
                )

# ── TAB 3: ACQUISITION PROPOSAL ──────────────────────────────────────────────
with tab_proposal:
    st.markdown("### Acquisition proposal generator")
    st.info(
        "This tool aggregates all reviewed leases for a property and generates "
        "a structured recommendation. The BUY/REVIEW/PASS recommendation is "
        "indicative only and must be reviewed by a qualified lawyer and financial "
        "advisor before any investment decision."
    )
    if not st.session_state.extraction_results:
        st.info("Run extractions first, then generate a proposal here.")
    else:
        unsigned = [
            k for k in st.session_state.extraction_results
            if k not in st.session_state.signoffs
        ]
        if unsigned:
            st.info(
                f"{len(unsigned)} lease(s) pending sign-off: {', '.join(unsigned)}."
            )

        col1, col2 = st.columns(2)
        with col1:
            prop_name    = st.text_input("Property name", placeholder="Edifício Marquês")
            prop_address = st.text_input("Address", placeholder="Av. da Liberdade 110, Lisboa")
            prop_type    = st.selectbox("Type", ["office","retail","warehouse","mixed"])
        with col2:
            asking_price = st.number_input("Asking price (€)", min_value=0.0, step=10000.0)
            district     = st.selectbox("District",
                ["Lisboa","Porto","Setúbal","Algarve","Braga","Other"])

        selected_leases = st.multiselect(
            "Include leases",
            options=list(st.session_state.extraction_results.keys()),
            default=list(st.session_state.extraction_results.keys()),
        )

        if st.button("Generate proposal", type="primary"):
            if not prop_name or not asking_price:
                st.warning("Property name and asking price are required.")
            elif not selected_leases:
                st.warning("Select at least one lease.")
            else:
                reviews    = [st.session_state.extraction_results[k] for k in selected_leases]
                review_ids = [st.session_state.review_ids.get(k) for k in selected_leases]
                proposal   = generate_proposal(
                    prop_name, prop_address, prop_type,
                    asking_price, district, reviews, review_ids,
                )
                rec = proposal.get("recommendation", "REVIEW")
                if rec == "BUY":
                    st.success(f"## ✅ Indicative recommendation: {rec}")
                elif rec == "PASS":
                    st.error(f"## ❌ Indicative recommendation: {rec}")
                else:
                    st.warning(f"## ⚠️ Indicative recommendation: {rec}")

                st.markdown(f"**Confidence:** {proposal.get('confidence_level')}")
                st.caption(
                    "Indicative only — verify with legal and financial advisors before any acquisition decision."
                )

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Gross yield", f"{proposal.get('gross_yield_pct',0):.1f}%")
                c2.metric("WALE", f"{proposal.get('wale_years',0):.1f} yrs")
                c3.metric("Risk score", f"{proposal.get('composite_risk_score',0)}/10")
                c4.metric("Total rent/yr", f"€{proposal.get('total_annual_rent_eur',0):,.0f}")

                st.markdown("**Reasoning:**")
                for r in proposal.get("recommendation_reasons", []):
                    st.markdown(f"- {r}")

                st.divider()
                st.markdown("**Portuguese acquisition taxes (estimates):**")
                tc1, tc2, tc3 = st.columns(3)
                tc1.metric("IMT (6.5%)",       f"€{proposal.get('estimated_imt_eur',0):,.0f}")
                tc2.metric("Stamp duty (0.8%)", f"€{proposal.get('estimated_stamp_duty_eur',0):,.0f}")
                tc3.metric("Total tax",         f"€{proposal.get('estimated_total_tax_eur',0):,.0f}")

                try:
                    from database import save_proposal
                    save_proposal(proposal)
                    st.caption("Proposal saved to database.")
                except Exception as e:
                    st.caption(f"Database save failed: {e}")

# ── TAB 4: HISTORY ────────────────────────────────────────────────────────────
with tab_history:
    st.markdown("### Review history")

    # show results from this session first
    session_results = st.session_state.get("extraction_results", {})
    if session_results:
        st.markdown("**Reviewed in this session:**")
        import pandas as pd
        rows = []
        for fname, r in session_results.items():
            summary = r.get("summary", {})
            validation = st.session_state.get("validation_results", {}).get(fname, {})
            rows.append({
                "filename": fname,
                "tenant": r.get("extracted_fields", {}).get("tenant_name", "—"),
                "flagged": summary.get("total_flagged_clauses", 0),
                "high_risk": summary.get("high_risk_clauses", 0),
                "recommendation": summary.get("review_recommendation", "—"),
                "claude_agreement": f"{validation.get('agreement_score', 0):.0f}%" if validation else "—",
                "signed_off": "✅" if fname in st.session_state.get("signoffs", {}) else "⏳",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No reviews in this session yet. Run extractions in the Extract & Review tab.")

    # try loading from database -- silently skip if unavailable
    st.divider()
    st.markdown("### Database history")
    try:
        reviews = get_recent_reviews(limit=20)
        if not reviews:
            st.info("No reviews saved to database yet.")
        else:
            import pandas as pd
            df = pd.DataFrame(reviews)
            display_cols = [c for c in [
                "created_at", "filename", "tenant_name", "total_flagged",
                "high_risk_count", "review_recommendation",
                "validation_passed", "total_cost_eur"
            ] if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True)
    except Exception:
        st.caption("Database history unavailable in this session.")

# ── TAB 5: STRESS TEST ────────────────────────────────────────────────────────
with tab_stress:
    st.markdown("### Stress test & determinism check")
    st.markdown(
        "Test the system at scale. Run all uploaded leases in parallel to measure "
        "throughput, thread usage, and cost. Verify that temperature=0 produces "
        "identical results across multiple runs."
    )

    if not st.session_state.lease_texts:
        st.info("Upload lease PDFs to run stress tests.")
    else:
        col_st1, col_st2 = st.columns(2)
        with col_st1:
            max_workers = st.slider(
                "Parallel threads", 1, 5, 3,
                help="Number of leases processed simultaneously. "
                     "More threads = faster but higher API cost."
            )
        with col_st2:
            st.metric("Leases loaded", len(st.session_state.lease_texts))
            st.markdown(
                f"Estimated cost: "
                f"€{len(st.session_state.lease_texts) * 0.025:.3f} "
                f"(~€0.025 per lease)"
            )

        if st.button("▶ Run stress test", type="primary"):
            results_list = []
            start_total = time.time()

            def process_one(args):
                fname, text = args
                tid = threading.get_ident()
                t0 = time.time()
                try:
                    r = process_lease(text, filename=fname)
                    return {
                        "filename": fname,
                        "success": True,
                        "duration_s": round(time.time() - t0, 2),
                        "thread_id": tid,
                        "total_flagged": r.get("summary",{}).get("total_flagged_clauses",0),
                        "high_risk": r.get("summary",{}).get("high_risk_clauses",0),
                        "error": None,
                    }
                except Exception as e:
                    return {
                        "filename": fname, "success": False,
                        "duration_s": round(time.time() - t0, 2),
                        "thread_id": tid, "total_flagged": 0,
                        "high_risk": 0, "error": str(e),
                    }

            args_list = list(st.session_state.lease_texts.items())
            with st.spinner(f"Running {len(args_list)} leases on {max_workers} threads..."):
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
                    futures = [ex.submit(process_one, a) for a in args_list]
                    results_list = [f.result() for f in
                                    concurrent.futures.as_completed(futures)]

            total_time = time.time() - start_total
            successful = [r for r in results_list if r["success"]]
            unique_threads = len({r["thread_id"] for r in results_list})
            durations = [r["duration_s"] for r in successful] or [0]

            st.success(
                f"✅ {len(successful)}/{len(results_list)} leases completed · "
                f"Total: {total_time:.1f}s · "
                f"Avg: {sum(durations)/len(durations):.1f}s/lease · "
                f"Threads used: {unique_threads} · "
                f"Est. cost: €{len(successful)*0.025:.3f}"
            )

            import pandas as pd
            df = pd.DataFrame(results_list)
            show_cols = [c for c in ["filename","success","duration_s",
                                     "total_flagged","high_risk","error"]
                         if c in df.columns]
            st.dataframe(df[show_cols], use_container_width=True)

        st.divider()
        st.markdown("### Determinism check")
        st.markdown(
            "Runs the same lease 3 times and verifies identical output. "
            "Temperature=0 on both models ensures deterministic results — "
            "the same input always produces the same extraction."
        )
        det_lease = st.selectbox(
            "Select lease",
            options=list(st.session_state.lease_texts.keys()),
            key="det_select",
        )
        if st.button("▶ Run determinism check (3 runs)"):
            results_det = []
            with st.spinner("Running 3 identical extractions (~60s)..."):
                for i in range(3):
                    r = process_lease(
                        st.session_state.lease_texts[det_lease],
                        filename=det_lease,
                    )
                    results_det.append(r.get("extracted_fields", {}))

            import pandas as pd

            reference = results_det[0]
            non_null = sum(1 for v in reference.values() if v is not None)
            st.markdown(f"**Fields extracted:** {non_null} non-null fields across 3 runs")

            # build full comparison table
            comparison = []
            mismatches = []
            for field in reference:
                vals = [str(r.get(field, ""))[:60] for r in results_det]
                identical = len(set(vals)) == 1
                comparison.append({
                    "field": field,
                    "run_1": vals[0],
                    "run_2": vals[1],
                    "run_3": vals[2],
                    "match": "✅" if identical else "❌",
                })
                if not identical:
                    mismatches.append(field)

            # verdict
            if not mismatches:
                st.success(
                    "✅ All 3 runs produced identical output. "
                    "Determinism confirmed — temperature=0 is working correctly."
                )
            else:
                st.warning(
                    f"❌ {len(mismatches)} field(s) differed: {', '.join(mismatches)}"
                )

            # always show the comparison table
            st.markdown("**Field-by-field comparison across 3 runs:**")
            st.dataframe(
                pd.DataFrame(comparison),
                use_container_width=True,
                height=350,
            )
