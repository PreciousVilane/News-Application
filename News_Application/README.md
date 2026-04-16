# News_Application

A role-based news platform where readers can follow publishers and journalists, journalists can publish content, and editors manage approvals.

The application also provides a secure API that allows users and third-party clients to retrieve articles content based on subscriptions
and send a tweet when when a new article has been approved by an editor.

---

## What Can You Do With This App?

### Readers
- View approved news articles
- Subscribe to publishers
- Follow journalists
- Retrieve subscribed articles

### Journalists
- Create articles
- Edit or delete their own articles
- Publish newsletters

###  Editors
- Review submitted articles
- Approve or reject articles
- Edit or delete any article or newsletter

###  Third-Party API Clients
- Access articles based on user subscriptions using token authentication

##  Tech Stack
- Python
- Django
- Django REST Framework
- MySQL
- Token Authentication

## Installation & Setup

### Clone the Repository
Make sure **Git** is installed on your system, then run:

```
git clone https://github.com/your-username/news-application.git
cd news-application

# Installation
1. python -m pip install -r requirements.txt
2. python manage.py migrate
3. python manage.py createsuperuser
4. python manage.py runserver


## Create and Activate a Virtual Environment
python -m venv venv
venv\Scripts\activate


# Install Dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Configure the Database

Ensure MySQL is installed and running
Update your database credentials in settings.py

#  Apply Migrations
python manage.py migrate

# Create a Superuser (Admin)
python manage.py createsuperuser

# Run the Development Server
python manage.py runserver

The application will be available at:

http://127.0.0.1:8000/