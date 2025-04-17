from flask import Flask, render_template, request, jsonify  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import xgboost as xgb  # type: ignore
import os
import json
import traceback

app = Flask(__name__)

# Load the XGBoost model
def load_model():
    with open('models/xgboost_model.json', 'r') as f:
        model_json = json.load(f)
    model = xgb.Booster()
    model.load_model('models/xgboost_model.json')
    return model
def load_dataset():
    # Specify the correct delimiter (semicolon)
    df = pd.read_csv('models/wine_quality_red.csv', sep=";")
    
    # Print out the columns to debug the issue
    print("Columns in the dataset:", df.columns)
    
    # Make sure 'quality' column exists before proceeding
    if 'quality' not in df.columns:
        raise ValueError("The 'quality' column is missing from the dataset")
    
    X = df.drop('quality', axis=1)
    y = df['quality']
    
    # Consider wine with quality >= 6 as good
    df['good_quality'] = [1 if quality >= 6 else 0 for quality in df['quality']]
    
    return df, X.columns

# Initialize model and data
model = load_model()
df, feature_names = load_dataset()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Collect the input features from the form
        features = {}
        for feature in feature_names:
            features[feature] = float(request.form.get(feature, 0))
        
        # Prepare the input data for prediction
        input_data = np.array([features[feature] for feature in feature_names]).reshape(1, -1)
        
        # Convert input data to DMatrix for XGBoost
        dmatrix = xgb.DMatrix(input_data)
        
        # Make prediction
        prediction = model.predict(dmatrix)[0]
        
        # Determine the quality (Good or Bad)
        quality_label = "Good" if prediction >= 0.5 else "Bad"
        
        # Calculate confidence score (0-10 scale)
        confidence_score = round(prediction * 10, 1)
        
        # Render the result.html template with prediction and features
        return render_template('result.html !!!', 
                               prediction=quality_label, 
                               confidence=confidence_score, 
                               features=features)

if __name__ == '__main__':
    # Set port and host for Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
