from typing import Any, Dict, List

import streamlit as st

from frontend.components._helpers import get_severity_style


SEVERITY_ORDER = ["critical", "high", "medium", "low"]

# Below this many flagged issues, we lead with encouragement instead of
# letting a short list read as "feedback is missing/broken."
LOW_ISSUE_COUNT_THRESHOLD = 3


def _group_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {level: [] for level in SEVERITY_ORDER}
    for issue in issues:
        level = (issue.get("severity_level") or "low").lower()
        grouped.setdefault(level, []).append(issue)
    return grouped


def _render_issue(issue: Dict[str, Any]) -> None:
    icon, text_color, bg_color = get_severity_style(issue.get("severity_level"))
    title = issue.get("issue_title", "Untitled issue")
    impact = issue.get("ats_impact", "")
    explanation = issue.get("explanation", "")
    where = issue.get("where_it_appears", "")
    how_to_fix = issue.get("how_to_fix", "")
    action_items = issue.get("action_items") or []
    example = issue.get("example_improvement", "")

    st.markdown(
        f"""
        <div style="border-left:4px solid {text_color}; background-color:{bg_color};
                    padding:0.75rem 1rem; border-radius:6px; margin-bottom:0.5rem;">
            <strong style="color:{text_color};">{icon} {title}</strong>
            <span style="color:#666; margin-left:0.5rem; font-size:0.85rem;">{impact}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Details", expanded=False):
        if explanation:
            st.markdown(f"**What's happening:** {explanation}")
        if where:
            st.markdown(f"**Where it appears:** {where}")
        if how_to_fix:
            st.markdown(f"**How to fix:** {how_to_fix}")
        if action_items:
            st.markdown("**Action items:**")
            for item in action_items:
                st.markdown(f"- {item}")
        if example:
            st.markdown("**Example improvement:**")
            st.code(example, language="text")


def _intro_message(issue_count: int, has_high_severity: bool) -> str:
    """Short framing line shown above the issue list, scaled to how clean the resume is."""
    if issue_count == 0:
        return (
            "🎉 **Your resume looks great!** No issues were flagged in this analysis — "
            "it's already in strong shape against the checks we run."
        )
    if issue_count <= LOW_ISSUE_COUNT_THRESHOLD and not has_high_severity:
        return (
            "✅ **Your resume is in solid shape.** Only a couple of targeted "
            "improvements below — addressing these can push your score even higher."
        )
    return ""  # let the issue list speak for itself once there's real volume/severity


def display_detailed_feedback(analysis: Dict[str, Any]) -> None:
    issues = analysis.get("detailed_feedback") or []

    st.markdown("### 🔍 Detailed Feedback")

    grouped = _group_by_severity(issues)
    has_high_severity = bool(grouped.get("critical") or grouped.get("high"))

    intro = _intro_message(len(issues), has_high_severity)
    if intro:
        st.success(intro)

    if not issues:
        return  # nothing further to render — the success message above covers it

    st.caption(f"{len(issues)} issue(s) flagged — grouped by severity.")

    for level in SEVERITY_ORDER:
        items = grouped.get(level, [])
        if not items:
            continue
        st.markdown(f"#### {level.title()} ({len(items)})")
        for issue in items:
            _render_issue(issue)