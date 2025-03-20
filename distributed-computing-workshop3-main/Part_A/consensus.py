import requests
import json
from sklearn.datasets import load_iris

# Load model info
with open("model_db.json", "r") as f:
    model_info = json.load(f)

params = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
true_label = 1

predictions = []
for model_name, info in model_info.items():
    try:
        response = requests.get(info["url"], params=params)
        print(f"URL: {info['url']}, Status: {response.status_code}, Response: {response.text}")
        pred = response.json()["prediction"]
        predictions.append((model_name, pred))
    except Exception as e:
        print(f"Error with {model_name}: {e}")

def slash_and_update(true_label, predictions, model_info, slash_amount=100):
    for model_name, pred in predictions:
        info = model_info[model_name]
        if pred != true_label:
            info["balance"] -= slash_amount
            info["weight"] = max(0.0, info["weight"] - 0.2)
        else:
            info["weight"] = min(1.0, info["weight"] + 0.1)
        if info["balance"] <= 0:
            print(f"{model_name} eliminated!")
            del model_info[model_name]
    return model_info

def weighted_consensus(predictions, model_info):
    weighted_preds = {}
    for model_name, pred in predictions:
        weighted_preds[pred] = weighted_preds.get(pred, 0) + model_info[model_name]["weight"]
    return max(weighted_preds, key=weighted_preds.get) if weighted_preds else None

if predictions:
    model_info = slash_and_update(true_label, predictions, model_info)
    consensus = weighted_consensus(predictions, model_info)
    with open("model_db.json", "w") as f:
        json.dump(model_info, f)

    iris = load_iris()
    print(f"Weighted Consensus: {consensus} ({iris.target_names[consensus]})")
    print("Updated Model Info:", model_info)
else:
    print("No valid predictions collected.")