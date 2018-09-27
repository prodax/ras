import unittest
from ras.lib.odoo_xmlrpc import OdooXmlRPC

class TestXmlRPC(unittest.TestCase):

    def setUp(self):
        host = "localhost"
        port = "8069"
        user = "admin"
        user_pw = "admin"
        database = "11.0-mig-hr_attendance_rfid"
        https_on = False
        self.right_rfid = "19c2af28"
        self.wrong_rfid = "FFFFFFFF"
        self.odoo_xmlrpc = OdooXmlRPC(host, port, https_on, database, user, user_pw)

    def test_connection_right_rfid(self):
        res = self.odoo_xmlrpc.check_attendance(self.right_rfid)
        self.assertTrue(res["action"] in ['check_in', 'check_out'])

    def test_connection_wrong_rfid(self):
        res = self.odoo_xmlrpc.check_attendance(self.wrong_rfid)
        self.assertTrue(res["action"] == 'FALSE')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()