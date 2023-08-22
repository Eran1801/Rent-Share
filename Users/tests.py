import unittest
from Users.views import *

class TestsFouUsersFunctions(unittest.TestCase):

    # ---------------password--------------------
    def test_valid_password(self):
        self.assertTrue(check_valid_password("Abc12345"))
        self.assertTrue(check_valid_password("Abcdefg1"))
        self.assertTrue(check_valid_password("Abcdefg1!"))
        self.assertTrue(check_valid_password("Abcdefg1@"))
        self.assertTrue(check_valid_password("Abcdefg1#"))

    def test_invalid_password(self):
        self.assertFalse(check_valid_password("abc12345"))
        self.assertFalse(check_valid_password("ABC12345"))
        self.assertFalse(check_valid_password("Abcdefg"))
        self.assertFalse(check_valid_password("12345678"))
        self.assertFalse(check_valid_password("Abcdefg!"))
        self.assertFalse(check_valid_password("")) 

    # ---------------user name--------------------
    def test_valid_user_name(self):
        self.assertTrue(full_name_check("John Doe"))
        self.assertTrue(full_name_check("John Doe Jr"))
        self.assertTrue(full_name_check("Eran Levy."))
        self.assertTrue(full_name_check("Karin Bitan."))
    
    def test_invalid_user_name(self):
        self.assertFalse(full_name_check("John"))
        self.assertFalse(full_name_check(""))
        self.assertFalse(full_name_check("Ben"))
        self.assertFalse(full_name_check("Jonathan"))

    # ---------------phone number------------------------
    def test_valid_phone_number(self):
        self.assertTrue(phone_number_check("0501234567"))
        self.assertTrue(phone_number_check("0501345678"))
        self.assertTrue(phone_number_check("0544776313"))
        self.assertTrue(phone_number_check("0544743313"))

    def test_invalid_phone_number(self):
        self.assertFalse(phone_number_check("050123456"))
        self.assertFalse(phone_number_check("05012345678901"))
        self.assertFalse(phone_number_check("050123456789012"))
        self.assertFalse(phone_number_check(""))     

if __name__ == "__main__":
    unittest.main()
