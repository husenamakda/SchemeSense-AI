import json
import re
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

DATABASE_PATH = (
    Path(__file__).parent.parent / "database" / "schemes.json"
)


def load_schemes():
    with open(DATABASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize text without removing Indian-language characters.
    """

    text = text.lower().strip()

    # Normalize different dash characters
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Normalize non-breaking spaces
    text = text.replace("\u00a0", " ")

    # Collapse repeated spaces
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(text: str) -> str:
    """
    Lightweight script-based language detection.

    Returns:
        English
        Hindi
        Kannada
        Gujarati
        Tamil
        Malayalam
        Mixed
    """

    counts = {
        "Hindi": 0,
        "Kannada": 0,
        "Gujarati": 0,
        "Tamil": 0,
        "Malayalam": 0,
        "English": 0,
    }

    for char in text:

        code = ord(char)

        # Devanagari
        if 0x0900 <= code <= 0x097F:
            counts["Hindi"] += 1

        # Kannada
        elif 0x0C80 <= code <= 0x0CFF:
            counts["Kannada"] += 1

        # Gujarati
        elif 0x0A80 <= code <= 0x0AFF:
            counts["Gujarati"] += 1

        # Tamil
        elif 0x0B80 <= code <= 0x0BFF:
            counts["Tamil"] += 1

        # Malayalam
        elif 0x0D00 <= code <= 0x0D7F:
            counts["Malayalam"] += 1

        # Basic English alphabet
        elif (
            "a" <= char.lower() <= "z"
        ):
            counts["English"] += 1

    # Remove zero values
    active_languages = [
        language
        for language, count in counts.items()
        if count > 0
    ]

    if not active_languages:
        return "English"

    # If multiple scripts are present
    if len(active_languages) > 1:

        # If English is combined with one Indian language,
        # consider the Indian language as the main language.
        indian_languages = [
            language
            for language in active_languages
            if language != "English"
        ]

        if len(indian_languages) == 1:
            return indian_languages[0]

        return "Mixed"

    return active_languages[0]


# ============================================================
# AGE EXTRACTION
# ============================================================

def extract_age(text: str):
    """
    Extract age from English and Indian-language sentences.
    """

    # --------------------------------------------------------
    # Explicit age patterns
    # --------------------------------------------------------

    age_patterns = [

        # English
        r"\b(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|year\s*old)\b",
        r"\bage\s*(?:is|of)?\s*(\d{1,3})\b",

        # Hindi
        r"(\d{1,3})\s*(?:साल|वर्ष)\s*(?:का|की|के)?",
        r"(?:उम्र|आयु)\s*(?:है|की)?\s*(\d{1,3})",

        # Kannada
        r"(\d{1,3})\s*(?:ವರ್ಷ|ವರ್ಷದ)\s*(?:ವಯಸ್ಸಿನ|ವಯಸ್ಸಿನವನು|ವಯಸ್ಸಿನವಳು)?",
        r"(?:ವಯಸ್ಸು|ವಯಸ್ಸಿನ)\s*(?:\d{1,3})",

        # Gujarati
        r"(\d{1,3})\s*(?:વર્ષ|વર્ષનો|વર્ષની)\s*",
        r"(?:ઉંમર|વય)\s*(?:\d{1,3})",

        # Tamil
        r"(\d{1,3})\s*(?:வயது|வயதுடைய)",
        r"(?:வயது)\s*(?:\d{1,3})",

        # Malayalam
        r"(\d{1,3})\s*(?:വയസ്സുള്ള|വയസ്സ്)",
        r"(?:പ്രായം)\s*(?:\d{1,3})",
    ]

    for pattern in age_patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            # Find the first number in the matched text
            numbers = re.findall(
                r"\d{1,3}",
                match.group(0)
            )

            if numbers:

                age = int(numbers[0])

                if 1 <= age <= 100:
                    return age

    # --------------------------------------------------------
    # Fallback:
    # Find a reasonable age number.
    #
    # We deliberately avoid numbers > 100 because those
    # are likely to be income values.
    # --------------------------------------------------------

    numbers = re.findall(r"\b\d{1,3}\b", text)

    for number in numbers:

        value = int(number)

        if 15 <= value <= 100:
            return value

    return None


# ============================================================
# INCOME EXTRACTION
# ============================================================

def extract_income(text: str):
    """
    Extract annual/family income.

    Supports:
        300000
        3,00,000
        3 lakh
        3 lakhs
        ₹300000
        Rs 300000
        रुपये 300000
        ರೂಪಾಯಿ 300000
        રૂપિયા 300000
        ரூபாய் 300000
    """

    clean_text = text.lower()

    # --------------------------------------------------------
    # Lakh format
    # --------------------------------------------------------

    lakh_patterns = [
        r"(\d+(?:\.\d+)?)\s*lakh(?:s)?",
        r"(\d+(?:\.\d+)?)\s*lac(?:s)?",
        r"(\d+(?:\.\d+)?)\s*लाख",
        r"(\d+(?:\.\d+)?)\s*ಲಕ್ಷ",
        r"(\d+(?:\.\d+)?)\s*લાખ",
        r"(\d+(?:\.\d+)?)\s*லட்சம்",
        r"(\d+(?:\.\d+)?)\s*ലക്ഷം",
    ]

    for pattern in lakh_patterns:

        match = re.search(
            pattern,
            clean_text,
            flags=re.IGNORECASE
        )

        if match:

            value = float(match.group(1))

            return int(value * 100000)

    # --------------------------------------------------------
    # Explicit currency / income patterns
    # --------------------------------------------------------

    income_patterns = [

        # English
        r"(?:income|annual income|family income|yearly income)"
        r"\s*(?:is|of|:)?\s*₹?\s*([\d,]+)",

        # Hindi
        r"(?:आय|वार्षिक आय|परिवार की आय|सालाना आय)"
        r"\s*(?:है|:)?\s*₹?\s*([\d,]+)",

        # Kannada
        r"(?:ಆದಾಯ|ವಾರ್ಷಿಕ ಆದಾಯ|ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ)"
        r"\s*(?:ವು|ಆಗಿದೆ|:)?\s*₹?\s*([\d,]+)",

        # Gujarati
        r"(?:આવક|વાર્ષિક આવક|પરિવારની વાર્ષિક આવક)"
        r"\s*(?:છે|:)?\s*₹?\s*([\d,]+)",

        # Tamil
        r"(?:வருமானம்|ஆண்டு வருமானம்|குடும்ப ஆண்டு வருமானம்)"
        r"\s*(?:ஆகும்|:)?\s*₹?\s*([\d,]+)",

        # Malayalam
        r"(?:വരുമാനം|വാർഷിക വരുമാനം|കുടുംബ വാർഷിക വരുമാനം)"
        r"\s*(?:ആണ്|:)?\s*₹?\s*([\d,]+)",
    ]

    for pattern in income_patterns:

        match = re.search(
            pattern,
            clean_text,
            flags=re.IGNORECASE
        )

        if match:

            value = match.group(1)

            value = value.replace(",", "")

            try:
                return int(value)
            except ValueError:
                pass

    # --------------------------------------------------------
    # Currency-based fallback
    # --------------------------------------------------------

    currency_patterns = [
        r"₹\s*([\d,]+)",
        r"rs\.?\s*([\d,]+)",
        r"rupees?\s*([\d,]+)",
        r"रुपये\s*([\d,]+)",
        r"रुपए\s*([\d,]+)",
        r"रुपये\s*([\d,]+)",
        r"ರೂಪಾಯಿ\s*([\d,]+)",
        r"ರೂ\s*([\d,]+)",
        r"રૂપિયા\s*([\d,]+)",
        r"ரூபாய்\s*([\d,]+)",
        r"ரூ\s*([\d,]+)",
        r"രൂപ\s*([\d,]+)",
    ]

    for pattern in currency_patterns:

        match = re.search(
            pattern,
            clean_text,
            flags=re.IGNORECASE
        )

        if match:

            value = match.group(1).replace(",", "")

            try:
                number = int(value)

                if number >= 1000:
                    return number

            except ValueError:
                pass

    # --------------------------------------------------------
    # Final numeric fallback
    # --------------------------------------------------------

    numbers = re.findall(
        r"\d[\d,]*",
        clean_text
    )

    candidates = []

    for number in numbers:

        number = number.replace(",", "")

        try:
            value = int(number)

            # Income is normally much larger than age.
            if value >= 1000:
                candidates.append(value)

        except ValueError:
            continue

    if candidates:
        return max(candidates)

    return None


# ============================================================
# OCCUPATION EXTRACTION
# ============================================================

def extract_occupation(text: str):
    """
    Normalize occupation into the English values expected
    by schemes.json.
    """

    text = text.lower()

    occupation_keywords = {

        "Student": [

            # English
            "student",
            "students",

            # Hindi
            "छात्र",
            "छात्रा",
            "विद्यार्थी",

            # Kannada
            "ವಿದ್ಯಾರ್ಥಿ",
            "ವಿದ್ಯಾರ್ಥಿನಿ",

            # Gujarati
            "વિદ્યાર્થી",
            "વિદ્યાર્થિની",

            # Tamil
            "மாணவர்",
            "மாணவி",

            # Malayalam
            "വിദ്യാർത്ഥി",
            "വിദ്യാർത്ഥിനി",
        ],

        "Farmer": [

            # English
            "farmer",

            # Hindi
            "किसान",

            # Kannada
            "ರೈತ",
            "ರೈತರು",

            # Gujarati
            "ખેડૂત",

            # Tamil
            "விவசாயி",

            # Malayalam
            "കർഷകൻ",
            "കർഷക",
        ],

        "Employee": [

            # English
            "employee",
            "worker",
            "working professional",

            # Hindi
            "कर्मचारी",
            "नौकरी",
            "काम करने वाला",

            # Kannada
            "ಉದ್ಯೋಗಿ",
            "ಕೆಲಸಗಾರ",

            # Gujarati
            "કર્મચારી",
            "નોકરી",

            # Tamil
            "ஊழியர்",
            "வேலை செய்பவர்",

            # Malayalam
            "ജീവനക്കാരൻ",
            "തൊഴിലാളി",
        ],
    }

    for occupation, keywords in occupation_keywords.items():

        for keyword in keywords:

            if keyword in text:
                return occupation

    return None


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education(text: str):
    """
    Normalize education into the English values expected
    by schemes.json.
    """

    text = text.lower()

    engineering_keywords = [

        # English
        "engineering",
        "engineer",
        "btech",
        "b.tech",
        "b tech",
        "b.e",
        "be",
        "computer engineering",
        "mechanical engineering",
        "civil engineering",
        "electronics engineering",
        "electrical engineering",
        "information technology",
        "computer science",

        # Hindi
        "इंजीनियरिंग",
        "इंजीनियर",
        "बीटेक",
        "बी.टेक",
        "कंप्यूटर इंजीनियरिंग",

        # Kannada
        "ಎಂಜಿನಿಯರಿಂಗ್",
        "ಇಂಜಿನಿಯರಿಂಗ್",
        "ಎಂಜಿನಿಯರ್",
        "ಬಿಟೆಕ್",
        "ಬಿ.ಟೆಕ್",
        "ಕಂಪ್ಯೂಟರ್ ಎಂಜಿನಿಯರಿಂಗ್",

        # Gujarati
        "એન્જિનિયરિંગ",
        "ઇજનેરી",
        "એન્જિનિયર",
        "બીટેક",
        "બી.ટેક",
        "કમ્પ્યુટર એન્જિનિયરિંગ",

        # Tamil
        "பொறியியல்",
        "பொறியாளர்",
        "பி.டெக்",
        "பிடெக்",
        "கணினி பொறியியல்",

        # Malayalam
        "എഞ്ചിനീയറിംഗ്",
        "എൻജിനീയറിംഗ്",
        "എഞ്ചിനീയർ",
        "ബി.ടെക്",
        "ബിടെക്",
        "കമ്പ്യൂട്ടർ എഞ്ചിനീയറിംഗ്",
    ]

    medical_keywords = [

        # English
        "medical",
        "mbbs",
        "doctor",
        "nursing",

        # Hindi
        "मेडिकल",
        "डॉक्टर",
        "नर्सिंग",
        "एमबीबीएस",

        # Kannada
        "ವೈದ್ಯಕೀಯ",
        "ವೈದ್ಯ",
        "ನರ್ಸಿಂಗ್",
        "ಎಂಬಿಬಿಎಸ್",

        # Gujarati
        "મેડિકલ",
        "ડોક્ટર",
        "નર્સિંગ",
        "એમબીબીએસ",

        # Tamil
        "மருத்துவம்",
        "மருத்துவர்",
        "நர்சிங்",
        "எம்பிபிஎஸ்",

        # Malayalam
        "മെഡിക്കൽ",
        "ഡോക്ടർ",
        "നഴ്സിംഗ്",
        "എംബിബിഎസ്",
    ]

    arts_keywords = [

        # English
        "arts",
        "ba",
        "b.a",

        # Hindi
        "कला",
        "आर्ट्स",

        # Kannada
        "ಕಲೆ",
        "ಆರ್ಟ್ಸ್",

        # Gujarati
        "કલા",
        "આર્ટ્સ",

        # Tamil
        "கலை",
        "ஆர்ட்ஸ்",

        # Malayalam
        "കല",
        "ആർട്സ്",
    ]

    for keyword in engineering_keywords:

        if keyword in text:
            return "Engineering"

    for keyword in medical_keywords:

        if keyword in text:
            return "Medical"

    for keyword in arts_keywords:

        if keyword in text:
            return "Arts"

    return None


# ============================================================
# STATE EXTRACTION
# ============================================================

def extract_state(text: str):
    """
    Detect Indian states in multiple Indian languages
    and normalize them to English database names.
    """

    text = text.lower()

    state_keywords = {

        "Karnataka": [
            "karnataka",
            "ಕರ್ನಾಟಕ",
            "कर्नाटक",
            "કર્ણાટક",
            "கர்நாடகா",
            "കർണാടക",
        ],

        "Gujarat": [
            "gujarat",
            "ગુજરાત",
            "गुजरात",
            "குஜராத்",
            "ഗുജറാത്ത്",
        ],

        "Maharashtra": [
            "maharashtra",
            "महाराष्ट्र",
            "महाराष्ट",
            "महाराष्ट्र",
            "મહારાષ્ટ્ર",
            "மகாராஷ்டிரா",
            "മഹാരാഷ്ട്ര",
        ],

        "Rajasthan": [
            "rajasthan",
            "राजस्थान",
            "રાજસ્થાન",
            "ராஜஸ்தான்",
            "രാജസ്ഥാൻ",
        ],

        "Tamil Nadu": [
            "tamil nadu",
            "tamilnadu",
            "तमिलनाडु",
            "தமிழ்நாடு",
            "தமிழ் நாடு",
            "தமிழ்நாட்டில்",
            "തമിഴ്നാട്",
        ],

        "Kerala": [
            "kerala",
            "केरल",
            "കേരളം",
            "கேரளா",
            "ગુજરાત",
        ],

        "Delhi": [
            "delhi",
            "दिल्ली",
            "દિલ્હી",
            "டெல்லி",
            "ഡൽഹി",
        ],
    }

    for state, keywords in state_keywords.items():

        for keyword in keywords:

            if keyword in text:
                return state

    return None


# ============================================================
# MAIN PROFILE EXTRACTION
# ============================================================

def extract_profile(text: str):
    """
    Main multilingual profile extraction function.

    Converts multilingual user input into the normalized
    English profile expected by find_matching_schemes().
    """

    if not text or not text.strip():

        return {
            "age": None,
            "state": None,
            "occupation": None,
            "education": None,
            "income": None,
        }

    normalized_text = normalize_text(text)

    profile = {
        "age": extract_age(normalized_text),
        "state": extract_state(normalized_text),
        "occupation": extract_occupation(normalized_text),
        "education": extract_education(normalized_text),
        "income": extract_income(normalized_text),
    }

    return profile


# ============================================================
# SCHEME MATCHING
# ============================================================

def find_matching_schemes(profile):

    schemes = load_schemes()

    matched = []

    for scheme in schemes:

        reasons = []

        # ----------------------------------------------------
        # AGE
        # ----------------------------------------------------

        if profile["age"] is not None:

            if not (
                scheme["min_age"]
                <= profile["age"]
                <= scheme["max_age"]
            ):
                continue

            reasons.append(
                f"Age ({profile['age']}) is within "
                f"{scheme['min_age']}-{scheme['max_age']} years."
            )

        # ----------------------------------------------------
        # OCCUPATION
        # ----------------------------------------------------

        if profile["occupation"] != scheme["occupation"]:
            continue

        reasons.append(
            f"Occupation matches ({profile['occupation']})."
        )

        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------

        if (
            profile["education"] is not None
            and scheme["education"] != "None"
            and profile["education"] != scheme["education"]
        ):
            continue

        if profile["education"] is not None:

            reasons.append(
                f"Education matches ({profile['education']})."
            )

        # ----------------------------------------------------
        # INCOME
        # ----------------------------------------------------

        if profile["income"] is not None:

            if profile["income"] > scheme["max_income"]:
                continue

            reasons.append(
                f"Income ₹{profile['income']:,} is within "
                f"the allowed limit of "
                f"₹{scheme['max_income']:,}."
            )

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        if profile["state"] not in scheme["states"]:
            continue

        reasons.append(
            f"Scheme is available in {profile['state']}."
        )

        # ----------------------------------------------------
        # COPY SCHEME
        # ----------------------------------------------------

        scheme_copy = scheme.copy()

        scheme_copy["why_eligible"] = reasons

        matched.append(scheme_copy)

    return matched