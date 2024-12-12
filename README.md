# Workout Tracker API - Version 2

## Key Definitions in the Project (so far)
- **Workout**: A session of physical exercise or training.
- **Workout Log**: A workout that the user uploads, containing information related to the workout session.
- **Exercise**: A component of a workout, consisting of specific physical activities or training movements.


## Description
**Workout Tracker API** is a backend application designed to help users log their workouts, their own exercises, and track their exercises.
Built with **Django REST Framework**, this API supports secure user authentication and offers endpoints for managing workouts, exercises, and related information.
The API is intended to be easily extensible for future features such as goal tracking, workout templates, system exercises, and more.

---

## Features

- **User Related Operations**:
    - Starting from create to update to delete
    - Secure user authentication using token-based authentication.
- **Exercise Management**: Create, update, list, and delete exercises specific to each user.
- **Workout Logging**: Users can log workouts with the next features
    - Logging it with some details like description
    - Providing a flag to start a workout when user starts it
    - Providing a flag to end a workout when user ends it
    - handling almost every egde cases for the operations
    - Logging it with one or more exercise with its info as the next point
- **Exercise In Workout Logs**:
    - while creating or updating a workout log you can write an exercise name:
        - if it exists then it will be choosen
        - if not it will be created as a new exercise in the database and used immedietly
    - so the user do not have to wok with the exercise's endpoints, he can just work with workout logs for easy use
- **Searching and Filtering**:
    - You can search for exercise by name or any field
- **Tracking progress**:
    - You can track each exercise so you can see you progress in sets, reps, rest_time, and so on

---

## Tools & Technologies

- **Django**
- **Django REST Framework (DRF)**
- **PostgreSQL**
- **API Documentation**: Auto-generated documentation for all API endpoints using **DRF Spectacular**.
- **Linting**: Code linting using **flake8** to maintain code quality and consistency.
- **Unit Testing**:
    - Used rest_framework built-in testing
    - Used both Test Driven Development and Code-first
    - testing with over 150 unit tests to ensure functionality.
- **Git**

---

## Plans for next version

for next version I want to implement these feature:
- adding machines if need to the exercise in the workout log
- add more fields that add meanings to my models
- adding pictures for user and icons and exercises and machine if needed
-

---

## plans for final version
for the final version I want these features to be available:
- There will be a system-level exercises and user-level ones
- same with machines
- there will be workout log templates for famous wokrouts
- more information to keep track of not onlt exercises