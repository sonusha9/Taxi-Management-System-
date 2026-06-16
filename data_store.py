import json
import os

from Admin import Admin
from Customer import Customer
from Ride import Ride
from TaxiDriver import TaxiDriver

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def default_data():
    return {
        "users": [
            {
                "username": "admin",
                "password": "123",
                "role": "admin",
                "full_name": "Administrator",
                "address": "B1 1AB",
            }
        ],
        "admin": {"username": "admin", "password": "123", "address": "B1 1AB"},
        "drivers": [
            {"first_name": "John", "surname": "Smith", "vehicle_type": "Sedan", "status": "Available"},
            {"first_name": "Jane", "surname": "Smith", "vehicle_type": "SUV", "status": "Available"},
            {"first_name": "Jone", "surname": "Carlos", "vehicle_type": "Van", "status": "Offline"},
        ],
        "customers": [
            {"first_name": "Sara", "surname": "Smith", "age": 20, "mobile": "07012345678", "postcode": "B1 234", "taxi_driver": "None"},
            {"first_name": "Mike", "surname": "Jones", "age": 37, "mobile": "07555551234", "postcode": "L2 2AB", "taxi_driver": "None"},
            {"first_name": "David", "surname": "Smith", "age": 25, "mobile": "07123456789", "postcode": "C1 ABC", "taxi_driver": "None"},
        ],
        "rides": [],
        "completed_customers": [],
        "next_ride_id": 1,
    }


def _migrate_users(data):
    """Ensure users list exists (upgrade from older data.json)."""
    if "users" not in data:
        admin = data.get("admin", {})
        data["users"] = [
            {
                "username": admin.get("username", "admin"),
                "password": admin.get("password", "123"),
                "role": "admin",
                "full_name": "Administrator",
                "address": admin.get("address", "B1 1AB"),
            }
        ]
    return data


def load_data():
    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data = _migrate_users(data)
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def authenticate_user(users, username, password):
    for user in users:
        if user["username"] == username and user["password"] == password:
            return user
    return None


def username_exists(users, username):
    return any(u["username"] == username for u in users)


def data_to_objects(data):
    admin_info = data["admin"]
    admin = Admin(admin_info["username"], admin_info["password"], admin_info.get("address", ""))
    drivers = [TaxiDriver.from_dict(d) for d in data["drivers"]]
    customers = [Customer.from_dict(c) for c in data["customers"]]
    rides = [Ride.from_dict(r) for r in data["rides"]]
    completed = [Customer.from_dict(c) for c in data.get("completed_customers", [])]
    users = data.get("users", [])
    return admin, drivers, customers, rides, completed, users


def objects_to_data(admin, drivers, customers, rides, completed, users, next_ride_id=1):
    admin_user = next((u for u in users if u.get("role") == "admin"), None)
    if admin_user:
        admin_info = {
            "username": admin_user["username"],
            "password": admin_user["password"],
            "address": admin_user.get("address", admin.get_address()),
        }
    else:
        admin_info = {
            "username": admin.get_username(),
            "password": admin.get_password(),
            "address": admin.get_address(),
        }

    return {
        "users": users,
        "admin": admin_info,
        "drivers": [d.to_dict() for d in drivers],
        "customers": [c.to_dict() for c in customers],
        "rides": [r.to_dict() for r in rides],
        "completed_customers": [c.to_dict() for c in completed],
        "next_ride_id": next_ride_id,
    }
