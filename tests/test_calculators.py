import unittest
from calculators import scope1_direct, scope2_indirect, scope3_supply, brsr_gri_mapper

class TestEcoSphereCalculators(unittest.TestCase):
    
    def test_scope1_stationary_combustion(self):
        res = scope1_direct.calculate_stationary_combustion("natural_gas", 1000)
        self.assertAlmostEqual(res, 54.3)
        
        res_diesel = scope1_direct.calculate_stationary_combustion("diesel", 50)
        self.assertAlmostEqual(res_diesel, 510.5)

    def test_scope1_mobile_combustion(self):
        res = scope1_direct.calculate_mobile_combustion("passenger_car", 200)
        self.assertAlmostEqual(res, 34.0)

    def test_scope2_electricity(self):
        res = scope2_indirect.calculate_purchased_electricity(1000, "us_national_average")
        self.assertAlmostEqual(res, 380.0)
        
        res_ind = scope2_indirect.calculate_purchased_electricity(1000, "india_grid")
        self.assertAlmostEqual(res_ind, 820.0)

    def test_scope3_business_travel(self):
        res = scope3_supply.calculate_business_travel("flight_short_haul", 400)
        self.assertAlmostEqual(res, 96.0)

    def test_scope3_freight(self):
        res = scope3_supply.calculate_freight_transport("road_truck", 5, 100)
        self.assertAlmostEqual(res, 70.0)

    def test_brsr_mapping(self):
        res = brsr_gri_mapper.map_to_brsr_principle_6(
            scope1_co2e_kg=1200.0,
            scope2_co2e_kg=2400.0,
            scope3_co2e_kg=5000.0,
            energy_kwh=10000.0
        )
        self.assertEqual(res["disclosure_name"], "BRSR Principle 6 - Environmental Performance")
        self.assertEqual(res["greenhouse_gas_emissions"]["direct_emissions_scope_1_tco2e"], 1.2)
        self.assertEqual(res["greenhouse_gas_emissions"]["indirect_emissions_scope_2_tco2e"], 2.4)
        self.assertEqual(res["greenhouse_gas_emissions"]["scope_3_other_indirect_emissions_tco2e"], 5.0)

if __name__ == '__main__':
    unittest.main()
