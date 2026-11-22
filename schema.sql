-- Hostel Management System Database Schema (SQLite)

PRAGMA foreign_keys = ON;

-- Users Table (Students, Administrators & Parents)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,           -- Roll number for students, 'admin' for warden, or username/phone for parents
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'admin', 'parent')),
    phone TEXT,
    guardian_name TEXT,
    guardian_phone TEXT,
    branch TEXT,                             -- e.g., 'Computer Engineering' (for students)
    semester INTEGER,                        -- e.g., 3 (for students)
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parent-Student Mapping Table (Links a Parent to one or more Wards)
CREATE TABLE IF NOT EXISTS parent_students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    relationship TEXT DEFAULT 'Parent/Guardian',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(parent_id, student_id)
);

-- Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number TEXT UNIQUE NOT NULL,        -- e.g., 'A-101', 'B-204'
    block TEXT NOT NULL,                     -- e.g., 'Block A', 'Block B'
    floor INTEGER NOT NULL,                  -- e.g., 1, 2, 3
    capacity INTEGER NOT NULL DEFAULT 2,     -- Max bed capacity
    room_type TEXT DEFAULT 'Non-AC' CHECK(room_type IN ('AC', 'Non-AC')),
    monthly_rent REAL DEFAULT 4500.0,
    status TEXT DEFAULT 'Available' CHECK(status IN ('Available', 'Occupied', 'Maintenance')),
    description TEXT
);

-- Room Allotments Table
CREATE TABLE IF NOT EXISTS room_allotments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,         -- One active room per student
    room_id INTEGER NOT NULL,
    bed_number INTEGER NOT NULL,             -- Bed 1, Bed 2, etc.
    allotted_date DATE DEFAULT (DATE('now')),
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Vacated')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- Notices Table
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'General' CHECK(category IN ('Urgent', 'General', 'Mess', 'Event', 'Maintenance', 'Rules')),
    is_pinned INTEGER DEFAULT 0,            -- 1 for pinned at top
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Mess Menu Table
CREATE TABLE IF NOT EXISTS mess_menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day_of_week TEXT NOT NULL CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    meal_type TEXT NOT NULL CHECK(meal_type IN ('Breakfast', 'Lunch', 'Snacks', 'Dinner')),
    items TEXT NOT NULL,                     -- Comma-separated or descriptive menu items
    timings TEXT NOT NULL,                   -- e.g., '07:30 AM - 09:30 AM'
    special_note TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(day_of_week, meal_type)
);

-- Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    room_number TEXT,                        -- Room where maintenance is required
    category TEXT NOT NULL CHECK(category IN ('Plumbing', 'Electrical', 'WiFi', 'Furniture', 'Cleanliness', 'Other')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')),
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Resolved', 'Rejected')),
    admin_remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Leave / Outpass Requests Table (Two-tier verification: Parent Consent + Warden Clearance)
CREATE TABLE IF NOT EXISTS outpasses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    departure_time DATETIME NOT NULL,
    expected_return DATETIME NOT NULL,
    actual_return DATETIME,
    reason TEXT NOT NULL,
    destination TEXT NOT NULL,
    emergency_contact TEXT NOT NULL,
    parent_approval TEXT DEFAULT 'Pending' CHECK(parent_approval IN ('Pending', 'Approved', 'Rejected')),
    parent_remarks TEXT,
    parent_action_at TIMESTAMP,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Rejected', 'Returned')),
    admin_remarks TEXT,
    reviewed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Hostel Fees and Payments Table
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    fee_type TEXT NOT NULL CHECK(fee_type IN ('Hostel Rent', 'Mess Fee', 'Maintenance', 'Security Deposit', 'Other')),
    amount REAL NOT NULL,
    due_date DATE NOT NULL,
    paid_date TIMESTAMP,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Paid', 'Overdue')),
    payment_method TEXT,
    transaction_ref TEXT,
    receipt_number TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Daily Night Curfew & Roll Call Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Late Entry', 'Absent', 'On Outpass')),
    check_in_time TEXT,
    remarks TEXT,
    marked_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(user_id, date)
);

-- Parent Inquiries & Warden Communication Desk
CREATE TABLE IF NOT EXISTS parent_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    category TEXT DEFAULT 'General' CHECK(category IN ('General', 'Health', 'Leave', 'Fee', 'Mess', 'Discipline')),
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Resolved')),
    admin_reply TEXT,
    replied_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    replied_at TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (replied_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_parent_students ON parent_students(parent_id, student_id);
CREATE INDEX IF NOT EXISTS idx_rooms_block ON rooms(block);
CREATE INDEX IF NOT EXISTS idx_notices_pinned ON notices(is_pinned, created_at);
CREATE INDEX IF NOT EXISTS idx_complaints_user ON complaints(user_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_outpasses_user ON outpasses(user_id);
CREATE INDEX IF NOT EXISTS idx_outpasses_status ON outpasses(status);
CREATE INDEX IF NOT EXISTS idx_outpasses_parent_app ON outpasses(parent_approval);
CREATE INDEX IF NOT EXISTS idx_fees_user ON fees(user_id);
CREATE INDEX IF NOT EXISTS idx_fees_status ON fees(status);
CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date);
CREATE INDEX IF NOT EXISTS idx_parent_queries_parent ON parent_queries(parent_id);
