class Customer:

    def __init__(self, first_name, surname, age, mobile, postcode):
        self.__first_name = first_name
        self.__surname = surname
        self.__age = age
        self.__mobile = mobile
        self.__postcode = postcode
        self.__taxi_driver = "None"

    def full_name(self):
        return f"{self.__first_name} {self.__surname}"

    def get_first_name(self):
        return self.__first_name

    def get_surname(self):
        return self.__surname

    def get_age(self):
        return self.__age

    def get_mobile(self):
        return self.__mobile

    def get_postcode(self):
        return self.__postcode

    def set_age(self, age):
        self.__age = age

    def set_mobile(self, mobile):
        self.__mobile = mobile

    def set_postcode(self, postcode):
        self.__postcode = postcode

    def get_taxi_driver(self):
        return self.__taxi_driver

    def link(self, taxi_driver):
        self.__taxi_driver = taxi_driver

    def print_requirements(self):
        print(f"Full Name: {self.full_name()}")
        print(f"Age: {self.__age}")
        print(f"Mobile: {self.__mobile}")
        print(f"Postcode: {self.__postcode}")
        print(f"Taxi Driver: {self.__taxi_driver}")

    def to_dict(self):
        return {
            "first_name": self.__first_name,
            "surname": self.__surname,
            "age": self.__age,
            "mobile": self.__mobile,
            "postcode": self.__postcode,
            "taxi_driver": self.__taxi_driver,
        }

    @classmethod
    def from_dict(cls, data):
        customer = cls(
            data["first_name"],
            data["surname"],
            data["age"],
            data["mobile"],
            data["postcode"],
        )
        customer.link(data.get("taxi_driver", "None"))
        return customer

    def __str__(self):
        return (
            f"{self.full_name():^30}|{self.__taxi_driver:^30}|"
            f"{self.__age:^5}|{self.__mobile:^15}|{self.__postcode:^10}"
        )
