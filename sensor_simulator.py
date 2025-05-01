import random
import time
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SensorThresholds:
    temp_min: float = 38.0  # °C
    temp_max: float = 39.5  # °C
    activity_min: int = 20   # steps/hour
    activity_max: int = 100  # steps/hour
    heart_rate_min: int = 60  # bpm
    heart_rate_max: int = 90  # bpm
    resp_rate_min: int = 20   # breaths/min
    resp_rate_max: int = 40   # breaths/min
    rumen_ph_min: float = 5.8
    rumen_ph_max: float = 6.8

class AnimalSensor:
    AVAILABLE_SENSORS = {
        "S1": "Temperature & Activity Sensor",
        "S2": "Heart Rate Monitor",
        "S3": "Respiration Sensor",
        "S4": "Rumen pH Monitor"
    }

    def __init__(self, animal_id):
        self.animal_id = animal_id
        self.sensor_id = None
        self.thresholds = None
        self.is_connected = False

    def link_to_animal(self, animal_record):
        """Link sensor to animal and use its thresholds"""
        if animal_record and animal_record.sensor_id in self.AVAILABLE_SENSORS:
            self.sensor_id = animal_record.sensor_id
            self.is_connected = True
            self.thresholds = SensorThresholds(
                temp_min=animal_record.temp_min,
                temp_max=animal_record.temp_max,
                activity_min=animal_record.activity_min,
                activity_max=animal_record.activity_max,
                heart_rate_min=animal_record.heart_rate_min,
                heart_rate_max=animal_record.heart_rate_max,
                resp_rate_min=animal_record.resp_rate_min,
                resp_rate_max=animal_record.resp_rate_max,
                rumen_ph_min=animal_record.rumen_ph_min,
                rumen_ph_max=animal_record.rumen_ph_max
            )
            return True
        return False

    def generate_reading(self):
        if not self.sensor_id or not self.thresholds:
            return None
            
        # Simulate occasional abnormal readings
        abnormal = random.random() < 0.2  # 20% chance of abnormal reading
        
        if abnormal:
            # Generate reading outside normal range
            temp = random.choice([
                random.uniform(37.0, self.thresholds.temp_min - 0.5),
                random.uniform(self.thresholds.temp_max + 0.5, 41.0)
            ])
            activity = random.choice([
                random.randint(0, self.thresholds.activity_min - 5),
                random.randint(self.thresholds.activity_max + 10, 150)
            ])
            heart_rate = random.choice([
                random.randint(40, self.thresholds.heart_rate_min - 5),
                random.randint(self.thresholds.heart_rate_max + 5, 120)
            ])
            resp_rate = random.choice([
                random.randint(10, self.thresholds.resp_rate_min - 2),
                random.randint(self.thresholds.resp_rate_max + 2, 60)
            ])
            rumen_ph = random.choice([
                random.uniform(5.0, self.thresholds.rumen_ph_min - 0.2),
                random.uniform(self.thresholds.rumen_ph_max + 0.2, 7.5)
            ])
        else:
            # Generate normal reading
            temp = random.uniform(self.thresholds.temp_min, self.thresholds.temp_max)
            activity = random.randint(self.thresholds.activity_min, self.thresholds.activity_max)
            heart_rate = random.randint(self.thresholds.heart_rate_min, self.thresholds.heart_rate_max)
            resp_rate = random.randint(self.thresholds.resp_rate_min, self.thresholds.resp_rate_max)
            rumen_ph = random.uniform(self.thresholds.rumen_ph_min, self.thresholds.rumen_ph_max)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "animal_id": self.animal_id,
            "temperature": round(temp, 2),
            "activity": activity,
            "heart_rate": heart_rate,
            "respiration_rate": resp_rate,
            "rumen_ph": round(rumen_ph, 2)
        }