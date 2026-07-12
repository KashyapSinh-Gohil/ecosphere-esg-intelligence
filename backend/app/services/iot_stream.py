import asyncio
import random
from datetime import datetime
from typing import AsyncGenerator

async def generate_iot_telemetry() -> AsyncGenerator[dict, None]:
    """
    Simulates real-time IoT energy/emission sensor telemetry from factory machines.
    """
    machines = ["CNC_Milling_01", "Assembly_Line_A", "Hvac_Unit_East", "Fleet_Truck_B"]
    
    while True:
        machine = random.choice(machines)
        power_usage = round(random.uniform(5.0, 75.0), 2)
        emissions = round((0.38 / 3600.0) * power_usage, 5)
        
        yield {
            "timestamp": datetime.utcnow().isoformat(),
            "machine_id": machine,
            "power_kw": power_usage,
            "emissions_kg_co2e_sec": emissions,
            "status": "normal" if emissions < 0.007 else "high_load"
        }
        await asyncio.sleep(2.0)
