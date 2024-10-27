import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

data = pd.read_csv('data.csv')

X = data[['Latitude', 'Longitude', 'DistanceToEye']]
y = data['DamageSeverity']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)

def predict_severity(latitude, longitude, distance_to_eye):
    new_data = np.array([[latitude, longitude, distance_to_eye]])
    prediction = rf_model.predict(new_data)
    return prediction[0]

with open('predicted_data.csv', 'a') as file:
    file.write('Latitude,Longitude,DamageSeverity,DistanceToEye')
    file.write('\n')

coordinates_data = [
    [18.2, -64.0, 35],
    [18.8, -65.4, 50],
    [21.1, -71.8, 70],
    [25.4, -80.1, 85],
    [25.59, -80.29, 110],
    [25.75, -80.35, 115],
    [25.85, -80.56, 185],
    [25.92, -80.77, 185],
    [26.04, -81.62, 295],
    [26.11, -81.69, 295],
    [26.15, -81.73, 360],
    [26.739, -81.77, 295],
    [29.5, -82.9, 185],
    [30.3, -83.1, 115],
    [33.0, -85.2, 70]
]

for coordinate in coordinates_data:
    with open('predicted_data.csv', 'a') as file:
        severity = predict_severity(coordinate[0], coordinate[1], coordinate[2])
        file.write(f"{coordinate[0]},{coordinate[1]},{severity},{coordinate[2]}")
        file.write('\n')