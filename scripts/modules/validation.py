import re
import streamlit as st
from sqlalchemy import text
from modules.db_connection import get_db_connection



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

    try:
        engine = get_db_connection()
        if not engine:
            return False, "Could not connect to the database"

        with engine.connect() as conn:
            query = text('SELECT "email" FROM vg_prod.student_details WHERE LOWER("email") = LOWER(:email)')
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

def render_form_field(label, required=True):
    """Render a consistent form field label"""
    if required:
        st.markdown(f"**{label}** <span style='color: red;'>*</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**{label}**", unsafe_allow_html=True)


