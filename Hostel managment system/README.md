# Hostel Management System

A Django-based hostel management system with student and admin dashboards, room booking, profiles, course and room management, and permission requests.

## Features
- Home page with hostel rules and area images
- Student registration and login
- Admin login page
- Student dashboard with:
  - My Profile
  - My Room
  - Book Hostel
  - Room Details
  - Change Password
  - Request Permission to go out
- Admin dashboard with:
  - Total Students, Total Rooms, Total Courses
  - Manage Students
  - Manage Rooms
  - Manage Courses
  - Manage Permissions
- Permission feature for parent/proctor/incharge approval
- Static CSS styling and responsive Bootstrap UI

## Setup
1. Open a terminal in the project folder.
2. Create and activate the virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

5. Create an admin user:

```powershell
python manage.py createsuperuser
```

6. Start the server:

```powershell
python manage.py runserver
```

7. Open browser at `http://127.0.0.1:8000/`.

## Notes
- User login uses the default Django `User` model.
- Student information is stored in `hostel_app.models.Student`.
- Permission requests are stored in `hostel_app.models.Permission`.
- Media uploads are saved to the `media/` folder.

## Useful URLs
- Home: `/`
- Register: `/register/`
- User Login: `/login/`
- Admin Login: `/admin_login/`
- Admin dashboard: `/admin_dashboard/`
- Student dashboard: `/student_dashboard/`

## Test Accounts

### Admin Login
- Go to: http://127.0.0.1:8000/admin_login/
- Username: `admin`
- Password: `admin@123`
- Access admin dashboard to manage students, rooms, courses, and permissions

### Student Test Account
- Username: `teststudent`
- Password: `testpass123`
- Login at: http://127.0.0.1:8000/login/

### Create New Student Accounts
- Register at: http://127.0.0.1:8000/register/
- Fill in the required fields (marked with *)
- Optional fields can be filled later in profile
- After registration, use your chosen username and password to login

## Login Issues
- If login fails, check that you're using the correct username and password
- Usernames are case-sensitive
- Error messages will appear on the login page if credentials are invalid
- Make sure you're using the correct login page (user login vs admin login)
