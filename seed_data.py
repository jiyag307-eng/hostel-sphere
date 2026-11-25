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
         "+91 98765 43210", "Rakesh Sardana", "+91 98765 00001", "Computer Engineering", 3, "Male"),
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
        ("parent_25001003043", "Mr. Rakesh Sardana", "rakesh.sardana@example.com", "+91 98765 00001", "25001003043", "Father"),
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
        p_id = cur.lastrowid
        parent_ids[p_user] = p_id

        # Link parent to student
        cur.execute("""
            INSERT INTO parent_students (parent_id, student_id, relationship)
            VALUES (?, ?, ?)
        """, (p_id, student_ids[ward_roll], relation))

    print("Seeding rooms...")
    rooms_data = [
        ("A-101", "Block A", 1, 2, "AC", 6500.0, "Occupied", "Double occupancy deluxe AC room, garden facing."),
        ("A-102", "Block A", 1, 2, "Non-AC", 4500.0, "Available", "Spacious 2-seater with dedicated wardrobes."),
        ("A-103", "Block A", 1, 3, "Non-AC", 3800.0, "Available", "Triple occupancy room with balcony."),
        ("A-201", "Block A", 2, 2, "AC", 6500.0, "Available", "Quiet corner room, study tables included."),
        ("A-202", "Block A", 2, 2, "Non-AC", 4500.0, "Maintenance", "Under painting and minor maintenance."),
        ("B-101", "Block B", 1, 2, "AC", 6500.0, "Occupied", "Girls Wing double occupancy AC room."),
        ("B-102", "Block B", 1, 2, "Non-AC", 4500.0, "Available", "Well ventilated 2-seater room."),
        ("B-201", "Block B", 2, 3, "Non-AC", 3800.0, "Available", "Triple bed room near library lounge.")
    ]
    room_ids = {}
    for r in rooms_data:
        cur.execute("""
            INSERT INTO rooms (room_number, block, floor, capacity, room_type, monthly_rent, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, r)
        room_ids[r[0]] = cur.lastrowid

    print("Seeding room allotments...")
    # Jiyansh and Rahul in A-101
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-01', 'Active')
    """, (student_ids["25001003043"], room_ids["A-101"], 1))
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-01', 'Active')
    """, (student_ids["25001003044"], room_ids["A-101"], 2))

    # Aarav and Rohan in A-102
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-05', 'Active')
    """, (student_ids["25001003045"], room_ids["A-102"], 1))
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-05', 'Active')
    """, (student_ids["25001003049"], room_ids["A-102"], 2))

    # Priya and Sneha in B-101
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-02', 'Active')
    """, (student_ids["25001003046"], room_ids["B-101"], 1))
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-02', 'Active')
    """, (student_ids["25001003047"], room_ids["B-101"], 2))

    # Ananya in B-102
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-04', 'Active')
    """, (student_ids["25001003048"], room_ids["B-102"], 1))

    # Kabir in A-103
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-06', 'Active')
    """, (student_ids["25001003051"], room_ids["A-103"], 1))

    # Ishita and Tanya in B-201
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-03', 'Active')
    """, (student_ids["25001003050"], room_ids["B-201"], 1))
    cur.execute("""
        INSERT INTO room_allotments (user_id, room_id, bed_number, allotted_date, status)
        VALUES (?, ?, ?, '2026-08-03', 'Active')
    """, (student_ids["25001003052"], room_ids["B-201"], 2))

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
        ("Wednesday", "Dinner", "Yellow Moong Dal, Bhindi Masala, Dum Aloo, Phulka, Steamed Rice, Fruit Custard", "07:45 PM - 09:45 PM", "Light nutritious meal"),

        ("Thursday", "Breakfast", "Methi Thepla, Curd, Chana Chaat, Fresh Bananas, Tea / Coffee", "07:30 AM - 09:30 AM", "Gujarati delicacy"),
        ("Thursday", "Lunch", "Dal Fry, Baingan Bharta / Aloo Shimlamirch, Chapati, Rice, Plain Curd, Salad", "12:30 PM - 02:30 PM", "Home-style cooked lunch"),
        ("Thursday", "Snacks", "Veg Cutlets, Coriander Dip, Tea / Milk", "05:00 PM - 06:15 PM", "Crispy vegetable patties"),
        ("Thursday", "Dinner", "Chana Dal Tadka, Matar Mushroom / Egg Curry, Jeera Rice, Tandoori Roti, Kheer", "07:45 PM - 09:45 PM", "Traditional rice pudding"),

        ("Friday", "Breakfast", "Uttapam with Sambhar & Red Chilli Chutney, Boiled Eggs / Apples, Tea / Coffee", "07:30 AM - 09:30 AM", "Hot onion-tomato uttapam"),
        ("Friday", "Lunch", "Black Dal (Maa ki Dal), Gatta Curry, Steamed Rice, Tawa Roti, Boondi Raita, Salad", "12:30 PM - 02:30 PM", "Rajasthani flavors"),
        ("Friday", "Snacks", "Paviraj Pav Bhaji / Bun Maska, Tea / Milk", "05:00 PM - 06:15 PM", "Weekend warm-up snacks"),
        ("Friday", "Dinner", "Veg Biryani / Chicken Biryani, Mirchi ka Salan, Onion Raita, Malai Kofta, Moong Dal Halwa", "07:45 PM - 09:45 PM", "Special Biryani night"),

        ("Saturday", "Breakfast", "Puri Bhaji (Halwai Style Aloo Curry), Suji Halwa, Tea / Coffee", "07:30 AM - 10:00 AM", "Extended Saturday morning hours"),
        ("Saturday", "Lunch", "Khichdi & Kadhi, Roasted Papad, Aloo Chokha, Pickle, Butter Milk (Chaas)", "12:30 PM - 02:30 PM", "Comfort food"),
        ("Saturday", "Snacks", "Bhel Puri / Sev Puri, Tea / Cold Drink", "05:00 PM - 06:15 PM", "Street snack vibes"),
        ("Saturday", "Dinner", "Dal Tadka, Palak Paneer, Zeera Rice, Roti, Gulab Jamun", "07:45 PM - 09:45 PM", "Wholesome weekend dinner"),

        ("Sunday", "Breakfast", "Masala Dosa, Sambhar, 2 Chutneys, Tea / Filter Coffee", "08:00 AM - 10:30 AM", "Special Sunday brunch timing"),
        ("Sunday", "Lunch", "Veg Manchurian / Chilli Paneer, Fried Rice, Hakka Noodles, Hot Sweet Corn Soup", "12:30 PM - 02:30 PM", "Indo-Chinese feast"),
        ("Sunday", "Snacks", "Pasta (Red Sauce), Garlic Bread, Tea / Coffee", "05:00 PM - 06:15 PM", "Italian evening"),
        ("Sunday", "Dinner", "Paneer Lababdar / Butter Chicken, Dal Makhani, Garlic Naan, Peas Pulao, Rasgulla", "07:45 PM - 10:00 PM", "Grand Sunday Banquet")
    ]
    for item in mess_schedule:
        cur.execute("""
            INSERT OR REPLACE INTO mess_menu (day_of_week, meal_type, items, timings, special_note)
            VALUES (?, ?, ?, ?, ?)
        """, (item[0], item[1], item[2], item[3], item[4]))

    print("Seeding complaints...")
    complaints_data = [
        (student_ids["25001003043"], "A-101", "Plumbing", "Bathroom tap leaking continuously",
         "The cold water tap in our attached washroom has a steady leakage, leading to water wastage and dripping noise at night. Needs a washer replacement.",
         "High", "In Progress", "Hostel maintenance plumber Mr. Ramu has been assigned. Scheduled for repair tomorrow at 10:30 AM."),

        (student_ids["25001003044"], "A-101", "Furniture", "Study chair backrest broken",
         "One of the study chairs has a wobbly and cracked back support screw. Needs tightening or replacement.",
         "Low", "Resolved", "Replaced with an ergonomic mesh chair from the hostel inventory on 2026-11-04."),

        (student_ids["25001003045"], "A-102", "WiFi", "Weak Wi-Fi signal in corner room",
         "The signal drops to 1 bar inside room A-102 especially during late night hours. Ping is fluctuating.",
         "Medium", "Pending", "Noted. IT team is mapping signal hotspots this weekend."),

        (student_ids["25001003046"], "B-101", "Electrical", "Tube light blinking repeatedly in corridor",
         "The corridor light right outside Room B-101 is flickering rapidly since yesterday.",
         "Medium", "Pending", "Electrician notified.")
    ]
    for c in complaints_data:
        cur.execute("""
            INSERT INTO complaints (user_id, room_number, category, title, description, priority, status, admin_remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, c)

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

        # Pending outpass for Jiyansh Sardana so his parent can approve it right away!
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
    # Seed past 6 days of attendance
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
         "Dear Warden, could you please confirm the nearest doctor on-call timings on campus for residents?",
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
