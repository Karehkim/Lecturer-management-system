# Lecturer Management System

A comprehensive Flask-based web application for managing lecturers, courses, departments, students, and academic records.

## Features

- **User Authentication**: Login system for admins and lecturers
- **Dashboard**: Overview of system statistics and performance metrics
- **Lecturer Management**: Add, view, and manage lecturers
- **Course Management**: Create and assign courses to lecturers
- **Department Management**: Organize academic departments
- **Student Management**: Enroll students and track their progress
- **Attendance Tracking**: Mark and view student attendance
- **Leave Management**: Handle lecturer leave requests
- **Timetable**: View course schedules
- **Reporting**: Generate performance reports
- **Material Design UI**: Modern, responsive interface with dark mode

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd lecturer-management-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to `http://127.0.0.1:5000/`

5. Login with:
   - Username: `admin`
   - Password: `admin`

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: HTML, CSS, JavaScript, Material Design
- **Database**: SQLite

## Project Structure

```
lecturer-management-system/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── ...
├── static/                # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── README.md
```

## Usage

### For Lecturers
- Login with assigned credentials
- View personal dashboard with course information
- Mark student attendance
- Input student marks
- Apply for leave

### For Admins
- Full access to all features
- Manage lecturers, courses, departments, and students
- View system-wide reports

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.