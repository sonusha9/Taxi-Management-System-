from TaxiDriver import TaxiDriver
from fare_calculator import calculate_fare
from validators import (
    validate_name,
    validate_password,
    validate_postcode,
    validate_username,
    validate_vehicle_type,
)


class Admin:
    """A class that deals with the Admin operations"""

    def __init__(self, username, password, address=""):
        self.__username = username
        self.__password = password
        self.__address = address

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_address(self):
        return self.__address

    def set_username(self, username):
        self.__username = username

    def set_password(self, password):
        self.__password = password

    def set_address(self, address):
        self.__address = address

    def view(self, a_list):
        """Print a list with numbering"""
        for index, item in enumerate(a_list):
            print(f"{index + 1:3}|{item}")

    def login(self, username=None, password=None):
        """Admin login. Returns True if credentials match."""
        if username is None:
            print("-----Login-----")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
        return username == self.__username and password == self.__password

    def find_index(self, index, taxidrivers):
        """Check if the taxi driver index exists"""
        return index in range(0, len(taxidrivers))

    def get_taxi_driver_details(self):
        """Get taxi driver details: first name, surname, vehicle_type"""
        ok, first_name = validate_name(input("First name: "), "First name")
        if not ok:
            raise ValueError(first_name)
        ok, surname = validate_name(input("Surname: "), "Surname")
        if not ok:
            raise ValueError(surname)
        ok, vehicle_type = validate_vehicle_type(input("Vehicle type: "))
        if not ok:
            raise ValueError(vehicle_type)
        return first_name, surname, vehicle_type

    def taxi_driver_management(self, taxidrivers):
        """Register/View/Update/Delete Taxi drivers"""
        print("-----TaxiDriver Management-----")
        print("Choose the operation:")
        print(" 1 - Register")
        print(" 2 - View")
        print(" 3 - Update")
        print(" 4 - Delete")

        op = input("Option: ")

        if op == "1":
            print("-----Register-----")
            print("Enter taxi driver's details:")
            try:
                first_name, surname, vehicle_type = self.get_taxi_driver_details()
            except ValueError as e:
                print(e)
                return

            for taxidriver in taxidrivers:
                if (
                    first_name == taxidriver.get_first_name()
                    and surname == taxidriver.get_surname()
                ):
                    print("Name already exists.")
                    return

            taxidrivers.append(TaxiDriver(first_name, surname, vehicle_type))
            print("TaxiDriver registered.")

        elif op == "2":
            print("-----List of TaxiDrivers-----")
            print(f"{'ID':>3} | {'Full Name':^30} | {'Vehicle':^15} | {'Status':^12}")
            self.view(taxidrivers)

        elif op == "3":
            while True:
                print("-----Update TaxiDriver's Details-----")
                print("ID | Full name | Vehicle Type | Status")
                self.view(taxidrivers)
                try:
                    index = int(input("Enter ID: ")) - 1
                    if self.find_index(index, taxidrivers):
                        break
                    print("TaxiDriver not found")
                except ValueError:
                    print("Incorrect ID")

            print("Choose field:")
            print("1 First name\n2 Surname\n3 Vehicle Type\n4 Status")
            try:
                field = int(input("Input: "))
            except ValueError:
                print("Invalid option!")
                return

            driver = taxidrivers[index]
            if field == 1:
                ok, val = validate_name(input("New first name: "), "First name")
                if ok:
                    driver.set_first_name(val)
            elif field == 2:
                ok, val = validate_name(input("New surname: "), "Surname")
                if ok:
                    driver.set_surname(val)
            elif field == 3:
                ok, val = validate_vehicle_type(input("New vehicle type: "))
                if ok:
                    driver.set_vehicle_type(val)
            elif field == 4:
                status = input("Status (Available/On Ride/Offline): ").strip()
                driver.set_status(status)
            else:
                print("Invalid option!")

        elif op == "4":
            print("-----Delete TaxiDriver-----")
            print("ID | Full Name | Vehicle Type | Status")
            self.view(taxidrivers)
            try:
                taxidriver_index = int(input("Enter ID to delete: ")) - 1
                if self.find_index(taxidriver_index, taxidrivers):
                    taxidrivers.pop(taxidriver_index)
                    print("TaxiDriver deleted.")
                else:
                    print("TaxiDriver not found.")
            except ValueError:
                print("Invalid input.")
        else:
            print("Invalid option!")

    def view_customer(self, customers):
        """View customers"""
        print("-----View Customers-----")
        print("ID | Full Name | TaxiDriver | Age | Mobile | Postcode")
        self.view(customers)

    def assign_taxi_driver_to_customer(self, customers, taxidrivers):
        """Assign taxidriver"""
        print("-----Assign-----")
        self.view(customers)
        customer_index = input("Enter customer ID: ")

        try:
            customer_index = int(customer_index) - 1
            if customer_index not in range(len(customers)):
                print("Invalid customer ID")
                return False
        except ValueError:
            print("Invalid input")
            return False

        print("-----TaxiDrivers-----")
        self.view(taxidrivers)
        taxidriver_index = input("Enter TaxiDriver ID: ")

        try:
            taxidriver_index = int(taxidriver_index) - 1
            if self.find_index(taxidriver_index, taxidrivers):
                driver = taxidrivers[taxidriver_index]
                if driver.get_status() != TaxiDriver.STATUS_AVAILABLE:
                    print(f"Driver is {driver.get_status()} and cannot be assigned.")
                    return False
                customer = customers[customer_index]
                customer.link(driver.full_name())
                driver.add_customer(customer)
                driver.set_status(TaxiDriver.STATUS_ON_RIDE)
                print(f"Assigned {driver.full_name()} to {customer.full_name()}.")
                return True
            print("Invalid TaxiDriver ID")
        except ValueError:
            print("Invalid input")
        return False

    def complete_ride(self, customers, completed_customers, taxidrivers, rides, distance_km, next_ride_id):
        """Mark customer ride as completed and record ride."""
        from Ride import Ride

        print("-----Complete Ride-----")
        customer_index = input("Enter Customer ID: ")
        try:
            customer_index = int(customer_index) - 1
            if customer_index not in range(len(customers)):
                print("Invalid customer ID")
                return None, next_ride_id
        except ValueError:
            print("Invalid input")
            return None, next_ride_id

        customer = customers[customer_index]
        driver_name = customer.get_taxi_driver()
        if driver_name == "None":
            print("Customer has no assigned driver.")
            return None, next_ride_id

        driver = None
        for d in taxidrivers:
            if d.full_name() == driver_name:
                driver = d
                break

        vehicle_type = driver.get_vehicle_type() if driver else "Sedan"
        fare = calculate_fare(distance_km, vehicle_type)
        ride = Ride(
            customer.full_name(),
            driver_name,
            distance_km,
            fare,
            vehicle_type,
            ride_id=next_ride_id,
        )
        rides.append(ride)
        completed_customers.append(customer)
        customers.pop(customer_index)
        if driver:
            driver.set_status(TaxiDriver.STATUS_AVAILABLE)
        print(f"Ride completed. Fare: £{fare:.2f}")
        return ride, next_ride_id + 1

    def view_completed(self, completed_customers):
        """View completed customers"""
        print("-----Completed Customers-----")
        self.view(completed_customers)

    def update_details(self):
        """Update admin details"""
        print("Choose field:")
        print("1 Username\n2 Password\n3 Address")
        try:
            op = int(input("Input: "))
        except ValueError:
            print("Invalid option!")
            return

        if op == 1:
            ok, username = validate_username(input("New Username: "))
            if ok:
                self.__username = username
        elif op == 2:
            password = input("New Password: ")
            if password == input("Confirm password: "):
                ok, password = validate_password(password)
                if ok:
                    self.__password = password
        elif op == 3:
            ok, address = validate_postcode(input("New Address (postcode): "))
            if ok:
                self.__address = address
        else:
            print("Invalid option!")
