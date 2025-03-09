# Overview

This project is a backend system designed during my internship, focusing on building a scalable and efficient API using Django Rest Framework (DRF). The application integrates authentication, database management, background tasks, search functionality, and real-time notifications.

# features
users crud

products/products-details crud 

product media crud

collections/collections-details crud 


# Technologies Used

Django & Django REST Framework – Core backend framework.

Docker – Containerization for environment consistency.

PostgreSQL – Database for persistent data storage.

Redis – Used for caching and Celery task queue.

Celery & Celery-Beat – Handling background tasks and scheduled jobs.

Elasticsearch – Implementing efficient product search.

Backblaze B2 – Cloud storage for product media.

OAuth2 Authentication – Secure user authentication.

GraphQL – Alternative API query language for optimized data retrieval.

WebSockets (Django Channels) – Real-time notifications for stock updates.

Unit Testing (Pytest & DRF TestCase) – Ensuring API stability.