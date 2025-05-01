from fpdf import FPDF
from datetime import datetime, timedelta
import random

class RecordGenerator:
    def __init__(self):
        self.breeds = ["Holstein", "Jersey", "Angus", "Hereford", "Simmental"]
        self.medications = ["Antibiotics", "Anti-inflammatory", "Vitamins", "Minerals", "Vaccines"]
        self.feeds = ["Hay", "Silage", "Grain Mix", "Pasture", "Protein Supplement"]
        self.behaviors = ["Normal", "Aggressive", "Lethargic", "Active", "Stressed"]
        self.certifications = ["Organic", "Animal Welfare Approved", "GAP Level 4", "Humane Certified"]

    def generate_health_record(self, animal_id):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Health and Medical Record - Animal ID: {animal_id}", ln=True)
        pdf.set_font("Arial", "", 12)
        
        # Generate past year of health records
        current_date = datetime.now()
        for i in range(12):
            date = (current_date - timedelta(days=30*i)).strftime("%Y-%m-%d")
            treatment = random.choice(self.medications)
            condition = random.choice(["Routine Check", "Minor Infection", "Vaccination", "Health Check"])
            pdf.multi_cell(0, 10, f"""
Date: {date}
Condition: {condition}
Treatment: {treatment}
Veterinarian: Dr. {'ABCDE'[i % 5]} Smith
Notes: {condition} - treatment administered as per protocol
            """)

        return pdf

    def generate_feeding_record(self, animal_id):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Feeding and Nutrition Record - Animal ID: {animal_id}", ln=True)
        pdf.set_font("Arial", "", 12)

        for i in range(6):
            month = (datetime.now() - timedelta(days=30*i)).strftime("%B %Y")
            feed_type = random.choice(self.feeds)
            quantity = random.randint(15, 25)
            pdf.multi_cell(0, 10, f"""
Month: {month}
Feed Type: {feed_type}
Daily Quantity: {quantity}kg
Supplements: Mineral Mix {random.randint(1, 3)}kg
Notes: Feed intake normal, good appetite
            """)

        return pdf

    def generate_behavior_record(self, animal_id):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Behavior and Welfare Record - Animal ID: {animal_id}", ln=True)
        pdf.set_font("Arial", "", 12)

        for i in range(6):
            date = (datetime.now() - timedelta(days=30*i)).strftime("%Y-%m-%d")
            behavior = random.choice(self.behaviors)
            pdf.multi_cell(0, 10, f"""
Date: {date}
Behavior Pattern: {behavior}
Social Interaction: {'Good' if behavior != 'Aggressive' else 'Poor'}
Welfare Score: {random.randint(7, 10)}/10
Notes: {'Normal behavior observed' if behavior == 'Normal' else f'Monitoring due to {behavior.lower()} behavior'}
            """)

        return pdf

    def generate_economic_record(self, animal_id):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Economic and Asset Record - Animal ID: {animal_id}", ln=True)
        pdf.set_font("Arial", "", 12)

        purchase_date = (datetime.now() - timedelta(days=random.randint(500, 1000))).strftime("%Y-%m-%d")
        purchase_price = random.randint(1500, 3000)
        
        pdf.multi_cell(0, 10, f"""
Purchase Information:
Date Acquired: {purchase_date}
Purchase Price: ${purchase_price}
Source: Local Auction

Monthly Costs:
Feed: ${random.randint(150, 250)}
Healthcare: ${random.randint(50, 150)}
Labor: ${random.randint(100, 200)}

Production Value:
Milk Production: {random.randint(25, 35)} liters/day
Quality Grade: {'A' if random.random() > 0.2 else 'B'}
            """)

        return pdf

    def generate_compliance_record(self, animal_id):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Compliance and Certification Record - Animal ID: {animal_id}", ln=True)
        pdf.set_font("Arial", "", 12)

        certifications = random.sample(self.certifications, 2)
        for cert in certifications:
            issue_date = (datetime.now() - timedelta(days=random.randint(100, 300))).strftime("%Y-%m-%d")
            expiry_date = (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            pdf.multi_cell(0, 10, f"""
Certification: {cert}
Issue Date: {issue_date}
Expiry Date: {expiry_date}
Status: Active
Auditor: {'ABCDE'[random.randint(0, 4)]} Certification Body
            """)

        return pdf

def generate_all_records():
    generator = RecordGenerator()
    
    for animal_id in range(1, 6):
        id_str = f"0{animal_id}"
        
        # Generate each type of record
        generator.generate_health_record(id_str).output(f"records/health_record_{id_str}.pdf")
        generator.generate_feeding_record(id_str).output(f"records/feeding_record_{id_str}.pdf")
        generator.generate_behavior_record(id_str).output(f"records/behavior_record_{id_str}.pdf")
        generator.generate_economic_record(id_str).output(f"records/economic_record_{id_str}.pdf")
        generator.generate_compliance_record(id_str).output(f"records/compliance_record_{id_str}.pdf")

if __name__ == "__main__":
    import os
    
    # Create records directory if it doesn't exist
    if not os.path.exists("records"):
        os.makedirs("records")
    
    generate_all_records()
    print("✅ Generated all dummy records successfully!")