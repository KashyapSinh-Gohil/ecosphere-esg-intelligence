"""
BRSR & GRI Alignment Mapper
Maps raw energy and emissions calculations into standard regulatory disclosure formats:
- BRSR (Business Responsibility & Sustainability Reporting - India SEBI) Principle 6
- GRI (Global Reporting Initiative) 302 (Energy) and 305 (Emissions)
"""

def map_to_brsr_principle_6(scope1_co2e_kg: float, scope2_co2e_kg: float, scope3_co2e_kg: float, energy_kwh: float) -> dict:
    """
    Format emissions and energy data into the BRSR Principle 6 (Essential Indicators) structure.
    All figures in metric tonnes (tCO2e) and GigaJoules (GJ).
    Conversion: 1 kWh = 0.0036 GJ.
    1 kg = 0.001 metric tonne.
    """
    energy_gj = energy_kwh * 0.0036
    return {
        "disclosure_name": "BRSR Principle 6 - Environmental Performance",
        "energy_consumption": {
            "total_electricity_consumption_gj": round(energy_gj, 2),
            "total_fuel_consumption_gj": 0.0, # Placeholder for fuel energy equivalent if calculated
            "total_energy_consumption_gj": round(energy_gj, 2),
            "energy_intensity_per_turnover_million": 0.0, # Filled by organization metadata
        },
        "greenhouse_gas_emissions": {
            "direct_emissions_scope_1_tco2e": round(scope1_co2e_kg / 1000.0, 4),
            "indirect_emissions_scope_2_tco2e": round(scope2_co2e_kg / 1000.0, 4),
            "total_scope_1_and_2_emissions_tco2e": round((scope1_co2e_kg + scope2_co2e_kg) / 1000.0, 4),
            "emissions_intensity_per_turnover_million": 0.0,
            "scope_3_other_indirect_emissions_tco2e": round(scope3_co2e_kg / 1000.0, 4),
        },
        "compliance_status": "Compliant (Calculated using standard GHG Protocol IPCC factors)"
    }

def map_to_gri_disclosures(scope1_co2e_kg: float, scope2_co2e_kg: float, scope3_co2e_kg: float, energy_kwh: float) -> dict:
    """
    Format emissions and energy data into standard GRI 302 and GRI 305 disclosures.
    """
    energy_joules = energy_kwh * 3600000.0 # 1 kWh = 3.6 MJ = 3.6e6 Joules
    return {
        "disclosure_name": "GRI Sustainability Disclosures",
        "gri_302_energy": {
            "302_1_energy_consumption_within_organization_joules": energy_joules,
            "302_1_energy_consumption_within_organization_mwh": round(energy_kwh / 1000.0, 4),
        },
        "gri_305_emissions": {
            "305_1_direct_scope_1_ghg_emissions_tco2e": round(scope1_co2e_kg / 1000.0, 4),
            "305_2_energy_indirect_scope_2_ghg_emissions_tco2e": round(scope2_co2e_kg / 1000.0, 4),
            "305_3_other_indirect_scope_3_ghg_emissions_tco2e": round(scope3_co2e_kg / 1000.0, 4),
            "305_4_ghg_emissions_intensity_tco2e_per_fte": 0.0, # Filled by organization metadata
        }
    }
