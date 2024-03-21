from Users.utilities import check_email_valid, email_exists, full_name_check, phone_exists, phone_number_check


def validate_update_user_info(user, full_name, email, phone):
    """Update user information and perform validation"""
    
    # Check if full name needs to be updated
    if full_name != user.user_full_name:
        if full_name_check(full_name) is False:
            return "Invalid full name"
        else:
            user.user_full_name = full_name  # Update full name in the database

    # Check if email needs to be updated
    if email != user.user_email:
        if email_exists(email):
            return "Email already exists"
        elif check_email_valid(email) is False:
            return "Email is invalid"
        else:
            user.user_email = email  # Update email in the database

    # Check if phone number needs to be updated
    if phone != user.user_phone:
        if phone_exists(phone):
            return "Phone number already exists"
        elif phone_number_check(phone) is False:
            return "Phone number is invalid"
        else:
            user.user_phone = phone  # Update phone number in the database
    
    return "success"