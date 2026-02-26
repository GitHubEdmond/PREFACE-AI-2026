# 📒 Simple Note Taking App - SPEC

## Overview
A lightweight web app for creating, storing, and searching notes.  
Features:
- User authentication (login/signup)
- Create, read, update, delete (CRUD) notes
- Search notes by keyword
- Supabase as backend (auth + database)
- Each note message displays the **user’s name** alongside the content

---

## Tech Stack
- **Frontend**: React (Vite or Next.js for simplicity)
- **Backend**: Supabase (Auth + Postgres DB)
- **Styling**: TailwindCSS (optional, for quick UI)
- **Deployment**: Vercel/Netlify

---

## User Stories
- As a user, I can **sign up** and **log in** securely.
- As a user, I can **set a display name** (username).
- As a user, I can **add new notes** with a title and body, and my **username** is shown on the note.
- As a user, I can **view all my notes** in a list.
- As a user, I can **search notes** by keyword in title or body.
- As a user, I can **edit or delete notes** I created.

---

## Database Schema (Supabase - Postgres)

### Table: `profiles`
| Column       | Type        | Constraints                          |
|--------------|-------------|--------------------------------------|
| id           | uuid        | primary key, references auth.users.id |
| username     | text        | unique, not null                     |
| created_at   | timestamp   | default now()                        |

### Table: `notes`
| Column       | Type        | Constraints                          |
|--------------|-------------|--------------------------------------|
| id           | uuid        | primary key, default uuid_generate_v4() |
| user_id      | uuid        | foreign key → auth.users.id          |
| title        | text        | not null                             |
| content      | text        | not null                             |
| created_at   | timestamp   | default now()                        |
| updated_at   | timestamp   | default now()                        |

---

## Authentication
- Supabase Auth handles signup/login.
- Email + password flow.
- Session stored in local storage or Supabase client.
- On signup, user must set a **username** stored in `profiles`.

---

## API Functions (via Supabase client)
- `signUp(email, password, username)`
- `signIn(email, password)`
- `signOut()`
- `getNotes(user_id)` → includes `username` from `profiles`
- `createNote(user_id, title, content)`
- `updateNote(note_id, title, content)`
- `deleteNote(note_id)`
- `searchNotes(user_id, query)` → SQL `ILIKE` on title + content

---

## UI Wireframe (Conceptual)
- **Login Page** → email/password form
- **Signup Page** → email/password + username field
- **Notes Dashboard** → list of notes + search bar
  - Each note shows: `username`, `title`, `content`, `created_at`
- **Note Editor** → form for title + content
- **Search Results** → filtered notes list

---

## Search Functionality
- Input field at top of dashboard.
- Query runs against `title` and `content` using Supabase SQL:
  ```sql
  SELECT notes.*, profiles.username
  FROM notes
  JOIN profiles ON notes.user_id = profiles.id
  WHERE notes.user_id = 'current_user'
  AND (notes.title ILIKE '%query%' OR notes.content ILIKE '%query%');
