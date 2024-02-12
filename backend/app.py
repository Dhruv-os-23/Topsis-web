from flask import Flask, request, jsonify,send_from_directory,make_response
from pymongo import MongoClient
import pandas as pd
from werkzeug.utils import secure_filename, send_from_directory,safe_join
import os
from flask_cors import CORS







app = Flask(__name__)
CORS(app)
#CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})





# MongoDB setup
MONGODB_URI = os.environ.get('MONGODB_URI')
DATABASE_NAME = os.environ.get('DATABASE_NAME')

# Establish MongoDB connection
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure UPLOAD_FOLDER exists

def allowed_file(filename):
   
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def normalize_dataset(dataset, weights):
    dataset_normalized = dataset.copy()
    for i in range(1, len(dataset.columns)):
        norm = (dataset.iloc[:, i]**2).sum()**0.5
        dataset_normalized.iloc[:, i] = (dataset.iloc[:, i] / norm) * weights[i-1]
    return dataset_normalized

def calculate_ideal_solutions(dataset, impacts):
    positive_ideal = []
    negative_ideal = []
    for i in range(1, len(dataset.columns)):
        if impacts[i-1] == '+':
            positive_ideal.append(dataset.iloc[:, i].max())
            negative_ideal.append(dataset.iloc[:, i].min())
        else:
            positive_ideal.append(dataset.iloc[:, i].min())
            negative_ideal.append(dataset.iloc[:, i].max())
    return positive_ideal, negative_ideal

def calculate_topsis_score(dataset, positive_ideal, negative_ideal):
    scores = []
    for index, row in dataset.iterrows():
        positive_distance = sum((row[1:] - positive_ideal)**2)**0.5
        negative_distance = sum((row[1:] - negative_ideal)**2)**0.5
        scores.append(negative_distance / (positive_distance + negative_distance))
    return scores

def apply_topsis(dataset, weights, impacts, output_file):
    dataset_normalized = normalize_dataset(dataset, weights)
    positive_ideal, negative_ideal = calculate_ideal_solutions(dataset_normalized, impacts)
    score = calculate_topsis_score(dataset_normalized, positive_ideal, negative_ideal)
    dataset['Topsis Score'] = score
    dataset['Rank'] = dataset['Topsis Score'].rank(method='max', ascending=False).astype(int)
    dataset.to_csv(output_file, index=False)

@app.route('/', methods=['POST'])
def process_file():
    if 'dataFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['dataFile']
    weights = request.form.get('weights', '').split(',')
    impacts = request.form.get('impact', '').split(',')
    emailid = request.form.get('emailid', '')

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'No selected file or file type not allowed'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        weights = [float(w) for w in weights]
        output_filename = f"output_{filename}"
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Load dataset
        dataset = pd.read_csv(filepath)
        # Apply TOPSIS
        apply_topsis(dataset, weights, impacts, output_file)

        # Optionally save details to MongoDB
        db['topsis_results'].insert_one({
            "emailid": emailid,
            "input_file": filename,
            "output_file": output_filename
        })

        # Generate download URL
        download_url = f"/download/{output_filename}"

        return jsonify({
            'status': 'success',
            'message': 'File processed successfully.',
            'download_url': download_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    safe_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(safe_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    return jsonify({'error': 'File not found.'}), 404

if __name__ == '__main__':
    app.run(debug=True)