# 🎓 Student Registration UI

The **Student Registration UI** is a Streamlit-based web application developed as an alternative to Google Forms for managing student registrations. It directly integrates with the organization’s database, allowing real-time registration and data management without manual data imports.

This application simplifies the registration process by directly storing all student information into structured tables in the **RDS database**, while dynamically fetching dropdown options (like college, course, location, subject, and university) from standard mapping tables.

---

## 🚀 Features

- 🧾 **Student Registration Form** — Clean, user-friendly interface for student registration.  
- 🗃️ **Direct Database Integration** — Student data is inserted directly into RDS intermediate schema tables.  
- 📊 **Dynamic Dropdowns** — Populates fields like college, course, subject, and university from mapping tables.  
- 🧩 **Configurable Setup** — Environment-based database connection and configuration handling.  
- ✅ **Validation** — Built-in validation for emails, phone numbers, and word count.  
- 💬 **Thank You Page** — Confirmation screen after successful registration.  
- 🔧 **Modular Design** — Structured, maintainable, and extendable codebase.

---

## 🧱 Database Structure

The student registration data is stored in the following **four main tables** within the intermediate schema:

- `student_details`  
- `student_registration`  
- `referral_college_professor`  
- `student_education`  

Additionally, data for dropdowns is dynamically fetched from **mapping tables**:

- `college_mapping`  
- `course_mapping`  
- `location_mapping`  
- `subject_mapping`  
- `university_mapping`

---

## 📂 Project Structure

├── image/
│   └── vslogo.png                 # Application logo and images
│
├── scripts/
│   ├── app.py                     # Main Streamlit application
│   ├── config.env                 # Environment variables and DB configuration
│   ├── requirements.txt           # Python dependencies
│   ├── run.sh                     # Application startup script
│   └── modules/                   # Supporting modules
│       ├── about_us.py            # Info about VigyanShaala & She For STEM initiative
│       ├── db_connection.py       # Loads config and establishes DB connection
│       ├── db_operation.py        # Functions to fetch and insert data into DB
│       ├── page_config.py         # Handles page title, icon, and logo setup
│       ├── thankyou.py            # Thank-you page displayed after form submission
│       └── validation.py          # Validation for email, phone number, word count
│
└── README.md                      # Project documentation
