
# Hospital Management System

This project is a Django-based Hospital Management System, designed to handle the administrative tasks of a hospital, including patient management, doctor management, appointment scheduling, and more.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+**: Make sure Python is installed on your machine. You can download it from [Python's official website](https://www.python.org/downloads/).
- **pip**: Ensure pip is installed for managing Python packages.
- **Virtualenv**: It's recommended to use virtual environments to manage dependencies.

## Installation

Follow these steps to set up the project:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/hospital-management-system.git
   cd hospital-management-system
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv env
   source env/bin/activate   # On Windows use `env\Scripts\activate`
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional but recommended for accessing the Django admin):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Project

To start the development server, run:

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

## Project Structure

Here is an overview of the project's structure:

```
hospital-management-system/
│
├── hospital/
│   ├── migrations/           # Database migrations
│   ├── static/               # Static files (CSS, JavaScript, images)
│   ├── templates/            # HTML templates
│   ├── admin.py              # Django admin customization
│   ├── apps.py               # Application configuration
│   ├── models.py             # Database models
│   ├── views.py              # Views handling the requests
│   └── urls.py               # URL routing for the hospital app
│
├── hospital_management/      # Main project directory
│   ├── settings.py           # Project settings
│   ├── urls.py               # URL routing for the entire project
│   └── wsgi.py               # WSGI entry point for deployment
│
├── manage.py                 # Command-line utility for Django
├── requirements.txt          # List of Python packages required for the project
└── README.md                 # This file
```

## Usage

After running the project, you can:

- Access the Django admin at `http://127.0.0.1:8000/admin/`.
- Manage doctors, patients, and appointments through the admin interface.
- Explore and extend the project by adding more features or customizing existing ones.

## Troubleshooting

### Common Issues

1. **Database Migrations**: If you encounter issues with database migrations, try running:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Static Files Not Loading**: Ensure you have collected the static files by running:
   ```bash
   python manage.py collectstatic
   ```

3. **Server Not Starting**: Check if another process is using port 8000 or try running the server on a different port:
   ```bash
   python manage.py runserver 8080
   ```

For further assistance, consult the [Django documentation](https://docs.djangoproject.com/en/stable/).
