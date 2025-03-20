from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle
from flask import Flask, request, jsonify

# Load and train model
iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)
print(f"Model Accuracy: {model.score(X_test, y_test):.2f}")
with open("model1.pkl", "wb") as f:
    pickle.dump(model, f)

# Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Iris Prediction API! Use /predict to make predictions."})

@app.route('/predict', methods=['GET'])
def predict():
    with open("model1.pkl", "rb") as f:
        loaded_model = pickle.load(f)
    features = [
        float(request.args.get('sepal_length')),
        float(request.args.get('sepal_width')),
        float(request.args.get('petal_length')),
        float(request.args.get('petal_width'))
    ]
    prediction = loaded_model.predict([features])[0]
    return jsonify({
        "prediction": int(prediction),
        "class_name": iris.target_names[prediction],
        "model": "LogisticRegression"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)  # Changed to 5001