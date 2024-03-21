from django.contrib.auth.hashers import make_password

from Users.utilities import full_name_check, email_exists, phone_exists, check_valid_password, phone_number_check


def validate_register_data(user_data):
    """Perform sequential validation checks and return the first error message encountered."""
    validators = [
        (lambda value: not full_name_check(value), 'Invalid full name', user_data.get('user_full_name')),
        (email_exists, 'Email already exists', user_data.get('user_email')),
        (phone_exists, 'Phone number already exists', user_data.get('user_phone')),
        (lambda value: not phone_number_check(value), 'Invalid phone number', user_data.get('user_phone')),
        (lambda value: not check_valid_password(value), 'Invalid password', user_data.get('user_password')),
        (lambda password: password != user_data.get('user_password_2'), "Passwords don't match",
         user_data.get('user_password')),
    ]

    for validator, error_msg, value in validators:
        if validator(value):
            return error_msg  # Return the error message if the validator condition is met
    return None  # No errors found

def encrypt_password(plain_password: str) -> str:
    '''encrypt the password user using PBKDF2 algorithm'''
    
    return make_password(plain_password)

