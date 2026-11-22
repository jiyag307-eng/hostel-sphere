"""
Comprehensive Test Suite for Hostel Management System
Tests routing, authentication (Student, Parent, Admin),
Parent Outpass Approval, Fee Payments & Invoices, Curfew Attendance, and Helpdesk.
Run: python test_app.py
"""

import unittest
from app import app
from database import init_db, query_db
import seed_data

class HostelAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Seed test database
        seed_data.seed()

    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def login(self, username, password):
        return self.client.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    # 1. Public Routes
    def test_landing_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'HostelSphere', response.data)
        self.assertIn(b'Today', response.data)

    def test_notices_page(self):
        response = self.client.get('/notices')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Notice Board', response.data)

    def test_mess_menu_page(self):
        response = self.client.get('/mess-menu?day=Monday')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Menu for Monday', response.data)
        self.assertIn(b'Rajma Masala', response.data)

    # 2. Authentication & RBAC (Student, Parent, Admin)
    def test_student_login_and_dashboard(self):
        rv = self.login('25001003043', 'student123')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Jiyansh Sardana', rv.data)
        self.assertIn(b'My Room', rv.data)

        # Access Student Dashboard
        dash = self.client.get('/student/dashboard')
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b'A-101', dash.data)

        # Student cannot access admin portal
        admin_page = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied', admin_page.data)

        self.logout()

    def test_admin_login_and_dashboard(self):
        rv = self.login('admin', 'admin123')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Administration Console', rv.data)

        # Access Admin Dashboard
        dash = self.client.get('/admin/dashboard')
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b'Pending Gate Outpasses', dash.data)

        self.logout()

    def test_parent_login_and_dashboard(self):
        # Parent login for Rakesh Sardana
        rv = self.login('parent_25001003043', 'parent123')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Mr. Rakesh Sardana', rv.data)
        self.assertIn(b'Jiyansh Sardana', rv.data)

        # Access Parent Dashboard
        dash = self.client.get('/parent/dashboard')
        self.assertEqual(dash.status_code, 200)
        self.assertIn(b'A-101', dash.data)
        self.assertIn(b'Curfew Attendance', dash.data)

        # Parent cannot access admin portal
        admin_page = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied', admin_page.data)

        self.logout()

    def test_invalid_login(self):
        rv = self.login('admin', 'wrong_password')
        self.assertIn(b'Invalid credentials', rv.data)

    # 3. Student Workflow: Lodge Complaint & Apply Outpass
    def test_student_lodge_complaint(self):
        self.login('25001003043', 'student123')
        rv = self.client.post('/student/complaints', data=dict(
            category='WiFi',
            room_number='A-101',
            priority='High',
            title='Test Disconnection Issue',
            description='Wi-Fi drops out frequently during lecture hours.'
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Test Disconnection Issue', rv.data)
        self.logout()

    def test_student_apply_outpass_and_view_pass(self):
        self.login('25001003043', 'student123')
        rv = self.client.post('/student/outpass', data=dict(
            departure_time='2026-11-20T10:00',
            expected_return='2026-11-21T18:00',
            destination='Gurugram Sector 29',
            emergency_contact='+91 98765 00001',
            reason='Visiting relatives for family function'
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Gurugram Sector 29', rv.data)
        self.logout()

    # 4. Parent Outpass Approval Workflow
    def test_parent_outpass_approval_flow(self):
        # Login as parent of Jiyansh
        self.login('parent_25001003043', 'parent123')

        # View ward outpasses list
        rv = self.client.get('/parent/outpasses')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Outpass Approvals', rv.data)

        # Approve outpass #4 (which is pending for Jiyansh)
        rv_review = self.client.post('/parent/outpass/4/review', data=dict(
            decision='Approved',
            parent_remarks='Verified with child. Permission granted for dental checkup.'
        ), follow_redirects=True)
        self.assertEqual(rv_review.status_code, 200)
        self.assertIn(b'approved by parent', rv_review.data)

        # Verify DB state
        with self.app.app_context():
            outpass = query_db("SELECT parent_approval, parent_remarks FROM outpasses WHERE id = 4", one=True)
            self.assertEqual(outpass['parent_approval'], 'Approved')
            self.assertIn('dental checkup', outpass['parent_remarks'])

        self.logout()

    # 5. Fee & Payment Workflow (Parent & Student)
    def test_fee_view_and_payment(self):
        # Login as parent of Jiyansh
        self.login('parent_25001003043', 'parent123')

        # Access fees view
        rv = self.client.get('/parent/fees')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Hostel Amenities', rv.data)

        # Pay pending fee #3
        rv_pay = self.client.post('/fees/3/pay', data=dict(
            payment_method='UPI',
            payer_name='Mr. Rakesh Sardana'
        ), follow_redirects=True)
        self.assertEqual(rv_pay.status_code, 200)
        self.assertIn(b'Payment of', rv_pay.data)

        # View printable fee receipt
        rv_receipt = self.client.get('/fees/3/receipt')
        self.assertEqual(rv_receipt.status_code, 200)
        self.assertIn(b'Official Fee Payment Receipt', rv_receipt.data)
        self.assertIn(b'Jiyansh Sardana', rv_receipt.data)

        self.logout()

    # 6. Night Curfew & Roll Call Attendance (Parent & Student View)
    def test_attendance_views(self):
        # Parent view
        self.login('parent_25001003043', 'parent123')
        rv_p = self.client.get('/parent/attendance')
        self.assertEqual(rv_p.status_code, 200)
        self.assertIn(b'Night Curfew', rv_p.data)
        self.logout()

        # Student view
        self.login('25001003043', 'student123')
        rv_s = self.client.get('/student/attendance')
        self.assertEqual(rv_s.status_code, 200)
        self.assertIn(b'Curfew Status', rv_s.data)
        self.logout()

    # 7. Parent Inquiries Desk & Admin Resolution
    def test_parent_queries_and_admin_reply(self):
        # 1. Parent submits inquiry
        self.login('parent_25001003043', 'parent123')
        rv = self.client.post('/parent/queries', data=dict(
            category='Health',
            subject='Medical Room Contact Number',
            message='Please share the emergency mobile number of night warden.'
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Medical Room Contact Number', rv.data)
        self.logout()

        # 2. Admin views and responds
        self.login('admin', 'admin123')
        rv_admin = self.client.get('/admin/parent-queries')
        self.assertEqual(rv_admin.status_code, 200)
        self.assertIn(b'Medical Room Contact Number', rv_admin.data)

        # Find latest query id
        with self.app.app_context():
            q = query_db("SELECT id FROM parent_queries WHERE subject = 'Medical Room Contact Number'", one=True)
            self.assertIsNotNone(q)
            q_id = q['id']

        rv_reply = self.client.post(f'/admin/parent-queries/{q_id}/reply', data=dict(
            admin_reply='The night warden on call can be reached at +91 98111 22335.'
        ), follow_redirects=True)
        self.assertEqual(rv_reply.status_code, 200)

        # Verify DB is resolved
        with self.app.app_context():
            updated_q = query_db("SELECT status, admin_reply FROM parent_queries WHERE id = ?", (q_id,), one=True)
            self.assertEqual(updated_q['status'], 'Resolved')
            self.assertIn('98111 22335', updated_q['admin_reply'])

        self.logout()

    # 8. Admin Workflow: Notice CRUD & Outpass Review
    def test_admin_create_notice(self):
        self.login('admin', 'admin123')
        rv = self.client.post('/admin/notices/new', data=dict(
            title='Unit Test Notice Title',
            category='Event',
            content='This is a test announcement content for automated testing.',
            is_pinned='1'
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Unit Test Notice Title', rv.data)
        self.logout()

    def test_admin_review_outpass(self):
        self.login('admin', 'admin123')
        # Review outpass #3 (which is pending in seed)
        rv = self.client.post('/admin/outpass/3/review', data=dict(
            decision='Approved',
            admin_remarks='Verified with parent. Approved by Chief Warden.'
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.logout()

    # 9. Admin Workflow: Attendance Management & Fees
    def test_admin_attendance_and_fees(self):
        self.login('admin', 'admin123')

        # View attendance console
        rv_att = self.client.get('/admin/attendance')
        self.assertEqual(rv_att.status_code, 200)
        self.assertIn(b'Roll Call Roster', rv_att.data)

        # View admin fees console
        rv_fees = self.client.get('/admin/fees')
        self.assertEqual(rv_fees.status_code, 200)
        self.assertIn(b'Fee Collections & Invoicing', rv_fees.data)

        self.logout()

    # 10. Admin Workflow: Room Allotment
    def test_admin_room_allotment(self):
        self.login('admin', 'admin123')
        # Student 5 (Sneha Kapoor, id 6) into Room A-103
        rv = self.client.post('/admin/rooms/allot', data=dict(
            student_id=6,
            room_id=3,
            bed_number=1
        ), follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.logout()


if __name__ == '__main__':
    unittest.main()
