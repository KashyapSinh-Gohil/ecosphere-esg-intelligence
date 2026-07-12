"""
Scope 1 Carbon Calculator
Calculates direct emissions from sources owned or controlled by the organization.
"""

# IPCC / EPA default emission factors and GWPs (Global Warming Potentials)
FUEL_EMISSION_FACTORS = {
    "natural_gas": 0.0543,    # kg CO2e per cubic foot
    "diesel": 10.21,          # kg CO2e per gallon
    "gasoline": 8.78,         # kg CO2e per gallon
    "coal": 2.25,             # kg CO2e per kg
}

VEHICLE_EMISSION_FACTORS = {
    "passenger_car": 0.17,    # kg CO2e per km
    "light_truck": 0.22,      # kg CO2e per km
    "heavy_truck": 0.85,      # kg CO2e per km
}

REFRIGERANT_GWP = {
    "HFC-134a": 1430,         # GWP relative to CO2
    "R-410A": 2088,
    "R-404A": 3922,
    "CO2": 1,
}

def calculate_stationary_combustion(fuel_type: str, quantity: float) -> float:
    """
    Calculate emissions from stationary combustion of fuels.
    
    Formula: CO2e (kg) = Fuel Quantity * Emission Factor
    """
    factor = FUEL_EMISSION_FACTORS.get(fuel_type.lower())
    if factor is None:
        raise ValueError(f"Unknown fuel type: {fuel_type}. Supported: {list(FUEL_EMISSION_FACTORS.keys())}")
    return quantity * factor

def calculate_mobile_combustion(vehicle_type: str, distance_km: float) -> float:
    """
    Calculate emissions from company-owned mobile assets.
    
    Formula: CO2e (kg) = Distance (km) * Emission Factor
    """
    factor = VEHICLE_EMISSION_FACTORS.get(vehicle_type.lower())
    if factor is None:
        raise ValueError(f"Unknown vehicle type: {vehicle_type}. Supported: {list(VEHICLE_EMISSION_FACTORS.keys())}")
    return distance_km * factor

def calculate_fugitive_emissions(refrigerant_type: str, leakage_kg: float) -> float:
    """
    Calculate direct fugitive emissions from refrigerant leaks.
    
    Formula: CO2e (kg) = Leakage (kg) * Global Warming Potential (GWP)
    """
    gwp = REFRIGERANT_GWP.get(refrigerant_type)
    if gwp is None:
        raise ValueError(f"Unknown refrigerant type: {refrigerant_type}. Supported: {list(REFRIGERANT_GWP.keys())}")
    return leakage_kg * gwp

def calculate_total_scope1(stationary_fuels: list, mobile_trips: list, fugitive_leaks: list) -> float:
    """
    Aggregates all Scope 1 components into total kg CO2e.
    """
    total = 0.0
    for fuel, qty in stationary_fuels:
        total += calculate_stationary_combustion(fuel, qty)
    for v_type, dist in mobile_trips:
        total += calculate_mobile_combustion(v_type, dist)
    for r_type, leak in fugitive_leaks:
        total += calculate_fugitive_emissions(r_type, leak)
    return total
