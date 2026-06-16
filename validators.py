import re


def validate_name(name, field_label="Name"):
    name = name.strip()
    if not name:
        return False, f"{field_label} cannot be empty."
    if not re.match(r"^[A-Za-z\s\-']{2,50}$", name):
        return False, f"{field_label} must be 2-50 letters only."
    return True, name.title()


def validate_age(age_str):
    try:
        age = int(age_str)
    except (TypeError, ValueError):
        return False, "Age must be a whole number."
    if age < 16 or age > 120:
        return False, "Age must be between 16 and 120."
    return True, age


def validate_mobile(mobile):
    mobile = mobile.strip().replace(" ", "")
    if not re.match(r"^07\d{9}$", mobile):
        return False, "Mobile must be 11 digits starting with 07."
    return True, mobile


def validate_postcode(postcode):
    postcode = postcode.strip().upper()
    if not re.match(r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$", postcode):
        return False, "Invalid UK postcode format (e.g. B1 1AB)."
    return True, postcode


def validate_vehicle_type(vehicle_type):
    allowed = {"Sedan", "SUV", "Van", "Estate", "Minibus"}
    vehicle_type = vehicle_type.strip().title()
    if vehicle_type not in allowed:
        return False, f"Vehicle type must be one of: {', '.join(sorted(allowed))}."
    return True, vehicle_type


def validate_distance(distance_str):
    try:
        distance = float(distance_str)
    except (TypeError, ValueError):
        return False, "Distance must be a number."
    if distance <= 0 or distance > 500:
        return False, "Distance must be between 0.1 and 500 km."
    return True, round(distance, 2)


def validate_username(username):
    username = username.strip()
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be 3-30 characters."
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False, "Username may only contain letters, numbers, and underscores."
    return True, username


def validate_password(password):
    if len(password) < 3:
        return False, "Password must be at least 3 characters."
    return True, password
