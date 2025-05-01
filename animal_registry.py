from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class AnimalRecord:
    animal_id: str
    name: str = ""
    breed: str = ""
    birth_date: str = ""
    notes: str = ""
    sensor_id: str = ""
    registration_date: str = ""
    # Add threshold fields
    temp_min: float = 38.0
    temp_max: float = 39.5
    activity_min: int = 20
    activity_max: int = 100
    heart_rate_min: int = 60
    heart_rate_max: int = 90
    resp_rate_min: int = 20
    resp_rate_max: int = 40
    rumen_ph_min: float = 5.8
    rumen_ph_max: float = 6.8

    def to_dict(self):
        return {
            "animal_id": self.animal_id,
            "name": self.name,
            "breed": self.breed,
            "birth_date": self.birth_date,
            "notes": self.notes,
            "sensor_id": self.sensor_id,
            "registration_date": self.registration_date,
            "thresholds": {
                "temperature": {"min": self.temp_min, "max": self.temp_max},
                "activity": {"min": self.activity_min, "max": self.activity_max},
                "heart_rate": {"min": self.heart_rate_min, "max": self.heart_rate_max},
                "respiration_rate": {"min": self.resp_rate_min, "max": self.resp_rate_max},
                "rumen_ph": {"min": self.rumen_ph_min, "max": self.rumen_ph_max}
            }
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_text(self):
        """Convert to text format for FAISS embedding"""
        thresholds_text = f"""
        Vital Signs Thresholds:
        Temperature: {self.temp_min}-{self.temp_max}°C
        Activity: {self.activity_min}-{self.activity_max} steps/hr
        Heart Rate: {self.heart_rate_min}-{self.heart_rate_max} bpm
        Respiration Rate: {self.resp_rate_min}-{self.resp_rate_max} br/min
        Rumen pH: {self.rumen_ph_min}-{self.rumen_ph_max}
        """
        
        return f"""
        Animal ID: {self.animal_id}
        Name: {self.name}
        Breed: {self.breed}
        Birth Date: {self.birth_date}
        Sensor ID: {self.sensor_id}
        Notes: {self.notes}
        Registration Date: {self.registration_date}
        {thresholds_text}
        """

    def validate_sensor(self):
        """Validate sensor ID format and existence"""
        if not self.sensor_id:
            return False
        # Add any specific sensor ID validation rules here
        return True