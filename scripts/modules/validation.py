import os
import re
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import text
from modules.db_connection import get_db_connection

# Always load scripts/config.env (not dependent on Streamlit working directory)
load_dotenv(Path(__file__).resolve().parent.parent / "config.env")


def _is_duplicate_email_check_enabled():
    value = os.getenv("CHECK_DUPLICATE_EMAIL", "false").strip().lower()
    return value in ("true", "1", "yes", "on")



def validate_character_count(text, min_chars=50, max_chars=1_000_000):
    char_count = len(text.strip())
    
    if char_count < min_chars:
        return False, f"Minimum {min_chars} characters required. Currently: {char_count}"
    if char_count > max_chars:
        return False, f"Maximum {max_chars} characters exceeded. Currently: {char_count}"
    
    return True, "Valid input"

# Email validation and suggestion functions
def get_email_suggestion(email):
    common_domains = {
        'g': 'gmail.com',
        'y': 'yahoo.com',
        'o': 'outlook.com'
    }
    
    try:
        user, domain = email.split('@')
        first_char = domain[0].lower()
        
        if first_char in common_domains and domain != common_domains[first_char]:
            return f"{user}@{common_domains[first_char]}"
    except:
        pass
    return None

def validate_email(email):
    email = (email or "").strip()
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return False, "Invalid email format"

    common_typos = {
        "gamil.com": "gmail.com",
        "gnail.com": "gmail.com",
        "gmial.com": "gmail.com",
        "yaho.com": "yahoo.com",
        "outlok.com": "outlook.com"
    }

    try:
        user, domain = email.split("@")
    except ValueError:
        return False, "Invalid email format"

    if domain.lower() in common_typos:
        suggestion = f"{user}@{common_typos[domain.lower()]}"
        return False, f"Did you mean {suggestion}?"

    valid_tlds = ('.com', '.org', '.net', '.edu', '.gov', '.io', '.in')
    if not domain.endswith(valid_tlds):
        return False, "Invalid email domain"

    # Always allow test@gmail.com (skip duplicate check)
    if email.lower() == "test@gmail.com":
        return True, ""

    if not _is_duplicate_email_check_enabled():
        return True, ""

    try:
        engine = get_db_connection()
        if not engine:
            return False, "Could not connect to the database"

        with engine.connect() as conn:
            query = text('SELECT "email" FROM raw.student_details WHERE LOWER("email") = LOWER(:email)')
            result = conn.execute(query, {"email": email})
            row = result.fetchone()

            if row:
                return False, "Already registered!!! Log in, try another email, or contact support (+918983835993)"
    except Exception as e:
        return False, f"Database error while checking email: {str(e)}"
    
    return True, ""

def validate_phone(phone):
    if not phone:
        return False, "Phone number is required"
    
    if any(char.isalpha() for char in phone):
        return False, "Phone number should not contain letters"
    
    # Remove any non-digit characters (like spaces, dashes, etc.)
    phone = re.sub(r'[^0-9]', '', phone)
    
    if not phone.isdigit():
        return False, "Phone number should contain only digits"
    
    if len(phone) != 10:
        return False, f"Phone number must be exactly 10 digits (you entered {len(phone)} digits)"
    
    if not phone.startswith(('6', '7', '8', '9')):
        return False, "Phone number should start with 6, 7, 8, or 9"
    
    return True, "Valid phone number"


def validate_word_count(text, min_words):
    words = text.split()
    if len(words) < min_words:
        return False, f"Please enter at least {min_words} words (you entered {len(words)} words)"
    return True, "Valid word count"

MENTOR_MATCH_OPTIONS = [
    (
        "Technical depth",
        "Someone with hands-on expertise in my specific subject area who can guide me through the technical challenges of my project",
    ),
    (
        "Research & Academia",
        "Someone from a university or research background who can help me think rigorously and explore ideas deeply",
    ),
    (
        "Industry & Practical Application",
        "Someone working in the field who can connect my project to real-world problems and solutions",
    ),
    (
        "Innovation & Frugal Design",
        "Someone experienced in building low-cost, high-impact solutions in resource-constrained environments",
    ),
    (
        "Entrepreneurship & Commercialization",
        "Someone who can help me think about how my project could become a product or startup",
    ),
    (
        "Interdisciplinary Thinking",
        "Someone who can bring perspectives from outside my field to make my project stronger",
    ),
]

MENTOR_MATCH_LABELS = [label for label, _ in MENTOR_MATCH_OPTIONS]
MENTOR_MATCH_DESCRIPTIONS = {label: description for label, description in MENTOR_MATCH_OPTIONS}


def render_form_field(label, required=True):
    """Render a consistent form field label"""
    if required:
        st.markdown(f"**{label}** <span style='color: red;'>*</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**{label}**", unsafe_allow_html=True)


def selectbox_index(options, value):
    """Index for selectbox(default from session_state) — None if value not in options."""
    return options.index(value) if value in options else None


def multiselect_from_state(state_key, options, *, max_selections=None, placeholder=""):
    """Multiselect restored from session_state; save return value on Next/Submit only."""
    if not options:
        return []
    kwargs = {
        "options": options,
        "default": st.session_state.get(state_key, []),
        "placeholder": placeholder,
        "label_visibility": "collapsed",
    }
    if max_selections is not None:
        kwargs["max_selections"] = max_selections
    return st.multiselect("", **kwargs)


def render_mentor_match_preference_field():
    """Mentor match type: multiselect labels; full text shown for each selection."""
    st.markdown(
        "**What type of mentor support are you looking for for your STEM Frugal project?** "
        "<span style='color: red;'>*</span>",
        unsafe_allow_html=True,
    )

    labels = MENTOR_MATCH_LABELS
    selected = multiselect_from_state(
        "mentor_match_preference",
        labels,
        placeholder="Search and select one or more options",
    )
    for choice in selected:
        st.info(f"**{choice}** — {MENTOR_MATCH_DESCRIPTIONS[choice]}")

    return selected


COMFORTABLE_LANGUAGES = [
    "Assamese",
    "Bengali",
    "Garhwali",
    "Gujarati",
    "Hindi",
    "Kannada",
    "Kashmiri",
    "Konkani",
    "Kumaoni",
    "Maithili",
    "Malayalam",
    "Manipuri",
    "Marathi",
    "Odia",
    "Punjabi",
    "Sindhi",
    "Tamil",
    "Telugu",
    "Urdu",
    "Others",
]

COMFORTABLE_LANGUAGES_OTHER = "Others"


def render_comfortable_languages_field():
    """Languages other than English; multiselect with optional text when Others is chosen."""
    st.markdown(
        "**Other than English, which languages are you comfortable communicating in?** "
        "<span style='color: red;'>*</span>",
        unsafe_allow_html=True,
    )

    selected = multiselect_from_state(
        "comfortable_languages",
        COMFORTABLE_LANGUAGES,
        placeholder="Search and select one or more languages",
    )
    other_text = ""
    if COMFORTABLE_LANGUAGES_OTHER in selected:
        render_form_field("Please specify other language(s)", required=True)
        other_text = st.text_input(
            "",
            value=st.session_state.get("comfortable_languages_other", ""),
            placeholder="Enter language(s) not listed above",
            label_visibility="collapsed",
        ).strip()

    return selected, other_text


