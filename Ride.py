from datetime import datetime


class Ride:
    def __init__(
        self,
        customer_name,
        driver_name,
        distance_km,
        fare,
        vehicle_type,
        completed_at=None,
        ride_id=None,
    ):
        self.ride_id = ride_id
        self.customer_name = customer_name
        self.driver_name = driver_name
        self.distance_km = distance_km
        self.fare = fare
        self.vehicle_type = vehicle_type
        self.completed_at = completed_at or datetime.now()

    def to_dict(self):
        return {
            "ride_id": self.ride_id,
            "customer_name": self.customer_name,
            "driver_name": self.driver_name,
            "distance_km": self.distance_km,
            "fare": self.fare,
            "vehicle_type": self.vehicle_type,
            "completed_at": self.completed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data):
        ride = cls(
            data["customer_name"],
            data["driver_name"],
            data["distance_km"],
            data["fare"],
            data["vehicle_type"],
            datetime.fromisoformat(data["completed_at"]),
            data.get("ride_id"),
        )
        return ride

    def __str__(self):
        date_str = self.completed_at.strftime("%Y-%m-%d %H:%M")
        return (
            f"{self.customer_name:^25}|{self.driver_name:^25}|"
            f"{self.distance_km:>6.1f} km|£{self.fare:>7.2f}|{date_str}"
        )
