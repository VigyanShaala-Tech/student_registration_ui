import streamlit as st
import pandas as pd
from sqlalchemy import text
import json
from typing import Union
import datetime
from modules.db_connection import fetch_data


@st.cache_data
def fetch_location_data(_engine, country=None, state=None, district=None):
    try:
        if country and state and district:
            query = f'''SELECT DISTINCT "city_category", "location_id" 
                       FROM intermediate."location_mapping" 
                       WHERE "country" = '{country}'
                       AND "state_union_territory" = '{state}'
                       AND "district" = '{district}'
                       ORDER BY "city_category"'''
            return fetch_data(_engine, query)
        elif country and state:
            query = f'''SELECT DISTINCT "district"     
                       FROM intermediate."location_mapping" 
                       WHERE "country" = '{country}'
                       AND "state_union_territory" = '{state}'
                       ORDER BY "district"'''
            return fetch_data(_engine, query, "district")
        elif country:
            query = f'''SELECT DISTINCT ON ("state_union_territory") "state_union_territory", "location_id" 
                       FROM intermediate."location_mapping" 
                       WHERE "country" = '{country}' 
                       ORDER BY "state_union_territory"'''
            return fetch_data(_engine, query)
        else:
            query = f'''SELECT DISTINCT ON ("country") "country", "location_id" 
                       FROM intermediate."location_mapping" 
                       ORDER BY "country"'''
            country_data = fetch_data(_engine, query)
            if country_data.empty:
                countries = []
                country_dict = {}
            else:
                countries = country_data["country"].tolist()
                country_dict = dict(zip(country_data["country"], country_data["location_id"]))

            return countries, country_dict
    except Exception as e:
        st.error(f"Error fetching location data: {str(e)}")
        return [], {}


def insert_referral_college_professor(conn, student_id, college_id, name, phone):
    """Insert data into intermediate.referral_college_professor table if name or phone is provided."""
    try:
        # Validate inputs
        if student_id is None:
            raise ValueError("student_id cannot be None")
        
        # Skip insertion if both name and phone are None or empty
        if (name is None or name.strip() == "") and (phone is None or phone.strip() == ""):
            print(f"Skipping insertion into referral_college_professor: both name and phone are empty (student_id={student_id}, college_id={college_id})")
            return True

        # Debug: Log parameter values
        print(f"Inserting into referral_college_professor: student_id={student_id}, college_id={college_id}, name={name}, phone={phone}")

        query = text("""
        INSERT INTO intermediate.referral_college_professor (student_id, college_id, name, phone)
        VALUES (:student_id, :college_id, :name, :phone)
        """)
        conn.execute(query, {
            "student_id": student_id,
            "college_id": college_id,
            "name": name,
            "phone": phone
        })
        return True
    except Exception as e:
        print(f"Error inserting into referral_college_professor: {str(e)}")
        raise

        

def insert_student_registration(conn, student_id: int, form_details: dict, submission_timestamp: Union[datetime.datetime, str]):
    """Insert data into intermediate.student_registration_details table."""
    try:
        if student_id is None:
            raise ValueError("student_id cannot be None")
        if not isinstance(form_details, dict):
            raise ValueError(f"form_details must be a dictionary, got {type(form_details)}")
        if submission_timestamp is None:
            raise ValueError("submission_timestamp cannot be None")

        expected_keys = {"motivation", "problems", "new_university_name", "New_College_Name", "Currently_Pursuing_Year"}
        missing_keys = expected_keys - form_details.keys()
        if missing_keys:
            raise ValueError(f"form_details missing expected keys: {missing_keys}")

        if isinstance(submission_timestamp, datetime.datetime):
            formatted_timestamp = submission_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(submission_timestamp, str):
            datetime.datetime.strptime(submission_timestamp, "%Y-%m-%d %H:%M:%S")  # will raise ValueError if invalid
            formatted_timestamp = submission_timestamp
        else:
            raise TypeError("submission_timestamp must be a datetime or string")

        query = text("""
            INSERT INTO intermediate.student_registration_details (student_id, form_details, registration_date)
            VALUES (:student_id, :form_details, :registration_date)
        """)
        conn.execute(query, {
            "student_id": student_id,
            "form_details": json.dumps(form_details),
            "registration_date": formatted_timestamp
        })
        return True
    except Exception as e:
        print(f"Error inserting into student_registration: {e}")
        raise



def insert_student_education(conn, student_id, education_course_id, subject_id, interest_subject_id, college_id, university_id, college_location_id, academic_year, course_duration):
    """Insert data into intermediate.student_education table."""
    try:
        # Validate inputs
        if student_id is None:
            raise ValueError("student_id cannot be None")
        if education_course_id is None:
            raise ValueError("education_course_id cannot be None")
        if college_location_id is None:
            raise ValueError("college_location_id cannot be None")
        if academic_year is None:
            raise ValueError("academic_year cannot be None")
        if course_duration is None:
            raise ValueError("course_duration cannot be None")
        if subject_id is not None and (not isinstance(subject_id, list) or not all(isinstance(id, int) for id in subject_id)):
            raise ValueError("subject_id must be a list of integers or None")

        # Convert subject_id list to PostgreSQL array format
        subject_id_array = f"{{{','.join(str(id) for id in subject_id)}}}" if subject_id and len(subject_id) > 0 else None

        # Academic year mapping
        academic_year_map = {
            "1st Year": 1,
            "2nd Year": 2,
            "3rd Year": 3,
            "4th Year": 4,
            "5th Year": 5
        }
        current_academic_year = academic_year_map.get(academic_year)
        if not current_academic_year:
            raise ValueError(f"Invalid academic_year: {academic_year}")

        # Cap current academic year if it exceeds course duration
        if current_academic_year > course_duration:
            current_academic_year = course_duration

        # Get current date
        now = datetime.datetime.now()
        current_year = now.year

        # Determine academic year start (July 1)
        academic_year_start = datetime.datetime(current_year, 7, 1)

        # If current date is before July 1, academic year started last year
        if now < academic_year_start:
            academic_start_year = current_year - 1
        else:
            academic_start_year = current_year

        # Calculate start_year and end_year based on academic year
        start_year = academic_start_year - (current_academic_year - 1)
        end_year = start_year + course_duration

        # Insert into database
        query = text("""
        INSERT INTO intermediate.student_education (
            student_id, education_course_id, subject_id, interest_subject_id, 
            college_id, university_id, college_location_id, start_year, end_year
        )
        VALUES (
            :student_id, :education_course_id, :subject_id, :interest_subject_id, 
            :college_id, :university_id, :college_location_id, :start_year, :end_year
        )
        """)
        conn.execute(query, {
            "student_id": student_id,
            "education_course_id": education_course_id,
            "subject_id": subject_id_array,
            "interest_subject_id": interest_subject_id,
            "college_id": college_id,
            "university_id": university_id,
            "college_location_id": college_location_id,
            "start_year": start_year,
            "end_year": end_year
        })
        return True
    except Exception as e:
        print(f"Error inserting into student_education: {str(e)}")
        raise