from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import pandas as pd
import os
from PIL import Image

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/Fashion"
mongo = PyMongo(app)

# Static folder for images
STATIC_FOLDER = "static/images"
RESIZED_FOLDER = "static/resized_images"

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

def resize_images(image_paths, output_folder, size=(30, 40)):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for image_path in image_paths:
        try:
            img = Image.open(image_path)
            img = img.resize(size, Image.ANTIALIAS)
            img.save(os.path.join(output_folder, os.path.basename(image_path)))
        except Exception as e:
            print(f"Error resizing image {image_path}: {e}")    

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/register')
def register():
    return render_template('register.html')

@app.route("/dashboard")
def dashboard():
    return render_template("home.html")
@app.route("/my_wardrobe")
def my_wardrobe():
    return render_template("MyWardrobe.html")

@app.route("/profile")
def profile():
    return render_template("Profile.html")

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
    # Resize images
    image_paths = [os.path.join(STATIC_FOLDER, f"{row['id']}.jpg") for _, row in recommendations.iterrows()]
    resize_images(image_paths, RESIZED_FOLDER)

    if not recommendation_list:
        return jsonify({"message": "No matching recommendations found!", "recommendations": []})

    return jsonify({"message": "Recommendations found!", "recommendations": recommendation_list})

BASE_DIR = "Clothing"
CATEGORIES = {
    "male": os.path.join(BASE_DIR, "MenClothing"),
    "female": os.path.join(BASE_DIR, "WomenClothing")
}
@app.route('/get_images', methods=['POST'])
def get_images():
    data = request.get_json()
    gender = data.get("gender").lower()

    if gender not in CATEGORIES:
        return jsonify({"error": "Invalid gender"}), 400

    # Get image file names from the respective folder
    image_folder = CATEGORIES[gender]
    images = [f"/static/{gender}/{img}" for img in os.listdir(image_folder) if img.endswith(('png', 'jpg', 'jpeg','webp'))]

    return jsonify({"images": images})

if __name__ == "__main__":
    app.run(debug=True)
