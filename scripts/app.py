import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import re
import datetime


# Set page config at the very beginning
st.set_page_config(
    page_title="She for STEM Program",
    page_icon="👩‍🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display the PNG image in the top left corner of the Streamlit sidebar with custom dimensions
image_path = "https://raw.githubusercontent.com/VigyanShaala-Tech/student_registration_ui/final_registration_ui/image/vslogo.png"
st.markdown(
    f'<div style="text-align:center"><img src="{image_path}" width="200"></div>',
    unsafe_allow_html=True
)

st.markdown(
    "<div style='text-align: center;margin-bottom: 30px;'>"
    "<span style='font-size: 34px; font-weight: bold;'>She for STEM Program</span><br>"
    "</div>", 
    unsafe_allow_html=True
)

# Load environment variables from config.env
load_dotenv('config.env')

@st.cache_resource
def get_db_connection():
    try:
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        
        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("One or more required environment variables are missing or empty.")
        
        conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        engine = create_engine(
            conn_string,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True
        )
        
        return engine  
    
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None  

      
# Cache database queries
@st.cache_data
def fetch_data(_engine, query, column_name=None, params=None):
    try:
        df = pd.read_sql(query, _engine, params=params)
        if column_name:
            return df[column_name].tolist()
        return df
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return []

# Cache location data
@st.cache_data
def fetch_location_data(_engine, state=None, district=None, is_hometown=False):
    try:
        if state and district:
            query = f'''SELECT DISTINCT "city_category" 
                       FROM intermediate."location_mapping" 
                       WHERE "state_union_territory" = '{state}'
                       AND "district" = '{district}'
                       ORDER BY "city_category"'''
        elif state:
            query = f'''SELECT DISTINCT "district"     
                       FROM intermediate."location_mapping" 
                       WHERE "state_union_territory" = '{state}'
                       ORDER BY "district"'''
        else:
            query = f'''SELECT DISTINCT "state_union_territory" 
                       FROM intermediate."location_mapping" 
                       WHERE "country" = 'India' 
                       ORDER BY "state_union_territory"'''
        
        return fetch_data(_engine, query, "city_category" if state and district else "district" if state else "state_union_territory")
    except Exception as e:
        st.error(f"Error fetching location data: {str(e)}")
        return []


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
            query = text('SELECT "Email" FROM raw.general_information_sheet WHERE LOWER("Email") = LOWER(:Email)')
            result = conn.execute(query, {"Email": email})
            row = result.fetchone()

            if row:
                return False, "already_registered"
    except Exception as e:
        return False, f"Database error while checking email: {str(e)}"

    return True, ""

def validate_phone(phone):
    if not phone:
        return False, "Phone number is required"
    
    # Remove any spaces or special characters
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



def show_thank_you_page():
    st.balloons()

    st.markdown(
         """
        <div style="display: flex; justify-content: center;">
            <div style="max-width: 700px; text-align: center;">
                <h2>🎉 Welcome to She-for-STEM!</h2>
                <p style="font-size: 18px;">
                    Thanks for registering — you'll be enrolled soon.
                </p>
                <h3>👉 Start Learning:</h3>
                <p style="font-size: 17px;">
                    📱 <a href="https://play.google.com/store/apps/details?id=com.vigyanshaala.courses" target="_blank">Download App (Mobile)</a><br>
                    💻 <a href="https://mytribe.vigyanshaala.com/" target="_blank">Access on Computer</a><br>
                    🎥 <a href="https://bit.ly/VigyanShaala_App_Playlist" target="_blank">How to log in</a>
                </p>
                <h3>📢 WhatsApp Group Updates:</h3>
                <p style="font-size: 17px;">
                    You will be added to the WhatsApp group shortly. Stay tuned!
                </p>
                <p style="font-size: 18px;">
                    Excited to have you onboard!<br>
                    – Team VigyanShaala
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )



    
# Main form
def main():
    # Display logo at the top of every page     
    
    # Initialize session state for multi-page form
    if 'page' not in st.session_state:
        st.session_state.page = 1
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'is_female' not in st.session_state:
        st.session_state.is_female = None
    if 'suggested_email' not in st.session_state:
        st.session_state.suggested_email = None
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    if 'academic_year' not in st.session_state:
        st.session_state.academic_year = None
    if 'current_degree' not in st.session_state:
        st.session_state.current_degree = None
    if 'selected_university' not in st.session_state:
        st.session_state.selected_university = None
    if 'selected_college' not in st.session_state:
        st.session_state.selected_college = None
    if 'new_college_name' not in st.session_state:
        st.session_state.new_college_name = None
    if 'college_state' not in st.session_state:
        st.session_state.college_state = None
    if 'college_district' not in st.session_state:
        st.session_state.college_district = None
    if 'college_city_category' not in st.session_state:
        st.session_state.college_city_category = None
    if 'selected_subjects' not in st.session_state:
        st.session_state.selected_subjects = []
    if 'whatsapp' not in st.session_state:
        st.session_state.whatsapp = ""
    if 'dob' not in st.session_state:
        st.session_state.dob = ""
    if 'hometown_state' not in st.session_state:
        st.session_state.hometown_state = None
    if 'hometown_district' not in st.session_state:
        st.session_state.hometown_district = None
    if 'hometown_city_category' not in st.session_state:
        st.session_state.hometown_city_category = None
    if 'caste_category' not in st.session_state:
        st.session_state.caste_category = None
    if 'income_range' not in st.session_state:
        st.session_state.income_range = None
    if 'motivation' not in st.session_state:
        st.session_state.motivation = ""
    if 'problems' not in st.session_state:
        st.session_state.problems = ""
    if 'professor_name' not in st.session_state:
        st.session_state.professor_name = ""
    if 'professor_phone' not in st.session_state:
        st.session_state.professor_phone = ""

    if st.session_state.page == "thank_you":
        show_thank_you_page()
        return

    # Page 1: About Us and Initial Questions
    if st.session_state.page == 1:
        
        # Email and Gender Input
        st.markdown("### Registration Form")
        
        # Email input with validation
        render_form_field("Email Address")
        email = st.text_input("", value=st.session_state.email, placeholder="Enter your email address", label_visibility="collapsed")
        
        # Check for email suggestions on every input
        if '@' in email:
            suggestion = get_email_suggestion(email)
            if suggestion:
                st.session_state.suggested_email = suggestion
                if st.button(f"Did you mean {suggestion}?"):
                    st.session_state.email = suggestion
                    st.rerun()
        
        # Validate email
        if email:
            is_valid, message = validate_email(email)

            if not is_valid:
                if message == "already_registered":
                    st.markdown(
                        "<div style='background-color:#fff3cd; color:#856404; padding:10px; border-radius:5px; font-weight:bold;'>"
                        "Already registered!!! Log in, try another email, or contact support."
                        "</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.error(message)
  

        
        render_form_field("Are you a Woman/Female?")
        gender = st.radio("", ["Yes", "No"], index=0 if st.session_state.is_female is None else (0 if st.session_state.is_female else 1), label_visibility="collapsed")

        # Next button
        if st.button("Next"):
            if not email:
                st.error("Please enter your email address")
            else:
                is_valid, message = validate_email(email)
                if not is_valid:
                    st.error(message)
                else:
                    st.session_state.email = email
                    st.session_state.is_female = gender == "Yes"
                    st.session_state.page = 2
                    st.rerun()

        # About Us Section
        st.markdown("""
        #### About Us
        At VigyanShaala, we believe everyone should have the opportunity to create a better world through science. 
        That's why our mission at VigyanShaala is to enable the innovators of tomorrow to achieve their dreams 
        by bringing science, technology, and learning to their doorstep today. We are determined to create equity 
        in STEM education and opportunities for the most marginalised across India. Through carefully developed 
        ecosystems, we can eradicate inequalities and help even the most marginalized-- those who must innovate 
        to survive - to thrive in STEM careers.

        #### What is She for STEM
        Incubated and launched between lockdowns by Prof Ashutosh Kumar Sharma, then Secretary, DST., Program 
        Kalpana is an online mentoring-career coaching fellowship designed to successfully place every fellow on 
        a high confidence STEM path. With a strong emphasis on the elements of Individual Development Plan, 
        Self-Efficacy strengthening and Research Grade Experimental Projects, over the last two years we have 
        continuously evolved the program structure with active partnership of our mentees themselves. These 
        experiences and skills equip our fellows for marching into a high confidence trajectory towards scientific 
        jobs or higher studies in STEM at leading global and national universities.

        #### Who is it for
        It is for all enthusiastic and aspiring Female Undergraduates and postgraduates in Science, Technology, 
        Engineering and Math (STEM). The three key pillars we look for in a Kalpana Fellow are ACT - Ambition, 
        Commitment and Talent.

        The first cohort of 'She for STEM' was launched by Honorable Governor of Uttarakhand (Retd.) Lt. General 
        Gurmit Singh on 10th August 2024.
        """)

    # Page 2: Gender Check and College/Academic Information
    elif st.session_state.page == 2:
        if not st.session_state.is_female:
            st.info("Kalpana Program is only for women in STEM. We will soon have something for MEN in STEM soon. Keep checking the website and app.")
            st.error("We are very sorry, this is only for Women who are pursuing degree in sciences, and in the STEM fields.")
        else:
            if st.button("← Back"):
                st.session_state.page = 1
                st.rerun()
            
            st.markdown("### College & Academic Information")
            st.write(f"Email: {st.session_state.email}")
            
            # Get database connection
            engine = get_db_connection()
            
            # 1. Full Name
            render_form_field("Full Name")
            full_name = st.text_input("", value=st.session_state.full_name, placeholder="Enter your full name", label_visibility="collapsed")
            
            # 2. Current Academic Year
            render_form_field("Current Academic Year")
            academic_year = st.selectbox(
                "",
                ["1st Year", "2nd Year", "3rd Year", "4th Year"],
                index=["1st Year", "2nd Year", "3rd Year", "4th Year"].index(st.session_state.academic_year) if st.session_state.academic_year else 0,
                label_visibility="collapsed"
            )

            # 3. Current Degree Level
            render_form_field("Current Degree Level")
            degrees = fetch_data(engine, 'SELECT DISTINCT "display_name" FROM intermediate."course_mapping" ORDER BY "display_name"', "display_name")
            current_degree = st.selectbox(
                "",
                degrees,
                index=degrees.index(st.session_state.current_degree) if st.session_state.current_degree in degrees else 0,
                label_visibility="collapsed"
            ) if degrees else None

            # 4. University Name
            render_form_field("University Name")
            universities = fetch_data(engine, 'SELECT DISTINCT "standard_university_names" FROM intermediate."university_mapping" ORDER BY "standard_university_names"', "standard_university_names")
            selected_university = st.selectbox(
                "",
                universities,
                index=universities.index(st.session_state.selected_university) if st.session_state.selected_university in universities else 0,
                label_visibility="collapsed"
            ) if universities else None

               # 5. College Name
            render_form_field("College Name")
            # Show helper note below the field title
            st.markdown(
                "<div style='margin-top: -1rem; font-size: 0.85rem; color: gray;'>"
                "If you didn't find your college, select <b>Other</b> as College Name and type it manually."
                "</div>",
                unsafe_allow_html=True
)
            colleges = fetch_data(engine, 'SELECT DISTINCT "standard_college_names" FROM intermediate."college_mapping" ORDER BY "standard_college_names"', "standard_college_names")

            # Add "Other" option manually
            colleges.append("Other")

            selected_college = st.selectbox(
                "",
                colleges,
                index=colleges.index(st.session_state.selected_college) if st.session_state.selected_college in colleges else 0,
                label_visibility="collapsed"
            )

            st.session_state.selected_college = selected_college

            # If 'Other' is selected, ask for manual input
            new_college_name = ""
            if selected_college == "Other":
                render_form_field("Enter your College Name")
                new_college_name = st.text_input(
                    "", 
                    value=st.session_state.get("new_college_name", ""),
                    placeholder="Enter your college name manually", 
                    label_visibility="collapsed"
                )
                st.session_state.new_college_name = new_college_name


            # 6. College Location - State
            render_form_field("College State/Union Territory")
            states = fetch_location_data(engine)
            college_state = st.selectbox(
                "",
                states,
                index=states.index(st.session_state.college_state) if st.session_state.college_state in states else 0,
                key='college_state_selector',
                on_change=lambda: setattr(st.session_state, 'college_district', None),
                label_visibility="collapsed"
            ) if states else None
            
            if college_state != st.session_state.college_state:
                st.session_state.college_state = college_state
                st.session_state.college_district = None

            # 7. College Location - District
            render_form_field("College District")
            college_districts = fetch_location_data(engine, st.session_state.college_state) if st.session_state.college_state else []
            college_district = st.selectbox(
                "",
                college_districts,
                index=college_districts.index(st.session_state.college_district) if st.session_state.college_district in college_districts else 0,
                key='college_district_selector',
                label_visibility="collapsed"
            ) if college_districts else None
            
            if college_district != st.session_state.college_district:
                st.session_state.college_district = college_district

            # 8. College City Category
            render_form_field("College City Category")
            college_city_categories = fetch_location_data(engine, st.session_state.college_state, st.session_state.college_district) if st.session_state.college_state and st.session_state.college_district else []
            college_city_category = st.selectbox(
                "",
                college_city_categories,
                index=college_city_categories.index(st.session_state.college_city_category) if st.session_state.college_city_category in college_city_categories else 0,
                label_visibility="collapsed"
            ) if college_city_categories else None



            # 9. Primary Subject Areasgit commit -m "review_for_final_registration_ui"
            render_form_field("Currently Pursuing Subject Areas")
            subject_areas = fetch_data(engine, 'SELECT DISTINCT "sub_field" FROM intermediate."subject_mapping" ORDER BY "sub_field"', "sub_field")
            
            # Filter out any invalid default values
            valid_defaults = [subject for subject in st.session_state.selected_subjects if subject in subject_areas]
            
            selected_subjects = st.multiselect(
                label="",
                options=subject_areas,
                default=valid_defaults,
                max_selections=4,
                label_visibility="collapsed"
            )

            # Add some spacing before the next button
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Next button to page 3
            if st.button("Next"):
                # Validate required fields for page 2
                errors = []
                
                if not full_name:
                    errors.append("Please enter your full name")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Store page 2 data in session state
                    st.session_state.full_name = full_name
                    st.session_state.academic_year = academic_year
                    st.session_state.current_degree = current_degree
                    st.session_state.selected_university = selected_university
                    st.session_state.selected_college = selected_college
                    st.session_state.college_state = college_state
                    st.session_state.college_district = college_district
                    st.session_state.college_city_category = college_city_category
                    st.session_state.selected_subjects = selected_subjects
                    st.session_state.page = 3
                    st.rerun()  

    # Page 3: Personal Information
    elif st.session_state.page == 3:
        # Add back button at the top
        if st.button("← Back"):
            st.session_state.page = 2
            st.rerun()
        
        st.markdown("### Personal Information")
        st.write(f"Email: {st.session_state.email}")
        
        # Get database connection
        engine = get_db_connection()
        
        # 1.a WhatsApp Number
        render_form_field("WhatsApp Number")
        whatsapp = st.text_input("", value=st.session_state.whatsapp, placeholder="Enter your 10-digit WhatsApp number", label_visibility="collapsed")
        if whatsapp:
            is_valid, message = validate_phone(whatsapp)
            if not is_valid:
                st.error(message)

        # 1.b. Date of Birth
        render_form_field("Date of Birth")
        #Ensure value is always a datetime.date
        default_dob = datetime.date(2005, 1, 1)
        dob = st.session_state.get("dob", default_dob)

        if not isinstance(dob, (datetime.date, datetime.datetime)):
            dob = default_dob  # fallback in case dob is invalid

        st.session_state.dob = st.date_input(
            "Date of Birth",
            value=dob,
            min_value=datetime.date(1970, 1, 1),
            max_value=datetime.date.today(),
            format="YYYY-MM-DD",
            label_visibility="collapsed"
        )


        # 2a.  Future Subject Area
        render_form_field("Which subject area do you want to pursue in future?")

        future_subject_areas = fetch_data(
            engine,
            '''SELECT DISTINCT "subject_area"
            FROM intermediate."subject_mapping"
            ORDER BY "subject_area"''',
            "subject_area"
        )

        st.selectbox(
            "",
            future_subject_areas,
            index=(
                future_subject_areas.index(st.session_state.future_subject_area)
                if st.session_state.get("future_subject_area") in future_subject_areas
                else 0
            ) if future_subject_areas else 0,
            key="future_subject_area",           # ← let Streamlit manage state for us
            on_change=lambda: st.session_state.pop("future_sub_field", None),
            label_visibility="collapsed"
        )

        # 2b.  Future Sub‑field (depends on subject area)

        render_form_field("Which sub-field do you want to pursue in it?")

        future_sub_fields = fetch_data(
            engine,
            f'''SELECT DISTINCT "sub_field"
                FROM intermediate."subject_mapping"
                WHERE "subject_area" = '{st.session_state.get("future_subject_area", "")}'
                ORDER BY "sub_field"''',
            "sub_field"
        ) if st.session_state.get("future_subject_area") else []

        st.selectbox(
            "",
            future_sub_fields,
            index=(
                future_sub_fields.index(st.session_state.future_sub_field)
                if st.session_state.get("future_sub_field") in future_sub_fields
                else 0
            ) if future_sub_fields else 0,
            key="future_sub_field",
            label_visibility="collapsed"
        )


        # 3. Hometown/Origin - State
        render_form_field("Hometown State/Union Territory")
        hometown_states = fetch_location_data(engine, is_hometown=True)
        hometown_state = st.selectbox(
            "",
            hometown_states,
            index=hometown_states.index(st.session_state.hometown_state) if st.session_state.hometown_state in hometown_states else 0,
            key='hometown_state_selector',
            on_change=lambda: setattr(st.session_state, 'hometown_district', None),
            label_visibility="collapsed"
        ) if hometown_states else None
        
        if hometown_state != st.session_state.hometown_state:
            st.session_state.hometown_state = hometown_state
            st.session_state.hometown_district = None

        

        # 4. Hometown/Origin - District
        render_form_field("Hometown District")
        hometown_districts = fetch_location_data(engine, st.session_state.hometown_state, is_hometown=True) if st.session_state.hometown_state else []
        hometown_district = st.selectbox(
            "",
            hometown_districts,
            index=hometown_districts.index(st.session_state.hometown_district) if st.session_state.hometown_district in hometown_districts else 0,
            key='hometown_district_selector',
            label_visibility="collapsed"
        ) if hometown_districts else None
        
        if hometown_district != st.session_state.hometown_district:
            st.session_state.hometown_district = hometown_district

        # 5. Hometown City Category
        render_form_field("Hometown City Category")
        st.session_state.hometown_city_category = st.selectbox(
            "",
            fetch_location_data(engine, st.session_state.hometown_state, st.session_state.hometown_district, is_hometown=True) if st.session_state.hometown_state and st.session_state.hometown_district else [],
            index=(
                fetch_location_data(engine, st.session_state.hometown_state, st.session_state.hometown_district, is_hometown=True).index(st.session_state.hometown_city_category)
                if st.session_state.hometown_state and st.session_state.hometown_district and st.session_state.hometown_city_category in fetch_location_data(engine, st.session_state.hometown_state, st.session_state.hometown_district, is_hometown=True)
                else 0
            ) if st.session_state.hometown_state and st.session_state.hometown_district else 0,
            label_visibility="collapsed"
        )

        # 6. Caste/Category
        render_form_field("Caste/Category")
        st.session_state.caste_category = st.selectbox(
            "",
            ["General", "OBC", "SC/ST", "Other", "Prefer not to say"],
            index=["General", "OBC", "SC/ST", "Other", "Prefer not to say"].index(st.session_state.caste_category) if st.session_state.caste_category else 0,
            label_visibility="collapsed"
        )

        # 7. Annual Household Income
        render_form_field("Annual Household Income")
        st.session_state.income_range = st.selectbox(
            "",
            ["Below or Equal to 3 lacs per year (INR)", "Between 3-5 lacs (INR) per year", "Above 5 lacs per year (INR)"],
            index=["Below or Equal to 3 lacs per year (INR)", "Between 3-5 lacs (INR) per year", "Above 5 lacs per year (INR)"].index(st.session_state.income_range) if st.session_state.income_range else 0,
            label_visibility="collapsed"
        )

        # 8. Motivation
        render_form_field("Why are you applying for this program?")
        st.session_state.motivation = st.text_area(
            "",
            value=st.session_state.motivation,
            placeholder="In 50 characters or more, describe why you are applying for this program",
            help="Minimum 50 characters required",
            label_visibility="collapsed"
        )
        if st.session_state.motivation:
            is_valid, message = validate_character_count(st.session_state.motivation, 50)
            if not is_valid:
                st.error(message)

        # 9. Challenges
        render_form_field("What challenges do you face in your studies and career?")
        st.session_state.problems = st.text_area(
            "",
            value=st.session_state.problems,
            placeholder="In 50 characters or more, describe the biggest challenges you face in your studies and career",
            help="Minimum 50 characters required",
            label_visibility="collapsed"
        )
        if st.session_state.problems:
            is_valid, message = validate_character_count(st.session_state.problems, 50)
            if not is_valid:
                st.error(message)

        # 9. Professor's Name (Optional)
        render_form_field("Professor's Full Name", required=False)
        professor_name = st.text_input(
            "",
            value=st.session_state.get("professor_name", ""),
            placeholder="Enter full name of the professor",
            label_visibility="collapsed"
            )
        st.session_state.professor_name = professor_name

        # 11. Professor's Phone (Optional)
        render_form_field("Professor's Contact Number", required=False)
        professor_phone = st.text_input(
            "",
            value=st.session_state.professor_phone,
            placeholder="Enter the phone number of a motivated professor from your college who inspires you and may be interested in collaborating with us",
            label_visibility="collapsed"
        )
        if professor_phone:
            is_valid, message = validate_phone(professor_phone)
            if not is_valid:
                st.error(message)

        if st.button("Submit Registration", type="primary"):
            submission_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            errors = []

            is_valid, message = validate_phone(whatsapp)
            if not is_valid:
                errors.append(f"WhatsApp number: {message}")

            is_valid, message = validate_character_count(st.session_state.motivation, 50)
            if not is_valid:
                errors.append(f"Motivation: {message}")

            is_valid, message = validate_character_count(st.session_state.problems, 50)
            if not is_valid:
                errors.append(f"Challenges: {message}")

            if professor_phone:
                is_valid, message = validate_phone(professor_phone)
                if not is_valid:
                    errors.append(f"Professor's phone: {message}")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    if engine:
                        data = {
                        'Email': st.session_state.email,
                        'Gender': "Female",
                        'Name': st.session_state.full_name,
                        'Phone': whatsapp,
                        'Date_of_Birth': st.session_state.dob.strftime("%Y-%m-%d") if st.session_state.dob else None,
                        'Currently_Pursuing_Year': st.session_state.academic_year,
                        'Currently_Pursuing_Degree': st.session_state.current_degree,
                        'University': st.session_state.selected_university,
                        'Country': "India",
                        'Name_of_College_University': st.session_state.selected_college,
                        'College_State_Union_Territory': st.session_state.college_state,
                        'College_District': st.session_state.college_district,
                        'College_City_Category': st.session_state.college_city_category,
                        'Subject_Area': ', '.join(st.session_state.selected_subjects),
                        'Interest_Subject_Area': st.session_state.future_subject_area,
                        'Interest_Sub_Field': st.session_state.future_sub_field,
                        'State_Union_Territory': st.session_state.hometown_state,
                        'District': st.session_state.hometown_district,
                        'City_Category': st.session_state.hometown_city_category,
                        'Caste_Category': st.session_state.caste_category,
                        'Annual_Family_Income': st.session_state.income_range,
                        'Motivation': st.session_state.motivation,
                        'Problems': st.session_state.problems,
                        'Professor_Name': professor_name,
                        'Professor_Phone_Number': professor_phone,
                        'New_College_Name': st.session_state.get("new_college_name", "") if st.session_state.selected_college == "Other" else None,
                        'Submission_Timestamp': submission_timestamp
                    }


                        df = pd.DataFrame([data])
                        df.to_sql('general_information_sheet', engine, schema='raw', if_exists='append', index=False)

                        st.session_state.page = "thank_you"
                        st.rerun()

                    else:
                        st.error("Could not connect to database")
                except Exception as e:
                    st.error(f"Error saving data: {str(e)}")

if __name__ == "__main__":
    main()