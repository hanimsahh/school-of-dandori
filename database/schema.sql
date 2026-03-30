
-- School of Dandori Database Schema
-- Create the main courses table

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT NOT NULL,
    title TEXT NOT NULL,
    instructor TEXT,
    location TEXT,
    cost INTEGER
);