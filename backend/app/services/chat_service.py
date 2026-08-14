import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_ollama import ChatOllama

from app.services.vector_store import search_schemes
from app.utils.parser import (
    extract_profile,
    find_matching_schemes,
    detect_language,
)


DATABASE_PATH = (
    Path(__file__).parent.parent / "database" / "schemes.json"
)


# ============================================================
# LLM
# ============================================================

llm = ChatOllama(
    model="phi3:latest",
    base_url="http://127.0.0.1:11434",
    temperature=0
)


# ============================================================
# DATABASE
# ============================================================

def load_schemes():
    with open(DATABASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# SCHEME CONTEXT
# ============================================================

def format_scheme_context(
    schemes: List[Dict[str, Any]]
) -> str:

    context_parts = []

    for index, scheme in enumerate(schemes, start=1):

        why_eligible = scheme.get(
            "why_eligible",
            []
        )

        if isinstance(why_eligible, list):

            reasons = "\n".join(
                f"- {reason}"
                for reason in why_eligible
            )

        else:

            reasons = f"- {why_eligible}"

        states = scheme.get(
            "states",
            []
        )

        if isinstance(states, list):
            states_text = ", ".join(states)
        else:
            states_text = str(states)

        context_parts.append(
            f"""
SCHEME {index}

Name: {scheme.get("name", "Not specified")}

Benefit: {scheme.get("benefit", "Not specified")}

Occupation: {scheme.get("occupation", "Not specified")}

Education: {scheme.get("education", "Not specified")}

Maximum Income: ₹{scheme.get("max_income", "Not specified")}

States: {states_text}

Verified Eligibility Reasons:
{reasons}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# COMPARISON
# ============================================================

def build_comparison(
    schemes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    comparison = []

    for scheme in schemes:

        comparison.append(
            {
                "id": scheme.get("id"),
                "name": scheme.get("name"),
                "benefit": scheme.get("benefit"),
                "occupation": scheme.get("occupation"),
                "education": scheme.get("education"),
                "max_income": scheme.get("max_income"),
                "states": scheme.get("states", []),
                "why_eligible": scheme.get(
                    "why_eligible",
                    []
                ),
                "application_url": scheme.get(
                    "application_url",
                    scheme.get("apply_url")
                )
            }
        )

    return comparison


# ============================================================
# BEST SCHEME
# ============================================================

def determine_best_scheme(
    schemes: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:

    if not schemes:
        return None

    candidates = []

    for scheme in schemes:

        benefit = str(
            scheme.get("benefit", "")
        ).lower()

        amounts = re.findall(
            r"(?:₹|rs\.?|inr)?\s*([\d,]+)",
            benefit,
            flags=re.IGNORECASE
        )

        values = []

        for amount in amounts:

            try:
                values.append(
                    int(
                        amount.replace(",", "")
                    )
                )

            except ValueError:
                pass

        if values:

            candidates.append(
                (
                    max(values),
                    scheme
                )
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return candidates[0][1]


# ============================================================
# FAST PROFILE ANALYSIS
# ============================================================

def analyze_profile(
    user_text: str
):

    profile = extract_profile(
        user_text
    )

    schemes = find_matching_schemes(
        profile
    )

    comparison = build_comparison(
        schemes
    )

    best_scheme = determine_best_scheme(
        schemes
    )

    return {
        "profile": profile,
        "eligible_schemes": schemes,
        "comparison": comparison,
        "best_scheme": best_scheme,
        "language": detect_language(
            user_text
        )
    }


# ============================================================
# AI RECOMMENDATION
# ============================================================

def generate_recommendation(
    user_text: str,
    profile: Dict[str, Any],
    schemes: List[Dict[str, Any]],
    best_scheme: Optional[Dict[str, Any]]
):

    if not schemes:

        return (
            "I could not find any eligible schemes "
            "for your profile in the available database."
        )

    language = detect_language(
        user_text
    )

    context = format_scheme_context(
        schemes
    )

    best_name = (
        best_scheme.get("name")
        if best_scheme
        else "No single best option"
    )

    best_benefit = (
        best_scheme.get("benefit")
        if best_scheme
        else "Not available"
    )

    prompt = f"""
You are SchemeSense AI.

Generate a SHORT recommendation using ONLY the verified
scheme information below.

USER PROFILE:
Age: {profile.get("age")}
Occupation: {profile.get("occupation")}
Education: {profile.get("education")}
State: {profile.get("state")}
Income: ₹{profile.get("income")}

NUMBER OF ELIGIBLE SCHEMES:
{len(schemes)}

VERIFIED SCHEMES:
{context}

BEST OPTION SELECTED BY PYTHON:
{best_name}

BENEFIT:
{best_benefit}

LANGUAGE:
{language}

STRICT RULES:

1. Mention ALL {len(schemes)} eligible schemes.
2. Do not add any scheme.
3. Do not remove any scheme.
4. Do not invent benefits.
5. Do not invent eligibility criteria.
6. Do not invent deadlines.
7. Do not invent documents.
8. Do not invent application procedures.
9. Do not invent government organizations.
10. Do not invent URLs.
11. Do not make unsupported assumptions.
12. Use the verified eligibility reasons supplied above.
13. Answer in the same language as the user's input.
14. Keep the answer concise.

FORMAT:

## Eligibility Summary

State the number of eligible schemes.

## Scheme Comparison

For every eligible scheme:

### Scheme Name

**Benefit:** exact benefit from the database.

**Why you're eligible:**
- verified reason
- verified reason

## Best Option

Mention the Python-selected best option and its exact stated benefit.

## Recommendation

Give one short recommendation based only on the database.

Return clean Markdown.
"""

    response = llm.invoke(
        prompt
    )

    return response.content


# ============================================================
# RAG CHAT
# ============================================================

def ask_llm(question: str):

    schemes = search_schemes(
        question
    )

    if not schemes:

        return (
            "I could not find that information in the "
            "available scheme database."
        )

    context = format_scheme_context(
        schemes
    )

    language = detect_language(
        question
    )

    prompt = f"""
You are SchemeSense AI.

Answer the user's question using ONLY the scheme data below.

RULES:

- Do not invent information.
- Do not guess.
- Do not invent benefits.
- Do not invent deadlines.
- Do not invent documents.
- Do not invent application procedures.
- Do not invent URLs.
- If information is unavailable, say so.
- Answer in the same language as the user.

LANGUAGE:
{language}

SCHEME DATA:
{context}

USER QUESTION:
{question}

Give a concise Markdown answer.
"""

    response = llm.invoke(
        prompt
    )

    return response.content


# ============================================================
# FOLLOW-UP CHAT
# ============================================================

def chat_with_user(
    question: str,
    profile: Optional[Dict[str, Any]] = None,
    eligible_schemes: Optional[List[Dict[str, Any]]] = None
):

    eligible_schemes = (
        eligible_schemes or []
    )

    if not eligible_schemes:
        return ask_llm(
            question
        )

    context = format_scheme_context(
        eligible_schemes
    )

    profile_text = ""

    if profile:

        profile_text = f"""
USER PROFILE:

Age: {profile.get("age")}
Occupation: {profile.get("occupation")}
Education: {profile.get("education")}
State: {profile.get("state")}
Income: ₹{profile.get("income")}
"""

    language = detect_language(
        question
    )

    prompt = f"""
You are the conversational assistant for SchemeSense AI.

{profile_text}

VERIFIED ELIGIBLE SCHEMES:

{context}

USER LANGUAGE:
{language}

STRICT RULES:

1. Answer only from the information above.
2. Do not invent facts.
3. Do not invent benefits.
4. Do not invent deadlines.
5. Do not invent documents.
6. Do not invent application procedures.
7. Do not invent URLs.
8. Do not assume missing information.
9. Answer in the same language as the user.
10. Keep the answer concise.

USER QUESTION:

{question}

ANSWER:
"""

    response = llm.invoke(
        prompt
    )

    return response.content


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def analyze_user(
    user_text: str
):

    # IMPORTANT:
    # This function does NOT call Phi-3.
    #
    # Therefore the frontend can receive the profile,
    # schemes and comparison almost immediately.

    return analyze_profile(
        user_text
    )