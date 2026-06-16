class TaxiDriver:
    STATUS_AVAILABLE = "Available"
    STATUS_ON_RIDE = "On Ride"
    STATUS_OFFLINE = "Offline"

    def __init__(self, first_name, surname, vehicle_type, status=None):
        self.__first_name = first_name
        self.__surname = surname
        self.__vehicle_type = vehicle_type
        self.__customers = []
        self.__bookings = []
        self.__status = status or self.STATUS_AVAILABLE

    def full_name(self):
        return f"{self.__first_name} {self.__surname}"

    def get_first_name(self):
        return self.__first_name

    def set_first_name(self, new_first_name):
        self.__first_name = new_first_name

    def get_surname(self):
        return self.__surname

    def set_surname(self, new_surname):
        self.__surname = new_surname

    def get_vehicle_type(self):
        return self.__vehicle_type

    def set_vehicle_type(self, new_vehicle_type):
        self.__vehicle_type = new_vehicle_type

    def get_status(self):
        return self.__status

    def set_status(self, status):
        if status in (self.STATUS_AVAILABLE, self.STATUS_ON_RIDE, self.STATUS_OFFLINE):
            self.__status = status

    def add_customer(self, customer):
        self.__customers.append(customer)

    def to_dict(self):
        return {
            "first_name": self.__first_name,
            "surname": self.__surname,
            "vehicle_type": self.__vehicle_type,
            "status": self.__status,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["first_name"],
            data["surname"],
            data["vehicle_type"],
            data.get("status", cls.STATUS_AVAILABLE),
        )

    def __str__(self):
        return f"{self.full_name():^30}|{self.__vehicle_type:^15}|{self.__status:^12}"
