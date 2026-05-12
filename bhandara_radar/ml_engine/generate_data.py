import pandas as pd
import random

def generate_mock_bhandara_data():
    data = []
    # 0 = Low, 1 = Moderate, 2 = High
    areas = ['Alambagh', 'Hazratganj', 'Gomti Nagar', 'Charbagh', 'Aminabad', 'Jankipuram']
    
    for i in range(500):
        hour = random.randint(10, 22) # 10 AM to 10 PM
        day = random.randint(0, 6)    # 0 = Monday, 1 = Tuesday...
        area_density = random.randint(1, 10) # 10 = extremely busy area
        
        # Logic: Higher crowds on Tuesday (1) and during lunch hours (13-15)
        if day == 1 or (13 <= hour <= 15):
            crowd = random.choices([1, 2], weights=[30, 70])[0]
        else:
            crowd = random.choices([0, 1], weights=[70, 30])[0]
            
        data.append([hour, day, area_density, crowd])
    
    df = pd.DataFrame(data, columns=['hour', 'day_of_week', 'area_score', 'crowd_level'])
    df.to_csv('bhandara_radar/ml_engine/bhandara_training_data.csv', index=False)
    print("✅ Training data generated: 500 records saved.")

if __name__ == "__main__":
    generate_mock_bhandara_data()