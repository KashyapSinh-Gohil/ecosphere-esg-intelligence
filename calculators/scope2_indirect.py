"""
Scope 2 Carbon Calculator
Calculates indirect emissions from purchased electricity, steam, heating, and cooling.
"""

# Grid emission factors (kg CO2e per kWh) based on geographical regions
GRID_EMISSION_FACTORS = {
    "us_national_average": 0.38,
    "eu_average": 0.23,
    "india_grid": 0.82,
    "china_grid": 0.61,
    "renewable_ppa": 0.00,  # Power Purchase Agreements for green energy
}

STEAM_EMISSION_FACTORS = {
    "standard_boiler_gas": 0.18,   # kg CO2e per kg steam
    "standard_boiler_coal": 0.31,  # kg CO2e per kg steam
}

def calculate_purchased_electricity(kwh: float, region: str = "us_national_average") -> float:
    """
    Calculate emissions from purchased electricity.
    
    Formula: CO2e (kg) = Electricity (kWh) * Grid Emission Factor
    """
    factor = GRID_EMISSION_FACTORS.get(region.lower())
    if factor is None:
        raise ValueError(f"Unknown region grid: {region}. Supported: {list(GRID_EMISSION_FACTORS.keys())}")
    return kwh * factor

def calculate_purchased_steam(steam_kg: float, source: str = "standard_boiler_gas") -> float:
    """
    Calculate emissions from purchased steam, heating, or cooling.
    
    Formula: CO2e (kg) = Steam (kg) * Boiler Emission Factor
    """
    factor = STEAM_EMISSION_FACTORS.get(source.lower())
    if factor is None:
        raise ValueError(f"Unknown steam source: {source}. Supported: {list(STEAM_EMISSION_FACTORS.keys())}")
    return steam_kg * factor

def calculate_total_scope2(electricity_records: list, steam_records: list) -> float:
    """
    Aggregates all Scope 2 components into total kg CO2e.
    """
    total = 0.0
    for kwh, region in electricity_records:
        total += calculate_purchased_electricity(kwh, region)
    for kg, source in steam_records:
        total += calculate_purchased_steam(kg, source)
    return total
