"""
Seed realistic demonstration data for Hostel Management System.
Includes Students, Administrators, Parents, Rooms, Allotments, Notices,
Mess Schedules, Maintenance Complaints, 2-Tier Outpasses, Fee Invoices,
Night Curfew Attendance, and Parent Inquiries.
Run: python seed_data.py
"""

import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash
from database import DATABASE, init_db

def hash_pw(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def seed():
    # If database file exists, safely reset for clean seed
    if os.path.exists(DATABASE):
        try:
            os.remove(DATABASE)
        except Exception:
            pass
    # Reinitialize tables
    init_db()
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print("Seeding users...")
    # 1. Admin
    admin_pw = hash_pw("admin123")
    cur.execute("""
        INSERT INTO users (username, full_name, email, password_hash, role, phone, guardian_name, guardian_phone, branch, semester, gender)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("admin", "Dr. Rajeshwar Sharma (Chief Warden)", "warden@hostel.edu", admin_pw, "admin",
          "+91 98111 22334", "Admin Office", "+91 98111 22335", "Administration", 0, "Male"))
    admin_id = cur.lastrowid

    # 2. Students (10 students enrolled)
    student_pw = hash_pw("student123")
    students_data = [
        ("25001003043", "Jiyansh Sardana", "jiyansh@hostel.edu", student_pw, "student",
         "+91 98765 43210", "Kapil Sardana", "+91 98765 00001", "Computer Engineering", 3, "Male"),
        ("25001003044", "Rahul Sharma", "rahul@hostel.edu", student_pw, "student",
         "+91 98765 43211", "Manoj Sharma", "+91 98765 00002", "Computer Engineering", 3, "Male"),
        ("25001003045", "Aarav Mehta", "aarav@hostel.edu", student_pw, "student",
         "+91 98765 43212", "Sunil Mehta", "+91 98765 00003", "Information Technology", 3, "Male"),
        ("25001003046", "Priya Verma", "priya@hostel.edu", student_pw, "student",
         "+91 98765 43213", "Virender Verma", "+91 98765 00004", "Electronics & Comm.", 3, "Female"),
        ("25001003047", "Sneha Kapoor", "sneha@hostel.edu", student_pw, "student",
         "+91 98765 43214", "Deepak Kapoor", "+91 98765 00005", "Computer Engineering", 3, "Female"),
        ("25001003048", "Ananya Singh", "ananya@hostel.edu", student_pw, "student",
         "+91 98765 43215", "Rajesh Singh", "+91 98765 00006", "Mechanical Engineering", 3, "Female"),
        ("25001003049", "Rohan Gupta", "rohan@hostel.edu", student_pw, "student",
         "+91 98765 43216", "Sanjay Gupta", "+91 98765 00007", "Electrical Engineering", 3, "Male"),
        ("25001003050", "Ishita Malik", "ishita@hostel.edu", student_pw, "student",
         "+91 98765 43217", "Harish Malik", "+91 98765 00008", "Civil Engineering", 5, "Female"),
        ("25001003051", "Kabir Das", "kabir@hostel.edu", student_pw, "student",
         "+91 98765 43218", "Kamal Das", "+91 98765 00009", "Computer Engineering", 5, "Male"),
        ("25001003052", "Tanya Batra", "tanya@hostel.edu", student_pw, "student",
         "+91 98765 43219", "Ashok Batra", "+91 98765 00010", "Information Technology", 1, "Female")
    ]
    student_ids = {}
    for data in students_data:
        cur.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role, phone, guardian_name, guardian_phone, branch, semester, gender)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        student_ids[data[0]] = cur.lastrowid

    # 3. Parents
    print("Seeding parent accounts...")
    parent_pw = hash_pw("parent123")
    parents_data = [
        # (username, full_name, email, phone, ward_roll, relation)
        ("parent_25001003043", "Mr. Kapil Sardana", "kapil.sardana@example.com", "+91 98765 00001", "25001003043", "Father"),
        ("parent_25001003044", "Mr. Manoj Sharma", "manoj.sharma@example.com", "+91 98765 00002", "25001003044", "Father"),
        ("parent_25001003046", "Mr. Virender Verma", "virender.verma@example.com", "+91 98765 00004", "25001003046", "Father"),
        ("parent_25001003049", "Mr. Sanjay Gupta", "sanjay.gupta@example.com", "+91 98765 00007", "25001003049", "Father"),
        ("parent_25001003050", "Mr. Harish Malik", "harish.malik@example.com", "+91 98765 00008", "25001003050", "Father")
    ]
    parent_ids = {}
    for p_user, p_name, p_email, p_phone, ward_roll, relation in parents_data:
        cur.execute("""
            INSERT INTO users (username, full_name, email, password_hash, role, phone, guardian_name, guardian_phone, branch, semester, gender)
            VALUES (?, ?, ?, ?, 'parent', ?, ?, ?, 'Guardian', 0, 'Male')
        """, (p_user, p_name, p_email, parent_pw, p_phone, p_name, p_phone))
        pid = cur.lastrowid
        parent_ids[p_user] = pid
        cur.execute("""
            INSERT INTO parent_students (parent_id, student_id, relationship)
            VALUES (?, ?, ?)
        """, (pid, student_ids[ward_roll], relation))

    # 4. Rooms
    print("Seeding rooms...")
    rooms_data = [
        ("A-101", "Block A", 1, 2, "Non-AC", 4500.0, "Occupied", "Ground floor corner room with garden view"),
        ("A-102", "Block A", 1, 2, "Non-AC", 4500.0, "Occupied", "Quiet wing room with high ceilings"),
        ("A-103", "Block A", 1, 3, "Non-AC", 4200.0, "Occupied", "Triple sharing spacious corner room"),
        ("A-201", "Block A", 2, 2, "AC", 6500.0, "Available", "Second floor AC room facing central courtyard"),
        ("A-202", "Block A", 2, 2, "AC", 6500.0, "Available", "Well-ventilated double occupancy room"),
        ("B-101", "Block B", 1, 2, "Non-AC", 4500.0, "Occupied", "Ground floor room near common reading hall"),
        ("B-102", "Block B", 1, 2, "Non-AC", 4500.0, "Occupied", "First floor room with attached balcony"),
        ("B-201", "Block B", 2, 2, "AC", 6800.0, "Occupied", "Second floor AC room with study desks"),
        ("B-202", "Block B", 2, 2, "AC", 6800.0, "Available", "Deluxe room with superior cooling and natural light"),
        ("C-101", "Block C", 1, 2, "Non-AC", 4200.0, "Available", "Quiet block room ideal for competitive exam study")
    ]
    room_ids = {}
    for r in rooms_data:
        cur.execute("""
            INSERT INTO rooms (room_number, block, floor, capacity, room_type, monthly_rent, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, r)
        room_ids[r[0]] = cur.lastrowid

    # 5. Room Allotments
    print("Seeding room allotments...")
    allotments = [
        (student_ids["25001003043"], room_ids["A-101"], 1, "2026-08-01"),
        (student_ids["25001003044"], room_ids["A-101"], 2, "2026-08-01"),
        (student_ids["25001003045"], room_ids["A-102"], 1, "2026-08-02"),
        (student_ids["25001003049"], room_ids["A-102"], 2, "2026-08-02"),
        (student_ids["25001003046"], room_ids["B-101"], 1, "2026-08-01"),
        (student_ids["25001003047"], room_ids["B-101"], 2, "2026-08-01"),
        (student_ids["25001003048"], room_ids["B-102"], 1, "2026-08-04"),
        (student_ids["25001003051"], room_ids["A-103"], 1, "2026-08-06"),
        (student_ids["25001003050"], room_ids["B-201"], 1, "2026-08-03"),
        (student_ids["25001003052"], room_ids["B-201"], 2, "2026-08-03")
    ]
    for user_id, room_id, bed, allot_date in allotments:
        cur.execute("""
            INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
            VALUES (?, ?, ?, ?, 'Active')
        """, (user_id, room_id, bed, allot_date))

    print("Seeding notices...")
    notices_data = [
        ("Hostel Curfew & Biometric Gate Rules (Fall 2026)",
         "All residents are hereby informed that the hostel main gate closes strictly at 09:30 PM. Any entry after 09:30 PM will require a pre-approved digital outpass and written permission from the Chief Warden. Biometric machines at the security booth will log all entry/exit timestamps. Late entries without permission will lead to parental intimation and disciplinary action.",
         "Rules", 1, admin_id),

        ("High-Speed Wi-Fi Router Upgrades in Block A & B",
         "The campus IT center will be upgrading access point hardware on 2nd and 3rd floors of both blocks on Saturday between 10:00 AM and 02:00 PM. Internet connectivity may face intermittent disruption during this window. We appreciate your cooperation.",
         "Maintenance", 1, admin_id),

        ("Upcoming Mess Committee Meeting & Special Feast Poll",
         "The monthly Mess Committee consultation is scheduled for Wednesday at 05:00 PM in the Common Hall. Student representatives from each floor are requested to attend. A survey poll for next Sunday's special dinner feast menu is now open at the admin reception desk.",
         "Mess", 0, admin_id),

        ("Inter-Hostel Badminton & Table Tennis Tournament",
         "Registrations are now open for the Annual Inter-Hostel Indoor Sports Tournament! Matches will commence next Friday evening. Interested students can register their teams at the sports room by Thursday noon. Exciting trophies and medals await!",
         "Event", 0, admin_id),

        ("Water Tank Cleaning & Solar Geyser Maintenance",
         "Overhead water tanks will undergo sanitization on Tuesday morning. Hot water supply from solar geysers will resume after 03:00 PM. Please store essential water in advance.",
         "General", 0, admin_id)
    ]
    for n in notices_data:
        cur.execute("""
            INSERT INTO notices (title, content, category, is_pinned, created_by)
            VALUES (?, ?, ?, ?, ?)
        """, n)

    print("Seeding weekly mess menu...")
    mess_schedule = [
        ("Monday", "Breakfast", "Aloo Paratha, Curd, Pickle, Boiled Eggs / Banana, Tea / Coffee", "07:30 AM - 09:30 AM", "Fresh mint chutney available"),
        ("Monday", "Lunch", "Rajma Masala, Steamed Rice, Tawa Roti, Mix Veg Dry, Boondi Raita, Salad", "12:30 PM - 02:30 PM", "Special Punjabi style Rajma"),
        ("Monday", "Snacks", "Veg Pakoras, Green Chutney, Tea / Milk", "05:00 PM - 06:15 PM", "Evening tea break"),
        ("Monday", "Dinner", "Dal Tadka, Seasonal Sabzi, Paneer Bhurji / Egg Curry, Phulka, Rice, Gulab Jamun", "07:45 PM - 09:45 PM", "Sweet dish included"),

        ("Tuesday", "Breakfast", "Idli Sambhar, Coconut Chutney, Medu Vada, Tea / Coffee", "07:30 AM - 09:30 AM", "South Indian special"),
        ("Tuesday", "Lunch", "Kadhi Pakora, Jeera Rice, Chapati, Aloo Gobhi, Roasted Papad, Salad", "12:30 PM - 02:30 PM", "Authentic Kadhi"),
        ("Tuesday", "Snacks", "Aloo Samosa, Tomato Ketchup, Tea / Milk", "05:00 PM - 06:15 PM", "Crispy samosas"),
        ("Tuesday", "Dinner", "Dal Makhani, Mix Veg, Shahi Paneer / Chicken Masala, Butter Naan, Rice, Ice Cream", "07:45 PM - 09:45 PM", "Chef recommendation"),

        ("Wednesday", "Breakfast", "Poha with Roasted Peanuts, Sev, Sprouts Salad, Boiled Eggs, Tea / Coffee", "07:30 AM - 09:30 AM", "Healthy breakfast"),
        ("Wednesday", "Lunch", "Chole Bhature / Kulche, Pulao, Cucumber Raita, Pickled Onions, Green Salad", "12:30 PM - 02:30 PM", "Delhi style chole"),
        ("Wednesday", "Snacks", "Bread Roll, Mint Chutney, Tea / Milk", "05:00 PM - 06:15 PM", "Crunchy bread rolls"),
        ("Wednesday", "Dinner", "Yellow Moong Dal, Bhindi Masala, Dum Aloo, Phulka, Steamed Rice, Fruit Custard", "07:45 PM - 09:45 PM", "Light healthy dinner"),

        ("Thursday", "Breakfast", "Masala Uttapam, Tomato Onion Chutney, Sambhar, Boiled Eggs, Tea / Coffee", "07:30 AM - 09:30 AM", "Steamed South Indian"),
        ("Thursday", "Lunch", "Lauki Kofta Curry, Arhar Dal Fry, Steamed Rice, Tawa Roti, Roasted Papad", "12:30 PM - 02:30 PM", "Homestyle nutritious meals"),
        ("Thursday", "Snacks", "Sweet Corn Chaat / Bhel, Tea / Milk", "05:00 PM - 06:15 PM", "Healthy steamed snack"),
        ("Thursday", "Dinner", "Paneer Butter Masala / Chicken Curry, Jeera Rice, Butter Roti, Dal Tadka, Moong Dal Halwa", "07:45 PM - 09:45 PM", "Special weekend warm-up feast"),

        ("Friday", "Breakfast", "Gobhi / Methi Paratha, Curd, Butter, Boiled Eggs / Seasonal Fruit, Tea / Coffee", "07:30 AM - 09:30 AM", "Stuffed winter parathas"),
        ("Friday", "Lunch", "Kashmiri Dum Aloo, Kali Masoor Dal, Steamed Basmati Rice, Phulka, Mint Raita", "12:30 PM - 02:30 PM", "Rich aromatic spices"),
        ("Friday", "Snacks", "Veg Cutlets, Sweet & Sour Chutney, Filter Coffee / Tea", "05:00 PM - 06:15 PM", "Hot crispy cutlets"),
        ("Friday", "Dinner", "Mix Dal, Matar Mushroom / Egg Masala, Phulka, Rice, Salad, Rasgulla", "07:45 PM - 09:45 PM", "Weekend welcome treat"),

        ("Saturday", "Breakfast", "Puri Bhaji (Halwai Style), Sooji Halwa, Tea / Coffee", "08:00 AM - 10:00 AM", "Weekend brunch timings"),
        ("Saturday", "Lunch", "Tehri / Veg Pulao with Soya Chunks, Plain Curd, Mirchi Pickle, Papad, Green Salad", "12:30 PM - 02:30 PM", "Saturday comfort one-pot meal"),
        ("Saturday", "Snacks", "Dhokla with Green Chilli Tadka, Masala Tea", "05:00 PM - 06:15 PM", "Gujarati snacks"),
        ("Saturday", "Dinner", "Chana Masala, Jeera Rice, Tandoori Roti, Dal Fry, Roasted Papad, Brownie / Pastry", "07:45 PM - 10:00 PM", "Extended Saturday dinner"),

        ("Sunday", "Breakfast", "Chole Kulche / Pav Bhaji, Boiled Eggs, Fresh Fruit Juice / Shake, Tea / Coffee", "08:00 AM - 10:30 AM", "Sunday leisure breakfast"),
        ("Sunday", "Lunch", "Special Matar Paneer, Dal Makhani, Kashmiri Pulao, Missi Roti, Dahi Vada, Green Chutney", "12:30 PM - 03:00 PM", "Sunday Grand Hostel Feast"),
        ("Sunday", "Snacks", "Veg Sandwiches / Cookies, Milk Tea / Cold Coffee", "05:00 PM - 06:15 PM", "Evening refreshment"),
        ("Sunday", "Dinner", "Khichdi with Desi Ghee / Light Phulka with Dal Fry, Aloo Jeera, Curd, Papad, Seasonal Fruit", "07:45 PM - 09:45 PM", "Light detox meal for Monday start")
    ]
    for m in mess_schedule:
        cur.execute("""
            INSERT OR REPLACE INTO mess_menu (day_of_week, meal_type, items, timings, special_note)
            VALUES (?, ?, ?, ?, ?)
        """, m)

    print("Seeding complaints...")
    complaints_data = [
        (student_ids["25001003043"], "A-101", "Plumbing",
         "Water seepage along bathroom shower head and tap in Room A-101",
         "The continuous tap dripping sound disturbs nighttime study, and water accumulates in the bucket causing bathroom dampness. Please assign plumber for rubber washer replacement.",
         "Medium", "Resolved", "Plumbing contractor replaced faucet washer and cartridge on 12 Nov. Checked and found leak-free.", admin_id),

        (student_ids["25001003044"], "A-101", "Electrical",
         "Study desk power point loose and sparking on plug insertion",
         "Left side switchboard socket in Room A-101 has loose terminals. Laptop charger disconnected intermittently and sparks observed.",
         "High", "In Progress", "Electrician visited on 22 Nov. Socket unit replaced; terminal board tightening pending tomorrow morning.", admin_id),

        (student_ids["25001003046"], "B-101", "WiFi",
         "Wi-Fi signal drops frequently in corner section of Room B-101",
         "SSID 'Hostel_Girls_BlockB_2G' shows full bars near door but drops completely near study table area. Intermittent disconnects during online practical submissions.",
         "High", "Pending", None, None),

        (student_ids["25001003049"], "A-102", "Furniture",
         "Study chair backrest weld joint detached",
         "The black mesh swivel chair assigned to desk 2 has a broken recline weld. Kindly replace with a spare study chair from the hostel store.",
         "Low", "Resolved", "Replaced with inspected wooden ergonomic chair from hostel inventory room on 18 Nov.", admin_id),

        (student_ids["25001003050"], "B-201", "Cleanliness",
         "Corridor dustbin overflow near Room B-201 water dispenser",
         "Common bin on second floor corridor was not cleared by morning housekeeping crew. Requesting timely daily clearance before 09:00 AM.",
         "Medium", "Pending", None, None)
    ]
    for c in complaints_data:
        cur.execute("""
            INSERT INTO complaints (user_id, room_number, category, title, description, priority, status, admin_remarks, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ? = 'Resolved' THEN CURRENT_TIMESTAMP ELSE NULL END)
        """, (c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[6]))

    print("Seeding outpasses with 2-tier approval...")
    outpasses_data = [
        # (user_id, departure_time, expected_return, actual_return, reason, destination, emergency_contact, parent_app, parent_rem, status, admin_rem, reviewed_by)
        (student_ids["25001003043"], "2026-11-08 09:00:00", "2026-11-09 20:00:00", "2026-11-09 19:40:00",
         "Visiting hometown for sibling's engagement ceremony", "Faridabad Sector 15 / Delhi",
         "+91 98765 00001", "Approved", "Family event confirmed. Permission granted.",
         "Returned", "Parental confirmation verified via telephone call. Permission granted.", admin_id),

        (student_ids["25001003044"], "2026-11-14 08:00:00", "2026-11-15 22:00:00", None,
         "Attending National Inter-College Hackathon at DTU New Delhi", "Delhi Technological University, Rohini",
         "+91 98765 00002", "Approved", "Academic event confirmed by parent. Safe journey.",
         "Approved", "Official event participation ticket verified. Stay safe.", admin_id),

        (student_ids["25001003045"], "2026-11-07 17:00:00", "2026-11-07 21:00:00", None,
         "Purchasing course textbooks and lab manuals from Nehru Place", "Nehru Place Electronics & Book Market",
         "+91 98765 00003", "Pending", None,
         "Pending", None, None),

        # Pending outpass for Jiyansh Sardana so his parent Kapil Sardana can approve it!
        (student_ids["25001003043"], "2026-11-26 10:00:00", "2026-11-27 18:00:00", None,
         "Weekend home visit for family function and dental appointment", "Gurugram Sector 14, Haryana",
         "+91 98765 00001", "Pending", None,
         "Pending", None, None),

        # Outpass for Rohan Gupta (Pending Parent Approval)
        (student_ids["25001003049"], "2026-11-28 08:30:00", "2026-11-29 20:00:00", None,
         "Attending IEEE Technical Workshop at DTU Delhi", "DTU Campus, Shahbad Daulatpur, Delhi",
         "+91 98765 00007", "Pending", None,
         "Pending", None, None),

        # Outpass for Ishita Malik (Parent Approved, Pending Warden)
        (student_ids["25001003050"], "2026-11-27 15:00:00", "2026-11-28 19:00:00", None,
         "Visiting hometown for sibling convocation ceremony", "Chandigarh Sector 35",
         "+91 98765 00008", "Approved", "Family permission granted. Travel safely.",
         "Pending", None, None)
    ]
    for o in outpasses_data:
        cur.execute("""
            INSERT INTO outpasses (user_id, departure_time, expected_return, actual_return, reason, destination, emergency_contact,
                                   parent_approval, parent_remarks, parent_action_at, status, admin_remarks, reviewed_by, reviewed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ? = 'Approved' THEN CURRENT_TIMESTAMP ELSE NULL END, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (o[0], o[1], o[2], o[3], o[4], o[5], o[6], o[7], o[8], o[7], o[9], o[10], o[11]))

    print("Seeding fees...")
    fees_data = [
        # (user_id, title, fee_type, amount, due_date, paid_date, status, payment_method, transaction_ref, receipt_number)
        (student_ids["25001003043"], "Semester 3 Hostel Accommodation (AC Double)", "Hostel Rent", 27000.0, "2026-08-15", "2026-08-10 11:20:00", "Paid", "UPI", "UPI9823412039", "REC-2026-1001"),
        (student_ids["25001003043"], "Fall 2026 Mess Advance (Full Semester)", "Mess Fee", 18000.0, "2026-08-20", "2026-08-12 15:45:00", "Paid", "NetBanking", "NB88231902", "REC-2026-1002"),
        (student_ids["25001003043"], "Hostel Amenities & Maintenance Fee", "Maintenance", 2500.0, "2026-11-30", None, "Pending", None, None, None),

        (student_ids["25001003044"], "Semester 3 Hostel Accommodation (AC Double)", "Hostel Rent", 27000.0, "2026-08-15", "2026-08-11 09:30:00", "Paid", "Debit Card", "DC773412", "REC-2026-1003"),
        (student_ids["25001003044"], "Fall 2026 Mess Advance (Full Semester)", "Mess Fee", 18000.0, "2026-08-20", None, "Pending", None, None, None),

        (student_ids["25001003046"], "Semester 3 Girls Hostel Room (AC)", "Hostel Rent", 27000.0, "2026-08-15", "2026-08-08 14:10:00", "Paid", "UPI", "UPI55123901", "REC-2026-1004"),
        (student_ids["25001003046"], "Fall 2026 Mess Charges", "Mess Fee", 18000.0, "2026-08-20", "2026-08-08 14:15:00", "Paid", "UPI", "UPI55123902", "REC-2026-1005"),

        (student_ids["25001003048"], "Semester 3 Girls Hostel Room (Non-AC)", "Hostel Rent", 22500.0, "2026-08-15", "2026-08-12 10:00:00", "Paid", "UPI", "UPI77123909", "REC-2026-1006"),
        (student_ids["25001003049"], "Semester 3 Boys Room A-102", "Hostel Rent", 22500.0, "2026-08-15", "2026-08-11 16:20:00", "Paid", "NetBanking", "NB99120344", "REC-2026-1007"),
        (student_ids["25001003050"], "Semester 5 Girls Room B-201", "Hostel Rent", 19000.0, "2026-08-15", None, "Pending", None, None, None),
        (student_ids["25001003051"], "Semester 5 Boys Room A-103", "Hostel Rent", 19000.0, "2026-08-15", "2026-08-09 11:30:00", "Paid", "Debit Card", "DC8812903", "REC-2026-1008"),
        (student_ids["25001003052"], "Semester 1 First Year Hostel Allotment", "Hostel Rent", 19000.0, "2026-08-20", "2026-08-18 12:00:00", "Paid", "UPI", "UPI4419023", "REC-2026-1009")
    ]
    for f in fees_data:
        cur.execute("""
            INSERT INTO fees (user_id, title, fee_type, amount, due_date, paid_date, status, payment_method, transaction_ref, receipt_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, f)

    print("Seeding attendance logs...")
    base_date = datetime.date(2026, 11, 16)
    for i in range(7):
        att_date = (base_date + datetime.timedelta(days=i)).isoformat()
        # Jiyansh
        j_status = "Present" if i != 4 else "Late Entry"
        j_time = "21:15" if i != 4 else "21:48"
        j_remarks = "Biometric check-in verified" if i != 4 else "Late by 18 mins due to library study group"
        cur.execute("""
            INSERT OR REPLACE INTO attendance (user_id, date, status, check_in_time, remarks, marked_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_ids["25001003043"], att_date, j_status, j_time, j_remarks, admin_id))

        # Rahul
        r_status = "On Outpass" if (i == 2 or i == 3) else "Present"
        r_time = "Outpass" if (i == 2 or i == 3) else "21:20"
        cur.execute("""
            INSERT OR REPLACE INTO attendance (user_id, date, status, check_in_time, remarks, marked_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_ids["25001003044"], att_date, r_status, r_time, "Curfew roll call verified", admin_id))

        # Priya
        cur.execute("""
            INSERT OR REPLACE INTO attendance (user_id, date, status, check_in_time, remarks, marked_by)
            VALUES (?, ?, 'Present', '21:05', 'Girls Wing turnstile verified', ?)
        """, (student_ids["25001003046"], att_date, admin_id))

        # Rohan
        cur.execute("""
            INSERT OR REPLACE INTO attendance (user_id, date, status, check_in_time, remarks, marked_by)
            VALUES (?, ?, 'Present', '21:10', 'Biometric check-in verified', ?)
        """, (student_ids["25001003049"], att_date, admin_id))

        # Ishita
        cur.execute("""
            INSERT OR REPLACE INTO attendance (user_id, date, status, check_in_time, remarks, marked_by)
            VALUES (?, ?, 'Present', '21:18', 'Biometric check-in verified', ?)
        """, (student_ids["25001003050"], att_date, admin_id))

    print("Seeding parent queries...")
    queries_data = [
        (parent_ids["parent_25001003043"], student_ids["25001003043"], "Health",
         "Campus First Aid & Late-Night Dispensary Timings",
         "Dear Warden, I am Kapil Sardana, father of Jiyansh (Roll 25001003043). Could you please confirm the nearest doctor on-call timings on campus for residents?",
         "Resolved", "Dispensary is open 24x7 near the Admin Block. Medical emergency helpline: +91 98111 22999.", admin_id),

        (parent_ids["parent_25001003044"], student_ids["25001003044"], "Mess",
         "Vegetarian Diet Preferences during Festivals",
         "Requesting special Navratri/festive satvik meals during the upcoming week.",
         "Pending", None, None)
    ]
    for q in queries_data:
        cur.execute("""
            INSERT INTO parent_queries (parent_id, student_id, category, subject, message, status, admin_reply, replied_by, replied_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CASE WHEN ? = 'Resolved' THEN CURRENT_TIMESTAMP ELSE NULL END)
        """, (q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[5]))

    conn.commit()
    conn.close()
    print("Database successfully seeded with realistic sample data!")

if __name__ == '__main__':
    seed()
