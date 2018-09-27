import unittest
from lib.odoo_xmlrpc import connection, authenticate_connection

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.host = "localhost"
        self.port = "8069"
        self.user = "admin"
        self.user_pw = "admin"
        self.database = "11.0-mig-hr_attendance_rfid"
        self.https_on = False
        self.right_rfid = "19c2af28"
        self.wrong_rfid = "FFFFFFFF"

    def test_connection_right_rfid(self):
        user_id = authenticate_connection(self.host, self.port,
                                          self.user,self.user_pw,
                                          self.database, self.https_on)

        object_facade = connection(self.host, self.port, self.https_on)

        res = object_facade.execute(
            self.database, user_id, self.user_pw, "hr.employee",
            "register_attendance", self.right_rfid)

        self.assertTrue(res["action"] in ['check_in', 'check_out'])

    def test_connection_wrong_rfid(self):
        user_id = authenticate_connection(self.host, self.port,
                                          self.user,self.user_pw,
                                          self.database, self.https_on)

        object_facade = connection(self.host, self.port, self.https_on)

        res = object_facade.execute(
            self.database, user_id, self.user_pw, "hr.employee",
            "register_attendance", self.wrong_rfid)

        self.assertTrue(res["action"] == 'FALSE')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()