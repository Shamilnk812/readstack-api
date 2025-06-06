# ReadStack - Book Management System API

ReadStack is a powerful backend API system designed for managing books, users, and reading lists. Built using Django REST Framework (DRF), this project offers secure user authentication with JWT, efficient book management, and flexible reading list functionality tailored for user preferences.
---

## Repository Overview

This repository contains the complete backend API implementation for:

- User registration, authentication, and profile management
- Book uploading, listing, and soft deletion
- Reading list creation, modification, and reordering
- Secure interaction between users and book-related content

---

## Features

### User Management
- Register new users with unique usernames and email addresses
- Secure login and logout using JWT authentication
- Manage and update user profile details

### Book Management
- Add new books with title, authors, genre, publication date, and optional description
- Soft delete books (no permanent deletion)
- Upload book files (PDF, etc.)
- View all uploaded books (available to all users)

### Reading Lists
- Create and manage personalized reading lists
- Add or remove books from reading lists
- Reorder books in a user-defined sequence
- Prevent duplicate books in the same list

### User Interactions
- Associate books with specific reading lists
- Remove books from lists when desired
- Fetch all items from a specific reading list

---

## ⚙️ Tech Stack

- **Backend Framework**: Django REST Framework (DRF)
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Language**: Python

---

## ⚙️ How to Set Up

### Clone the repository

```bash
git clone https://github.com/Shamilnk812/readstack-api.git
```

### Navigate to root directory

```bash
cd backend
```

### Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate #linux
venv/scripts/activate  # windows
```

### Install the dependencies

```bash
pip install -r requirements.txt
```

### Create a .env file in the root directory and add your environment variables

```bash
SECRET_KEY=your-django-secret-key
DEBUG=True

DB_NAME=readstack_db
DB_USER=readstack_user
DB_PASSWORD=strong_dummy_password
DB_HOST=localhost
DB_PORT=5432
```

### Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run the development server using Daphne

```bash
python manage.py runserver
```

- Open your browser and go to http://localhost:8000
