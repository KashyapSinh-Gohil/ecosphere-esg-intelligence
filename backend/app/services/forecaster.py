from datetime import datetime, timedelta
import math
from sqlalchemy.orm import Session
from ..models import CarbonTransaction

def forecast_emissions(db: Session, department_id: int = None, forecast_days: int = 180) -> list:
    """
    Business Logic: Time-Series Carbon Forecasting
    """
    query = db.query(CarbonTransaction)
    if department_id:
        query = query.filter(CarbonTransaction.department_id == department_id)
    
    transactions = query.order_by(CarbonTransaction.date).all()
    if not transactions:
        return generate_default_forecast(forecast_days)
    
    daily_emissions = {}
    first_date = transactions[0].date.date()
    
    for tx in transactions:
        tx_date = tx.date.date()
        daily_emissions[tx_date] = daily_emissions.get(tx_date, 0.0) + tx.calculated_co2e
        
    dates_sorted = sorted(daily_emissions.keys())
    x_days = [(d - first_date).days for d in dates_sorted]
    y_vals = [daily_emissions[d] for d in dates_sorted]
    
    if len(y_vals) < 3:
        return generate_default_forecast(forecast_days, base_value=sum(y_vals)/max(1, len(y_vals)))
    
    n = len(x_days)
    sum_x = sum(x_days)
    sum_y = sum(y_vals)
    sum_xx = sum(x**2 for x in x_days)
    sum_xy = sum(x*y for x, y in zip(x_days, y_vals))
    
    denom = (n * sum_xx - sum_x**2)
    if denom == 0:
        slope = 0.0
        intercept = sum_y / n
    else:
        slope = (n * sum_xy - sum_x * sum_y) / denom
        intercept = (sum_y - slope * sum_x) / n
        
    last_date = dates_sorted[-1]
    forecast_results = []
    
    for d in dates_sorted[-15:]:
        forecast_results.append({
            "date": d.isoformat(),
            "emissions": round(daily_emissions[d], 2),
            "type": "historical"
        })
        
    for step in range(1, forecast_days + 1):
        future_date = last_date + timedelta(days=step)
        t_days = (future_date - first_date).days
        
        trend_val = slope * t_days + intercept
        
        weekday = future_date.weekday()
        seasonality = 1.0
        if weekday >= 5:
            seasonality = 0.45
        else:
            seasonality = 1.0 + 0.15 * math.sin(2 * math.pi * (weekday / 5.0))
            
        forecast_val = max(10.0, trend_val * seasonality)
        
        forecast_results.append({
            "date": future_date.isoformat(),
            "emissions": round(forecast_val, 2),
            "type": "forecast"
        })
        
    return forecast_results

def generate_default_forecast(days: int, base_value: float = 120.0) -> list:
    start_date = datetime.utcnow().date()
    forecast = []
    for step in range(-10, days + 1):
        date = start_date + timedelta(days=step)
        weekday = date.weekday()
        seasonality = 0.5 if weekday >= 5 else (1.0 + 0.1 * math.sin(step / 3.0))
        growth = 1.0 + (step * 0.0005)
        emissions = max(10.0, base_value * seasonality * growth)
        
        forecast.append({
            "date": date.isoformat(),
            "emissions": round(emissions, 2),
            "type": "historical" if step <= 0 else "forecast"
        })
    return forecast
