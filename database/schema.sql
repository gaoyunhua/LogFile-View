-- Create the fields table
CREATE TABLE IF NOT EXISTS fields (
    field_name TEXT PRIMARY KEY,  -- Unique name for the field
    regex TEXT,                   -- Regular expression for extracting data
    visibility INTEGER,           -- 1 for visible, 0 for not visible
    sorted INTEGER                -- 1 for sorted, 0 for not sorted
);

-- Create the logs table
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each log entry
    raw TEXT                              -- Raw log line
);