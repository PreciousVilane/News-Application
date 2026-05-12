# News Publishing & Subscription Platform

## Project Overview
The News Publishing & Subscription Platform is a full-stack Django web application designed to simulate a real-world digital news ecosystem where:

1. Journalists create and manage articles
2. Editors review and approve content
3. Readers subscribe to publishers and journalists
4.  Users access personalized newsletters
5. Role-based permissions control platform access
6.  APIs provide subscribed news feeds
7. Approved articles can be shared to Twitter/X
8. The platform demonstrates advanced Django concepts including:
9. Custom authentication systems
10. Role-based access control (RBAC)
11. CRUD functionality
12.Django Groups & Permissions
13. REST API development with Django REST Framework
14. Many-to-Many & ForeignKey relationships
15. Protected views & authorization
16. Newsletter systems
17. Twitter-integrated news systems

## Features

1. Authentication & User Roles
The application uses a Custom User Model with three distinct roles:
RoleCapabilities * ReaderRead approved articles & subscribe to content. * JournalistCreate and manage articles/newsletters. * EditorReview, approve, edit, and manage all content

2.Authentication Features
- User Registration
- Login & Logout
- Role-based access control
- Django Groups integration
- Permission-based route protection

## Article Management System
* Journalists Can
  - Create articles
  - Edit their own articles
  - Delete their own articles
  - Manage independent publications

* Editors Can
 - View all articles
 - Approve pending articles
  - Edit any article
  - Delete any article

* Readers Can
- View approved articles only
-Access subscribed content
-Read article details
-View newsletters from subscribed publishers
-Access personalized newsletter feeds


## REST API Integration
The platform includes Django REST Framework APIs for accessing subscribed articles.
API Features

1. Authenticated API access
2. Reader-specific article feeds
3. Approved article filtering
4. JSON responses


## Twitter/X Integration
Approved articles can automatically be posted to Twitter/X using a custom tweet integration.
Features
Tweets approved articles
Prevents unapproved content from being posted
API-triggered posting system



## Tech Stack
* Backend
  - Python
  - Django
  - Django REST Framework
  - Database
  - SQLite
  - Authentication & Authorization
  - Django Authentication System
  - Django Groups & Permissions


* Frontend
 - HTML
 - Django Templates
 - CSS
 - APIs
 - REST API
 - JSON Responses


## License
This project is open-source and available under the MIT License.

## Author
Built as a full-stack Django portfolio project to demonstrate advanced backend development skills including authentication systems, role-based permissions, REST APIs, subscription-based content delivery, newsletter management, and real-world news publishing workflows.
