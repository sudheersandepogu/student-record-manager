# Student Record Manager

A simple Student Record Manager web application built using **Python**, **Flask**, **HTML**, and **CSS**. This project allows users to manage student records by adding, viewing, searching, editing, and deleting student information. It also validates email addresses using regular expressions and stores data locally.

---

## Overview

The Student Record Manager is designed as a beginner-friendly CRUD (Create, Read, Update, Delete) application. It demonstrates the fundamentals of Flask development, file handling, regular expressions, exception handling, and frontend integration.

---

## Features

- Add new student records
- View all students
- Search students by ID or Name
- Update student information
- Delete student records
- Email validation using Regular Expressions (Regex)
- Store student records in a local file
- Read records from the file automatically
- Handle invalid user input using exception handling
- Simple and responsive user interface
- Flask-based backend

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend Programming |
| Flask | Web Framework |
| HTML5 | Structure |
| CSS3 | Styling |
| Regular Expressions (Regex) | Email Validation |
| File Handling | Data Storage |
| Exception Handling | Error Management |

---

## Project Structure

```text
student-record-manager/
│
├── app.py
├── students.txt
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── add_student.html
│   ├── edit_student.html
│   └── search.html
│
├── static/
│   └── style.css
│
└── utils/
    └── validation.py
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/sudheersandepogu/student-record-manager.git
```

### Navigate to the Project

```bash
cd student-record-manager
```

### Create a Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000/
```

---

## Application Workflow

1. Open the application.
2. Add a new student by entering:
   - Student ID
   - Name
   - Email
   - Address
3. The application validates the email format using Regex.
4. Student details are stored in the local file.
5. View all saved student records.
6. Search students by ID or Name.
7. Edit existing student details.
8. Delete unwanted student records.

---

## Email Validation

The application validates email addresses using Regular Expressions.

Example of a valid email:

```
student@example.com
```

Invalid emails are rejected with an appropriate error message.

---

## Data Storage

Student information is stored in a local text file.

Example:

```
ID: 101
Name: John Doe
Email: john@example.com
Address: Hyderabad
------------------------
```

---

## Exception Handling

The application handles common errors such as:

- Empty input fields
- Invalid email format
- Duplicate student IDs
- Student not found
- File not found
- Invalid user input

---

## Future Enhancements

- SQLite/MySQL database integration
- User authentication
- Dashboard with statistics
- Pagination
- Export data to Excel
- Export data to PDF
- Student photo upload
- Responsive Bootstrap UI
- REST API integration

---

## Author

**Sudheer Roy**

GitHub:
https://github.com/sudheersandepogu

---

## License

This project is developed for educational and learning purposes.
