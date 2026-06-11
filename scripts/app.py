import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json
from typing import Union
import re
import datetime
from pytz import timezone
from modules.page_config import setup_she_for_stem_page
from modules.validation import (
    validate_email,
    get_email_suggestion,
    validate_phone,
    validate_character_count,
    render_form_field,
    render_mentor_match_preference_field,
    render_comfortable_languages_field,
    multiselect_from_state,
    selectbox_index,
)
from modules.thankyou import show_thank_you_page
from modules.db_connection import get_db_connection, fetch_data, fetch_sub_fields_for_subject_areas
from modules.db_operations import fetch_location_data, insert_referral_college_professor, insert_student_registration, insert_student_education
from modules.about_us import show_about_us

# Setup page
setup_she_for_stem_page()

# Load environment variables from config.env
load_dotenv('config.env')


def save_page2_state(
    full_name,
    academic_year,
    current_degree,
    degree_dict,
    degree_data,
    selected_university,
    university_dict,
    new_university_name,
    selected_college,
    college_dict,
    new_college_name,
    college_country,
    college_state,
    college_district,
    college_city_category,
    college_location_dict,
    college_country_dict,
    selected_subjects,
    subject_dict,
):
    st.session_state.full_name = full_name
    st.session_state.academic_year = academic_year
    st.session_state.current_degree = current_degree
    st.session_state.current_degree_id = degree_dict.get(current_degree) if current_degree else None
    st.session_state.degree_data = degree_data
    st.session_state.selected_university = selected_university
    st.session_state.university_id = (
        university_dict.get(selected_university) if selected_university != "Others" else None
    )
    st.session_state.new_university_name = new_university_name
    st.session_state.selected_college = selected_college
    st.session_state.college_id = (
        college_dict.get(selected_college) if selected_college != "Others" else None
    )
    st.session_state.new_college_name = new_college_name
    st.session_state.college_country = college_country
    st.session_state.college_state = college_state
    st.session_state.college_district = college_district
    st.session_state.college_city_category = college_city_category
    st.session_state.college_location_id = (
        college_location_dict.get(college_city_category)
        if college_city_category
        else college_country_dict.get(college_country)
    )
    st.session_state.selected_subjects = selected_subjects
    st.session_state.selected_subject_ids = [
        subject_dict.get(subject) for subject in selected_subjects if subject in subject_dict
    ]


def save_page3_state(
    whatsapp,
    dob,
    future_subject_areas,
    future_sub_field,
    future_sub_field_2,
    future_sub_field_3,
    sub_field_pref_ids,
    mentor_match_preference,
    comfortable_languages,
    hometown_country,
    hometown_state,
    hometown_district,
    hometown_city_category,
    hometown_location_dict,
    hometown_country_dict,
    caste_category,
    income_range,
    motivation,
    problems,
    professor_name,
    professor_phone,
    partner_organization,
):
    st.session_state.whatsapp = whatsapp
    st.session_state.dob = dob
    st.session_state.future_subject_areas = future_subject_areas
    st.session_state._last_future_subject_areas = tuple(sorted(future_subject_areas))
    st.session_state.future_sub_field = future_sub_field
    st.session_state.future_sub_field_2 = future_sub_field_2
    st.session_state.future_sub_field_3 = future_sub_field_3
    st.session_state.sub_field_pref_ids = sub_field_pref_ids
    st.session_state.sub_field_id = sub_field_pref_ids[0] if sub_field_pref_ids else None
    st.session_state.mentor_match_preference = mentor_match_preference
    st.session_state.comfortable_languages = comfortable_languages
    st.session_state.hometown_country = hometown_country
    st.session_state.hometown_state = hometown_state
    st.session_state.hometown_district = hometown_district
    st.session_state.hometown_city_category = hometown_city_category
    st.session_state.hometown_location_id = (
        hometown_location_dict.get(hometown_city_category)
        if hometown_city_category
        else hometown_country_dict.get(hometown_country)
    )
    st.session_state.caste_category = caste_category
    st.session_state.income_range = income_range
    st.session_state.motivation = motivation
    st.session_state.problems = problems
    st.session_state.professor_name = professor_name
    st.session_state.professor_phone = professor_phone
    st.session_state.partner_organization = partner_organization


