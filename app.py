from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import pandas as pd
import os

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Fashion"
mongo = PyMongo(app)

# Static folder for images
STATIC_FOLDER = "static/images"

# Load the dataset
try:
    dataset = pd.read_csv("cleaned_styles.csv")
    dataset = dataset[
        (dataset['masterCategory'] == 'Apparel') &
        (dataset['subCategory'] != 'Innerwear')
        ]
except Exception as e:
    print(f"Error loading dataset: {e}")
    dataset = pd.DataFrame()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/save_preferences", methods=["POST"])
def save_preferences():
    data = request.json
    username = data.get("username")
    if username:
        mongo.db.user_preferences.update_one(
            {"username": username},
            {"$set": {"preferences": data.get("preferences", {})}},
            upsert=True,
        )
        return jsonify({"message": "Preferences saved successfully!"})
    return jsonify({"message": "Username not provided!"}), 400

@app.route("/get_recommendations", methods=["GET"])
def get_recommendations():
    username = request.args.get("username")  # Pass username as a query parameter
    user_preferences = mongo.db.user_preferences.find_one({"username": username})

    if not user_preferences:
        return jsonify({"message": "No preferences found!", "recommendations": []})

    # Extract user preferences
    preferred_style = user_preferences.get("preferences", {}).get("preferredStyle", "").lower()
    preferred_colors = user_preferences.get("preferences", {}).get("preferredColors", [])
    preferred_colors = [color.lower() for color in preferred_colors]

    # Filter the dataset based on preferences
    recommendations = dataset[
        (dataset["usage"].str.lower() == preferred_style)
        & (dataset["baseColour"].str.lower().isin(preferred_colors))
    ]

    recommendations = recommendations.head(50)
    # Get recommendations (assume images are named as "<id>.jpg")
    recommendation_list = [
        {
            "id": row["id"],
            "productName": row["productDisplayName"],
            "image": f"/static/images/{row['id']}.jpg"
        }
        for _, row in recommendations.iterrows()
    ]

    if not recommendation_list:
        return jsonify({"message": "No matching recommendations found!", "recommendations": []})

    return jsonify({"message": "Recommendations found!", "recommendations": recommendation_list})

if __name__ == "__main__":
    app.run(debug=True)
