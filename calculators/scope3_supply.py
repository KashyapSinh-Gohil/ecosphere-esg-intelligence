"""
Scope 3 Carbon Calculator
Calculates indirect value chain emissions including business travel, employee commuting, and transport logistics.
"""

# Flight, rail, and vehicle emission factors (kg CO2e per passenger-km)
TRAVEL_EMISSION_FACTORS = {
    "flight_short_haul": 0.24,  # < 500 km
    "flight_medium_haul": 0.19, # 500 - 1600 km
    "flight_long_haul": 0.15,  # > 1600 km
    "train": 0.04,
    "taxi_or_car": 0.18,
}

# Freight/logistics emission factors (kg CO2e per ton-km, weight in metric tons, distance in km)
FREIGHT_EMISSION_FACTORS = {
    "air_cargo": 0.96,
    "sea_cargo": 0.012,
    "road_truck": 0.14,
    "rail_freight": 0.022,
}

def calculate_business_travel(travel_type: str, distance_km: float) -> float:
    """
    Calculate emissions from business travel.
    
    Formula: CO2e (kg) = Distance (passenger-km) * Emission Factor
    """
    factor = TRAVEL_EMISSION_FACTORS.get(travel_type.lower())
    if factor is None:
        raise ValueError(f"Unknown travel type: {travel_type}. Supported: {list(TRAVEL_EMISSION_FACTORS.keys())}")
    return distance_km * factor

def calculate_freight_transport(mode: str, weight_metric_tons: float, distance_km: float) -> float:
    """
    Calculate emissions from supply chain logistics and shipping.
    
    Formula: CO2e (kg) = Weight (tons) * Distance (km) * Cargo Mode Factor
    """
    factor = FREIGHT_EMISSION_FACTORS.get(mode.lower())
    if factor is None:
        raise ValueError(f"Unknown freight mode: {mode}. Supported: {list(FREIGHT_EMISSION_FACTORS.keys())}")
    return weight_metric_tons * distance_km * factor

def calculate_employee_commuting(num_employees: int, working_days: int, avg_distance_km: float, transport_type: str = "taxi_or_car") -> float:
    """
    Calculate emissions from employee commuting.
    
    Formula: CO2e (kg) = Employees * Days * Average Round-trip Distance * Factor
    """
    factor = TRAVEL_EMISSION_FACTORS.get(transport_type.lower(), 0.18)
    # Factor is per passenger-km. Distance is the roundtrip distance.
    return num_employees * working_days * avg_distance_km * factor

def calculate_total_scope3(travel_records: list, freight_records: list, commuting_records: list) -> float:
    """
    Aggregates all Scope 3 components into total kg CO2e.
    """
    total = 0.0
    for t_type, dist in travel_records:
        total += calculate_business_travel(t_type, dist)
    for mode, weight, dist in freight_records:
        total += calculate_freight_transport(mode, weight, dist)
    for emp_count, days, dist, mode in commuting_records:
        total += calculate_employee_commuting(emp_count, days, dist, mode)
    return total
