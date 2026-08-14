import re
import spacy

nlp = spacy.load("en_core_web_sm")

STATES = [
    "Karnataka",
    "Gujarat",
    "Maharashtra",
    "Delhi",
    "Tamil Nadu",
    "Kerala",
    "Rajasthan",
    "Punjab",
    "Uttar Pradesh",
    "Bihar"
]

EDUCATION = {
    "engineering": "Engineering",
    "engineer": "Engineering",
    "btech": "Engineering",
    "b.tech": "Engineering",
    "mba": "MBA",
    "mba student": "MBA",
    "medical": "Medical",
    "doctor": "Medical"
}

OCCUPATIONS = {
    "student": "Student",
    "farmer": "Farmer",
    "labourer": "Labourer",
    "worker": "Worker",
    "businessman": "Business",
    "businesswoman": "Business",
    "unemployed": "Unemployed"
}


def parse_profile(text):
    doc = nlp(text)

    profile = {
        "age": None,
        "income": None,
        "state": None,
        "education": None,
        "occupation": None
    }

    # ---------------- Age ----------------
    age_match = re.search(r"\b(\d{1,2})\s*(years?|yrs?)?\s*old\b", text.lower())

    if age_match:
        profile["age"] = int(age_match.group(1))

    # ---------------- Income ----------------
    income_patterns = [
        r"(\d+(?:\.\d+)?)\s*lakh",
        r"income.*?(\d+)",
        r"salary.*?(\d+)"
    ]

    for pattern in income_patterns:
        match = re.search(pattern, text.lower())

        if match:
            value = float(match.group(1))

            if "lakh" in pattern:
                value *= 100000

            profile["income"] = int(value)
            break

    # ---------------- Named Entities ----------------
    for ent in doc.ents:

        if ent.label_ == "GPE":
            for state in STATES:
                if state.lower() == ent.text.lower():
                    profile["state"] = state

    # ---------------- Tokens ----------------
    for token in doc:

        word = token.text.lower()

        if word in EDUCATION:
            profile["education"] = EDUCATION[word]

        if word in OCCUPATIONS:
            profile["occupation"] = OCCUPATIONS[word]

    return profile