# Main form
def main():
    # Initialize session state with defaults
    defaults = {
        'page': 1,
        'email': "",
        'is_female': None,
        'full_name': "",
        'academic_year': "",
        'current_degree': "",
        'current_degree_id': None,
        'selected_university': "",
        'university_id': None,
        'new_university_name': "",
        'selected_college': "",
        'college_id': None,
        'new_college_name': "",
        'college_country': "India",
        'college_state': "",
        'college_district': "",
        'college_city_category': "",
        'college_location_id': None,
        'hometown_country': "India",
        'hometown_state': "",
        'hometown_district': "",
        'hometown_city_category': "",
        'hometown_location_id': None,
        'selected_subjects': [],
        'selected_subject_ids': [],
        'future_sub_field': None,
        'future_sub_field_2': None,
        'future_sub_field_3': None,
        'sub_field_id': None,
        'sub_field_pref_ids': [],
        'whatsapp': "",
        'dob': None,
        'future_subject_areas': [],
        'caste_category': "",
        'income_range': "",
        'motivation': "",
        'problems': "",
        'professor_name': "",
        'professor_phone': "",
        'partner_organization': "",
        'mentor_match_preference': [],
        'comfortable_languages': [],
        'comfortable_languages_other': "",
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Remove legacy widget keys that caused double-click / lost selections
    for stale_key in (
        "mentor_match_preference_selector",
        "comfortable_languages_selector",
        "comfortable_languages_other_input",
        "future_sub_field_pref_1_selector",
        "future_sub_field_pref_2_selector",
        "future_sub_field_pref_3_selector",
        "college_country_selector",
        "college_state_selector",
        "college_district_selector",
        "hometown_country_selector",
        "hometown_state_selector",
        "hometown_district_selector",
    ):
        st.session_state.pop(stale_key, None)

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

        # Validate email immediately when user types
        if email:
            is_valid, message = validate_email(email)
            if not is_valid:
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
        show_about_us()

    # Page 2: Gender Check and College/Academic Information
    elif st.session_state.page == 2:
        if not st.session_state.is_female:
            st.info("The She for STEM Program is only for women in STEM. We will be launching a program for men in STEM soon. Please keep checking our website and app for updates.")
            st.error("We are very sorry, this is only for Women who are pursuing degree in sciences, and in the STEM fields.")
            
            # Add back button for non-eligible users
            if st.button("← Back to Registration"):
                st.session_state.page = 1
                st.rerun()
        else:
            col1, col2 = st.columns([1, 4])
            with col1:
                page2_back_clicked = st.button("← Back")

            st.markdown("### College & Academic Information")
            st.write(f"Email: {st.session_state.email}")
            
            # Get database connection
            engine = get_db_connection()
            
            # 1. Full Name
            render_form_field("Full Name")
            full_name = st.text_input("", value=st.session_state.full_name, placeholder="Enter your full name", label_visibility="collapsed")
            # Auto-save to session state
            st.session_state.full_name = full_name
            
            # 2. Current Academic Year
            render_form_field("Current Academic Year")
            academic_year = st.selectbox(
                "",
                ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year"],
                index=selectbox_index(
                    ["1st Year", "2nd Year", "3rd Year", "4th Year", "5th Year"],
                    st.session_state.academic_year,
                ),
                placeholder="Select your current academic year",
                label_visibility="collapsed"
            )
            
            # 3. Current Degree Level
            render_form_field("Current Degree Level")
            degree_data = fetch_data(
                engine,
                '''
                SELECT DISTINCT ON ("display_name")
                    "display_name", "course_id", course_duration
                FROM raw."course_mapping"
                WHERE course_duration != 1
                ORDER BY "display_name"
                '''
            )
        
            if degree_data.empty:
                degrees = []
                degree_dict = {}
            else:
                degrees = degree_data["display_name"].tolist()
                degree_dict = dict(zip(degree_data["display_name"], degree_data["course_id"]))
            
            current_degree = st.selectbox(
                "",
                degrees,
                index=selectbox_index(degrees, st.session_state.current_degree),
                placeholder="Select your current degree level",
                label_visibility="collapsed"
            ) if degrees else None

            # 4. University Name
            render_form_field("University Name")
            st.markdown(
                "<div style='margin-top: -1rem; font-size: 0.85rem; color: gray;'>"
                "If your university isn't listed, select <b>Others</b> and enter the name manually."
                "</div>",
                unsafe_allow_html=True
            )
            university_data = fetch_data(engine, 'SELECT DISTINCT "university_id", "standard_university_names" FROM raw."university_mapping" ORDER BY "standard_university_names"')
            if university_data.empty:
                universities = []
                university_dict = {}
            else:
                universities = university_data["standard_university_names"].tolist()
                university_dict = dict(zip(university_data["standard_university_names"], university_data["university_id"]))
            universities.append("Others")

            selected_university = st.selectbox(
                "",
                universities,
                index=selectbox_index(universities, st.session_state.selected_university),
                placeholder="Search or select your university",
                label_visibility="collapsed"
            )

            # If 'Others' is selected, ask for manual input
            new_university_name = ""
            if selected_university == "Others":
                render_form_field("Enter your University Name")
                new_university_name = st.text_input(
                    "",
                    value=st.session_state.new_university_name,
                    placeholder="Enter your university name manually",
                    label_visibility="collapsed"
                )
                # Auto-save to session state
                st.session_state.new_university_name = new_university_name

            # 5. College Name
            render_form_field("College Name")
            st.markdown(
                "<div style='margin-top: -1rem; font-size: 0.85rem; color: gray;'>"
                "If your college isn't listed, select <b>Others</b> and enter the name manually."
                "</div>",
                unsafe_allow_html=True
            )
            college_data = fetch_data(engine, 'SELECT DISTINCT "college_id", "standard_college_names" FROM raw."college_mapping" ORDER BY "standard_college_names"')
            if college_data.empty:
                colleges = []
                college_dict = {}
            else:
                colleges = college_data["standard_college_names"].tolist()
                college_dict = dict(zip(college_data["standard_college_names"], college_data["college_id"]))
            colleges.append("Others")

            selected_college = st.selectbox(
                "",
                colleges,
                index=selectbox_index(colleges, st.session_state.selected_college),
                placeholder="Search or select your college",
                label_visibility="collapsed"
            )
            
            # If 'Others' is selected, ask for manual input
            new_college_name = ""
            if selected_college == "Others":
                render_form_field("Enter your College Name")
                new_college_name = st.text_input(
                    "",
                    value=st.session_state.new_college_name,
                    placeholder="Enter your college name manually",
                    label_visibility="collapsed"
                )
                # Auto-save to session state
                st.session_state.new_college_name = new_college_name

            # 6. College Location - Country
            render_form_field("College Country")
            college_countries, college_country_dict = fetch_location_data(engine)
            college_country = st.selectbox(
                "",
                college_countries,
                index=selectbox_index(college_countries, st.session_state.college_country) or 0,
                placeholder="Search or select your college country",
                label_visibility="collapsed"
            ) if college_countries else None

            # 7. College Location - State (only for India)
            college_state = None
            college_district = None
            college_city_category = None
            college_location_dict = {}
            if college_country == "India":
                render_form_field("College State/Union Territory")
                college_state_data = fetch_location_data(engine, country=college_country) if college_country else pd.DataFrame()
                if college_state_data.empty:
                    college_states = []
                else:
                    college_states = college_state_data["state_union_territory"].tolist()

                college_state = st.selectbox(
                    "",
                    college_states,
                    index=selectbox_index(college_states, st.session_state.college_state),
                    placeholder="Search or select your college state",
                    label_visibility="collapsed"
                ) if college_states else None

                # 8. College Location - District
                if college_state:
                    render_form_field("College District")
                    college_districts = fetch_location_data(engine, college_country, college_state) if college_country and college_state else []

                    college_district = st.selectbox(
                        "",
                        college_districts,
                        index=selectbox_index(college_districts, st.session_state.college_district),
                        placeholder="Search or select your college district",
                        label_visibility="collapsed"
                    ) if college_districts else None

                # 9. College City Category
                if college_district:
                    render_form_field("College City Category")
                    college_location_data = fetch_location_data(
                        engine,
                        college_country,
                        college_state,
                        college_district
                    ) if college_country and college_state and college_district else pd.DataFrame()

                    if college_location_data.empty:
                        college_city_categories = []
                        college_location_dict = {}
                    else:
                        college_city_categories = college_location_data["city_category"].tolist()
                        college_location_dict = dict(zip(college_location_data["city_category"], college_location_data["location_id"]))

                    college_city_category = st.selectbox(
                        "",
                        college_city_categories,
                        index=selectbox_index(college_city_categories, st.session_state.college_city_category),
                        placeholder="Select your college city category",
                        label_visibility="collapsed"
                    ) if college_city_categories else None


            # 10. Currently Pursuing Subject Areas
            render_form_field("Currently Pursuing Subject Areas")
            subject_data = fetch_data(
                engine,
                '''
                SELECT DISTINCT ON ("sub_field") "sub_field", "id"
                FROM raw."subject_mapping"
                ORDER BY "sub_field", "id"
                ''',
                None
            )
            if subject_data.empty:
                subjects = []
                subject_dict = {}
            else:
                subjects = subject_data["sub_field"].tolist()
                subject_dict = dict(zip(subject_data["sub_field"], subject_data["id"]))

            selected_subjects = multiselect_from_state(
                "selected_subjects",
                subjects,
                max_selections=4,
                placeholder="Search and select up to 4 subject areas",
            )


            st.markdown("<br>", unsafe_allow_html=True)

            if page2_back_clicked:
                save_page2_state(
                    full_name,
                    academic_year,
                    current_degree,
                    degree_dict,
                    degree_data,
                    selected_university,
                    university_dict,
                    new_university_name,
                    selected_college,
                    college_dict,
                    new_college_name,
                    college_country,
                    college_state,
                    college_district,
                    college_city_category,
                    college_location_dict,
                    college_country_dict,
                    selected_subjects,
                    subject_dict,
                )
                st.session_state.page = 1
                st.rerun()

            if st.button("Next"):
                # Validate required fields for page 2
                errors = []
                
                if not full_name:
                    errors.append("Please enter your full name")
                if not academic_year:
                    errors.append("Please select your academic year")
                if not current_degree:
                    errors.append("Please select your current degree level")
                if not selected_university:
                    errors.append("Please select your university")
                if selected_university == "Others" and not new_university_name:
                    errors.append("Please enter your university name")
                if not selected_college:
                    errors.append("Please select your college")
                if selected_college == "Others" and not new_college_name:
                    errors.append("Please enter your college name")
                if not college_country:
                    errors.append("Please select your college country")
                if college_country == "India":
                    if not college_state:
                        errors.append("Please select your college state")
                    if not college_district:
                        errors.append("Please select your college district")
                    if not college_city_category:
                        errors.append("Please select your college city category")
                if not selected_subjects:
                    errors.append("Please select at least one subject area")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    save_page2_state(
                        full_name,
                        academic_year,
                        current_degree,
                        degree_dict,
                        degree_data,
                        selected_university,
                        university_dict,
                        new_university_name,
                        selected_college,
                        college_dict,
                        new_college_name,
                        college_country,
                        college_state,
                        college_district,
                        college_city_category,
                        college_location_dict,
                        college_country_dict,
                        selected_subjects,
                        subject_dict,
                    )
                    st.session_state.page = 3
                    st.rerun()

# Page 3: Personal Information
    elif st.session_state.page == 3:
        col1, col2 = st.columns([1, 4])
        with col1:
            page3_back_clicked = st.button("← Back")

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
        st.session_state.whatsapp = whatsapp

        # 1.b. Date of Birth
        render_form_field("Date of Birth")

        dob = st.date_input(
            "",
            value=st.session_state.dob,
            min_value=datetime.date(1970, 1, 1),
            max_value=datetime.date.today(),
            format="YYYY-MM-DD",
            label_visibility="collapsed"
        )


        # 2a. Future Subject Areas (up to 2)
        st.markdown(
            "**Which subject area do you want to pursue in future?** "
            "<span style='color: red;'>*</span> "
            "<small style='color: #555;'>(select up to 2 subject areas)</small>",
            unsafe_allow_html=True,
        )

        subject_area_options = fetch_data(
            engine,
            '''SELECT DISTINCT "subject_area"
            FROM raw."subject_mapping"
            ORDER BY "subject_area"''',
            "subject_area"
        )

        future_subject_areas = multiselect_from_state(
            "future_subject_areas",
            subject_area_options,
            max_selections=2,
            placeholder="Search and select up to 2 subject areas",
        )

        # 2b. Future Sub-field / STEM Frugal preferences (up to 3)
        st.markdown(
            "**What is your specific area of specialization or the sub-field you'd like to work in for your STEM Frugal project?** "
            "<span style='color: red;'>*</span><br>"
            "<small style='color: #555;'>"
            "(Select up to 3 preferences in order of priority — this helps us find the best mentor match for you in accelerator programs)"
            "</small>",
            unsafe_allow_html=True,
        )

        selected_areas = future_subject_areas
        sub_field_data = fetch_sub_fields_for_subject_areas(engine, selected_areas)

        if not isinstance(sub_field_data, pd.DataFrame) or sub_field_data.empty:
            future_sub_fields = []
            sub_field_dict = {}
        else:
            future_sub_fields = sub_field_data["sub_field"].tolist()
            sub_field_dict = dict(zip(sub_field_data["sub_field"], sub_field_data["id"]))

        # Reset preferences when selected subject areas change
        areas_key = tuple(sorted(selected_areas))
        if st.session_state.get("_last_future_subject_areas") != areas_key:
            st.session_state.future_sub_field = None
            st.session_state.future_sub_field_2 = None
            st.session_state.future_sub_field_3 = None
            st.session_state.sub_field_pref_ids = []
            st.session_state.sub_field_id = None
            st.session_state._last_future_subject_areas = areas_key

        def _sub_field_options(exclude):
            return [f for f in future_sub_fields if f not in exclude]

        future_sub_field = None
        future_sub_field_2 = None
        future_sub_field_3 = None

        if future_sub_fields:
            render_form_field("1st Preference")
            pref_1_options = _sub_field_options([])
            future_sub_field = st.selectbox(
                "",
                pref_1_options,
                index=selectbox_index(pref_1_options, st.session_state.future_sub_field),
                placeholder="Search or select your 1st preference",
                label_visibility="collapsed",
            )

            render_form_field("2nd Preference", required=False)
            pref_2_options = _sub_field_options([future_sub_field] if future_sub_field else [])
            if pref_2_options:
                future_sub_field_2 = st.selectbox(
                    "",
                    pref_2_options,
                    index=selectbox_index(pref_2_options, st.session_state.future_sub_field_2),
                    placeholder="Search or select your 2nd preference (optional)",
                    label_visibility="collapsed",
                )
            else:
                future_sub_field_2 = None

            render_form_field("3rd Preference", required=False)
            exclude_for_3 = [p for p in (future_sub_field, future_sub_field_2) if p]
            pref_3_options = _sub_field_options(exclude_for_3)
            if pref_3_options:
                future_sub_field_3 = st.selectbox(
                    "",
                    pref_3_options,
                    index=selectbox_index(pref_3_options, st.session_state.future_sub_field_3),
                    placeholder="Search or select your 3rd preference (optional)",
                    label_visibility="collapsed",
                )
            else:
                future_sub_field_3 = None

        sub_field_pref_ids = [
            sub_field_dict[name]
            for name in (future_sub_field, future_sub_field_2, future_sub_field_3)
            if name and name in sub_field_dict
        ]

        mentor_match_preference = render_mentor_match_preference_field()
        comfortable_languages, comfortable_languages_other = render_comfortable_languages_field()

        # 3. Hometown/Origin - Country
        render_form_field("Hometown Country")
        hometown_countries, hometown_country_dict = fetch_location_data(engine)
        hometown_country = st.selectbox(
            "",
            hometown_countries,
            index=selectbox_index(hometown_countries, st.session_state.hometown_country) or 0,
            placeholder="Search or select your hometown country",
            label_visibility="collapsed"
        ) if hometown_countries else None

        # 4. Hometown/Origin - State (only for India)
        hometown_state = None
        hometown_district = None
        hometown_city_category = None
        hometown_location_dict = {}
        if hometown_country == "India":
            render_form_field("Hometown State/Union Territory")
            hometown_state_data = fetch_location_data(engine, country=hometown_country) if hometown_country else pd.DataFrame()
            if hometown_state_data.empty:
                hometown_states = []
            else:
                hometown_states = hometown_state_data["state_union_territory"].tolist()

            hometown_state = st.selectbox(
                "",
                hometown_states,
                index=selectbox_index(hometown_states, st.session_state.hometown_state),
                placeholder="Search or select your hometown state",
                label_visibility="collapsed"
            ) if hometown_states else None

            # 5. Hometown/Origin - District
            if hometown_state:
                render_form_field("Hometown District")
                hometown_districts = fetch_location_data(
                    engine, hometown_country, hometown_state
                ) if hometown_country and hometown_state else []

                hometown_district = st.selectbox(
                    "",
                    hometown_districts,
                    index=selectbox_index(hometown_districts, st.session_state.hometown_district),
                    placeholder="Search or select your hometown district",
                    label_visibility="collapsed"
                ) if hometown_districts else None

            # 6. Hometown City Category
            if hometown_district:
                render_form_field("Hometown City Category")
                hometown_location_data = fetch_location_data(
                    engine,
                    hometown_country,
                    hometown_state,
                    hometown_district
                ) if hometown_country and hometown_state and hometown_district else pd.DataFrame()

                if hometown_location_data.empty:
                    hometown_city_categories = []
                    hometown_location_dict = {}
                else:
                    hometown_city_categories = hometown_location_data["city_category"].tolist()
                    hometown_location_dict = dict(zip(hometown_location_data["city_category"], hometown_location_data["location_id"]))

                hometown_city_category = st.selectbox(
                    "",
                    hometown_city_categories,
                    index=selectbox_index(hometown_city_categories, st.session_state.hometown_city_category),
                    placeholder="Select your hometown city category",
                    label_visibility="collapsed"
                ) if hometown_city_categories else None

        # 6. Caste/Category
        render_form_field("Caste/Category")
        caste_options = ["General", "OBC", "SC/ST", "Other", "Prefer not to say"]
        caste_category = st.selectbox(
            "",
            caste_options,
            index=selectbox_index(caste_options, st.session_state.caste_category),
            placeholder="Select your caste/category",
            label_visibility="collapsed"
        )

        # 7. Annual Household Income
        render_form_field("Annual Household Income")
        income_options = [
            "Below or Equal to 3 lacs per year (INR)",
            "Between 3-5 lacs (INR) per year",
            "Above 5 lacs per year (INR)"
        ]
        income_range = st.selectbox(
            "",
            income_options,
            index=selectbox_index(income_options, st.session_state.income_range),
            placeholder="Select your income range",
            label_visibility="collapsed"
        )

        # 8. Motivation
        render_form_field("Why are you applying for this program? (Optional)", required=False)
        motivation = st.text_area(
            "",
            value=st.session_state.get("motivation", ""),
            placeholder="In 50 characters or more, describe why you are applying for this program",
            help="Minimum 50 characters required",
            label_visibility="collapsed"
        )
        st.session_state.motivation = motivation
        if motivation:
            is_valid, message = validate_character_count(motivation, 50)
            if not is_valid:
                st.error(message)

        # 9. Challenges
        render_form_field("What challenges do you face in your studies and career? (Optional)", required=False)
        problems = st.text_area(
            "",
            value=st.session_state.get("problems", ""),
            placeholder="In 50 characters or more, describe the biggest challenges you face in your studies and career",
            help="Minimum 50 characters required",
            label_visibility="collapsed"
        )
        st.session_state.problems = problems
        if problems:
            is_valid, message = validate_character_count(problems, 50)
            if not is_valid:
                st.error(message)

        # 10. Professor's Name (Optional)
        render_form_field("If possible, please enter the full name of an inspiring professor from your college who may be open to collaboration.(Optional)", required=False)
        professor_name = st.text_input(
            "",
            value=st.session_state.get("professor_name", ""),
            placeholder="Enter full name of the professor",
            label_visibility="collapsed"
        )
        st.session_state.professor_name = professor_name

        # 11. Professor's Phone (Optional)
        render_form_field("Professor's contact number.(Optional)", required=False)
        professor_phone = st.text_input(
            "",
            value=st.session_state.get("professor_phone", ""),
            placeholder="Enter the professor's 10-digit phone number",
            label_visibility="collapsed"
        )

        if professor_phone:
                is_valid, message = validate_phone(professor_phone)
                if not is_valid:
                    st.error(message)    

        st.session_state.professor_phone = professor_phone

        # 12. Partner Organization
        render_form_field(
            "Are you associated with any of the following partner organizations or chapters?",
        )
        st.markdown(
                "<div style='margin-top: -1rem; font-size: 0.85rem; color: gray;'>"
                "(If none, please select <b>“I’m applying on my own”</b>)"
                "</div>",
                unsafe_allow_html=True
            )            

        partner_options = [
            "Avanti Fellows",
            "Christ University / Trivandrum Chapter",
            "Christ University / Bangalore Chapter",
            "Dr. Reddy’s Foundation – SASHAKTH",
            "Eklavya Foundation",
            "Foundation For Excellence (FFE)",
            "Udayan Care – Udayan Shalini Fellowship",
            "I’m applying on my own (not through any organization)"
        ]

        partner_organization = st.selectbox(
            "",
            partner_options,
            index=selectbox_index(partner_options, st.session_state.get("partner_organization")),
            placeholder="Please select the one that applies to you the most.",
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if page3_back_clicked:
            save_page3_state(
                whatsapp,
                dob,
                future_subject_areas,
                future_sub_field,
                future_sub_field_2,
                future_sub_field_3,
                sub_field_pref_ids,
                mentor_match_preference,
                comfortable_languages,
                hometown_country,
                hometown_state,
                hometown_district,
                hometown_city_category,
                hometown_location_dict,
                hometown_country_dict,
                caste_category,
                income_range,
                motivation,
                problems,
                professor_name,
                professor_phone,
                partner_organization,
            )
            st.session_state.page = 2
            st.rerun()

        if st.button("Submit Registration", type="primary"):
            
            ist = timezone('Asia/Kolkata')
            submission_timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
            errors = []

            is_valid, message = validate_phone(whatsapp)
            if not is_valid:
                errors.append(f"WhatsApp number: {message}")
            if not dob:
                errors.append("Please enter your date of birth")
            if len(future_subject_areas) < 2:
                errors.append("Please select exactly 2 subject areas you want to pursue in future")
            if not future_sub_field:
                errors.append("Please select your 1st preference for sub-field / specialization")
            if not mentor_match_preference:
                errors.append("Please select at least one type of mentor support you are looking for")
            if not comfortable_languages:
                errors.append("Please select at least one language you are comfortable communicating in")
            elif "Others" in comfortable_languages and not comfortable_languages_other:
                errors.append("Please specify the other language(s) you selected")
            if not caste_category:
                errors.append("Please select your caste/category")
            if not income_range:
                errors.append("Please select your income range")
            # Motivation is optional, but if provided, must be at least 50 characters
            if motivation:
                is_valid, message = validate_character_count(motivation, 50)
                if not is_valid:
                    errors.append(f"Motivation: {message}")
            # Problems/Challenges is optional, but if provided, must be at least 50 characters
            if problems:
                is_valid, message = validate_character_count(problems, 50)
                if not is_valid:
                    errors.append(f"Challenges: {message}")
            if professor_phone:
                is_valid, message = validate_phone(professor_phone)
                if not is_valid:
                    errors.append(f"Professor's phone: {message}")
            if not partner_organization:
                errors.append("Please select your partner organization")
            if errors:
                for error in errors:
                    st.error(error)
            else:
                save_page3_state(
                    whatsapp,
                    dob,
                    future_subject_areas,
                    future_sub_field,
                    future_sub_field_2,
                    future_sub_field_3,
                    sub_field_pref_ids,
                    mentor_match_preference,
                    comfortable_languages,
                    hometown_country,
                    hometown_state,
                    hometown_district,
                    hometown_city_category,
                    hometown_location_dict,
                    hometown_country_dict,
                    caste_category,
                    income_range,
                    motivation,
                    problems,
                    professor_name,
                    professor_phone,
                    partner_organization,
                )

                try:
                    with engine.connect() as conn:
                        with conn.begin():  # Start a transaction for the core inserts
                            # Split full_name into first_name and last_name (simple split on first space)
                            full_name = st.session_state.full_name or ""
                            name_parts = full_name.strip().split(" ", 1)
                            first_name = name_parts[0].capitalize() if name_parts else ""
                            last_name = name_parts[1].capitalize() if len(name_parts) > 1 else ""

                            # Upsert student_details -> RETURNING id
                            result = conn.execute(
                                text("""
                                    INSERT INTO raw.student_details (
                                        email,
                                        first_name,
                                        last_name,
                                        gender,
                                        phone,
                                        date_of_birth,
                                        caste,
                                        annual_family_income_inr,
                                        location_id
                                    )
                                    VALUES (
                                        LOWER(:email),
                                        :first_name,
                                        :last_name,
                                        :gender,
                                        :phone,
                                        :date_of_birth,
                                        :caste,
                                        :annual_family_income_inr,
                                        :location_id
                                    )
                                    ON CONFLICT (email)
                                    DO UPDATE SET
                                        first_name = EXCLUDED.first_name,
                                        last_name = EXCLUDED.last_name,
                                        phone = EXCLUDED.phone,
                                        date_of_birth = EXCLUDED.date_of_birth,
                                        caste = EXCLUDED.caste,
                                        annual_family_income_inr = EXCLUDED.annual_family_income_inr,
                                        location_id = EXCLUDED.location_id
                                    RETURNING id;
                                """),
                                {
                                    "email": st.session_state.email,
                                    "first_name": first_name,
                                    "last_name": last_name,
                                    "gender": "F",
                                    "phone": whatsapp,
                                    "date_of_birth": dob.strftime("%Y-%m-%d") if dob else None,
                                    "caste": st.session_state.caste_category,
                                    "annual_family_income_inr": st.session_state.income_range,
                                    "location_id": st.session_state.hometown_location_id,
                                }
                            )

                            # >>> Special handling: if scalar() fails, show the custom message
                            try:
                                student_id = result.scalar()
                            except Exception as scalar_err:
                                st.error(
                                    "Your basic information has been saved. "
                                    "We ran into an issue while generating your Student ID. "
                                    "Please contact support at +91 8983835993 and share a screenshot of this error:\n\n"
                                    f"{scalar_err}"
                                )
                                st.stop()  # halt execution so nothing else runs

                            # Prepare form_details for student_registration
                            form_json = {
                                "motivation": st.session_state.motivation,
                                "problems": st.session_state.problems,
                                "partner_organization": partner_organization,
                                "new_university_name": st.session_state.new_university_name if st.session_state.selected_university == "Others" else None,
                                "new_college_name": st.session_state.new_college_name if st.session_state.selected_college == "Others" else None,
                                "currently_pursuing_year": st.session_state.academic_year,
                                "mentor_match_preference": st.session_state.mentor_match_preference,
                                "comfortable_languages": st.session_state.comfortable_languages,
                                "comfortable_languages_other": (
                                    st.session_state.comfortable_languages_other
                                    if "Others" in st.session_state.comfortable_languages
                                    else None
                                ),
                            }

                            # Insert into raw.student_registration
                            if not insert_student_registration(
                                conn,
                                student_id=student_id,
                                form_details=form_json,
                                submission_timestamp=submission_timestamp
                            ):
                                raise Exception("Failed to insert into student_registration")

                            # Insert into raw.referral_college_professor
                            if not insert_referral_college_professor(
                                conn,
                                student_id=student_id,
                                college_id=st.session_state.college_id if st.session_state.selected_college != "Others" else None,
                                name=professor_name,
                                phone=professor_phone
                            ):
                                raise Exception("Failed to insert into referral_college_professor")

                            # Retrieve course_duration from degree_data
                            course_duration = None
                            if st.session_state.current_degree_id and not st.session_state.degree_data.empty:
                                matching_rows = st.session_state.degree_data[
                                    st.session_state.degree_data["course_id"] == st.session_state.current_degree_id
                                ]
                                if not matching_rows.empty:
                                    course_duration = int(matching_rows["course_duration"].iloc[0])

                            # Insert into raw.student_education
                            if not insert_student_education(
                                conn,
                                student_id=student_id,
                                education_course_id=st.session_state.current_degree_id,
                                subject_id=st.session_state.selected_subject_ids,
                                interest_subject_id=st.session_state.sub_field_pref_ids,
                                college_id=st.session_state.college_id if st.session_state.selected_college != "Others" else None,
                                university_id=st.session_state.university_id if st.session_state.selected_university != "Others" else None,
                                college_location_id=st.session_state.college_location_id,
                                academic_year=st.session_state.academic_year,
                                course_duration=course_duration
                            ):
                                raise Exception("Failed to insert into student_education")

                    # If everything went fine:
                    st.session_state.page = "thank_you"
                    st.rerun()

                except Exception as e:
                    # Generic catch-all for other failures (after the backup is already saved)
                    st.error(
                        f"Error: {e}\n\n"
                        "Please contact support at +91 8983835993 and share a screenshot of this message."
                    )



if __name__ == "__main__":
    main()


































