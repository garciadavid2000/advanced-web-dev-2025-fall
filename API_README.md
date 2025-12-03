# API Documentation

This document details the API endpoints available in the application, organized by controller.

## Auth Controller (`/auth`)

Handles authentication via Google OAuth and session management.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/login` | Initiates the Google OAuth login flow. Redirects to Google's login page. | No |
| `GET` | `/callback` | Handles the callback from Google OAuth. Creates a user session and redirects to the frontend. | No |
| `GET` | `/logout` | Clears the user session. | No |
| `POST` | `/test-login` | **Test Only**. Creates an authenticated session for E2E testing. Requires `TESTING=True` config. | No |
| `POST` | `/calendar/export` | Exports all user tasks to their Google Calendar. | Yes |

## Task Controller (`/tasks`)

Manages task creation, retrieval, updates, and deletion.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/` | Create a new task. Expects JSON body with `title`, `frequency`, and `category`. | Yes |
| `GET` | `/` | Get all tasks for the current user, grouped by due date. | Yes |
| `PUT` | `/<task_id>` | Update a task's title. Expects JSON body with `title`. | Yes |
| `DELETE` | `/<task_id>` | Delete a task. | Yes |
| `POST` | `/<occurrence_id>/complete` | Mark a specific task occurrence as completed. | Yes |

## User Controller (`/users`)

Manages user data.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/current` | Get the currently authenticated user's details. | No (Returns 401 if not auth) |
| `POST` | `/` | Create a new user manually. Expects JSON body with `email` and `name`. | No |
| `GET` | `/<user_id>` | Get a specific user's details by ID. | No |
| `GET` | `/` | Get a list of all users. | No |
| `PUT` | `/<user_id>` | Update a user's data. Expects JSON body. | No |
| `DELETE` | `/<user_id>` | Delete a user by ID. | No |
