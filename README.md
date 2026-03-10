# Pilates Studio Booking System - REST API & Database

## 1. Project Overview
This repository contains the middleware REST API and backend database schema for an enterprise-style Pilates booking system. It acts as the central hub for all business rules, data validation, and secure data persistence.

## 2. Architecture & Technology Stack
* **Middleware Framework:** Django / Django REST Framework.
* **Backend Database:** PostgreSQL.
* **Layer Responsibilities:** This layer is exclusively responsible for authentication, authorisation, business logic, server-side validation, and communication with the persistent data storage.

## 3. Core API Features & Business Logic
* **Security & Auth:** Secure password storage and protected API endpoints using token-based authentication (e.g., JWT).
* **Booking CRUD Operations:** Endpoints to create, read, update, and delete bookings.
* **Business Rules:** Implementation of availability checks to prevent double-booking of Pilates classes or instructors.
* **Administrative Features:** Endpoints to support administrative booking management and enforce business rules like booking cut-off times.

## 4. External Integrations
* **Email Services:** Integration with external services like SendGrid to handle automated email notifications, including password reset workflows and booking confirmations.
* **Media Storage:** Integration with cloud-based media storage like Cloudinary to handle user-uploaded files, such as profile images.

## 5. Testing Strategy
* The system includes comprehensive automated testing to ensure enterprise-level quality.
* The test suite consists of unit tests and API tests covering core domain logic, booking validation, and authentication workflows.

## 6. Deployment & CI/CD
* The API and database will be deployed using Render.
* Deployment practices include the secure handling of environment variables (e.g., database credentials, secret keys) and evidence of CI/CD pipeline integration.
* The database is configured to remain active and accessible for at least three weeks post-submission.

## 7. AI Usage Acknowledgement
*(Note to Developer: Update this section before final submission)*
This module is classified as Yellow under institutional AI guidance. AI tools were utilized for drafting docstrings, generating initial test cases, and debugging complex Django ORM queries. All generated code was manually reviewed, refined, and tested to ensure a complete understanding of the underlying architecture.
