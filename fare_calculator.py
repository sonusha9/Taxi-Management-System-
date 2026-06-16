BASE_FARE = 3.50
PER_KM_RATES = {
    "Sedan": 1.80,
    "SUV": 2.20,
    "Van": 2.50,
    "Estate": 2.00,
    "Minibus": 3.00,
}


def calculate_fare(distance_km, vehicle_type):
    """Calculate ride fare from distance and vehicle type."""
    rate = PER_KM_RATES.get(vehicle_type, PER_KM_RATES["Sedan"])
    fare = BASE_FARE + (distance_km * rate)
    return round(fare, 2)


def fare_breakdown(distance_km, vehicle_type):
    rate = PER_KM_RATES.get(vehicle_type, PER_KM_RATES["Sedan"])
    distance_charge = round(distance_km * rate, 2)
    total = round(BASE_FARE + distance_charge, 2)
    return {
        "base_fare": BASE_FARE,
        "rate_per_km": rate,
        "distance_km": distance_km,
        "distance_charge": distance_charge,
        "total": total,
    }
