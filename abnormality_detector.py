from sensor_simulator import SensorThresholds

class AbnormalityDetector:
    def __init__(self, animal_registry):
        self.animal_registry = animal_registry
    
    def check_reading(self, reading):
        animal_id = reading["animal_id"]
        animal = self.animal_registry.get(animal_id)
        
        if not animal:
            return []
            
        abnormalities = []
        
        if reading["temperature"] < animal.temp_min:
            abnormalities.append(f"Low body temperature: {reading['temperature']}°C (min: {animal.temp_min}°C)")
        elif reading["temperature"] > animal.temp_max:
            abnormalities.append(f"High body temperature: {reading['temperature']}°C (max: {animal.temp_max}°C)")
            
        if reading["activity"] < animal.activity_min:
            abnormalities.append(f"Low activity: {reading['activity']} steps/hr (min: {animal.activity_min})")
        elif reading["activity"] > animal.activity_max:
            abnormalities.append(f"High activity: {reading['activity']} steps/hr (max: {animal.activity_max})")
            
        # Similar checks for other vital signs...
        
        return abnormalities