from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import cloudinary
import cloudinary.uploader
from datetime import datetime





ap_data = [
    {"image": "image1.png", "title": "జగన్ అక్రమాలపై తిరుమలలో సిట్ తనిఖీలు ముమ్మరం.", "description": "వైఎస్ హయాంలో జరిగిన అక్రమాలపై దర్యాప్తును వేగవంతం చేసిన సిట్జగన్ హయాం.", "date": "14/12/2024"},
]

right_data = [
    {"title": "స్పోర్ట్స్ కోటాలో Mega DSC ఉద్యోగాలు.. ‘సెటిల్‌మెంట్‌’ పేరిటజోరుగా మామూళ్లు వసూలు!"}
]

b_left_data = [
    {"image": "image1", "title": "ఇప్పుడు పోస్టల్‌ సేవలు మరింత స్మార్ట్‌.. అడ్వాన్స్‌డ్‌ టెక్నాలజీ"},
]

b_right_data = [
    {"id": "స్పోర్ట్స్ కోటాలో Mega DSC ఉద్యోగాలు.. ‘సెటిల్‌మెంట్‌’ పేరిటజోరుగా మామూళ్లు వసూలు!"}
]



# ----------------------------
# App Configuration
# ----------------------------
app = Flask(__name__)
CORS(app)

# MySQL DB Credentials
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "12345"
DB_NAME = "cvr"

# Cloudinary Configuration
cloudinary.config(
    cloud_name="desc19eyc",
    api_key="779295713681398",
    api_secret="uKzfcnOrHydP1jBqwbS3MQhdGkk"
)

# UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# ----------------------------
# Utility Functions
# ----------------------------
def get_db_connection():
    """Connect to MySQL database and return connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_to_cloudinary(file):
    """Upload image to Cloudinary and return URL"""
    if file and allowed_file(file.filename):
        try:
            result = cloudinary.uploader.upload(file)
            return result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary upload error: {e}")
            return None
    return None

def fetch_all_dict(cursor):
    """Helper to fetch all rows as list of dicts"""
    columns = cursor.column_names
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one_dict(cursor):
    """Helper to fetch one row as dict"""
    row = cursor.fetchone()
    if row is None:
        return None
    columns = cursor.column_names
    return dict(zip(columns, row))



# ----------------------------
# Telangana page Top Section APIs
# ----------------------------
@app.route("/telangana/top-section", methods=["GET"])
def get_top_section():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM top_section")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/telangana/top-section", methods=["POST"])
def add_top_section():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO top_section (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path}
    }), 201


@app.route("/telangana/top-section/<int:news_id>", methods=["PUT"])
def update_top_section(news_id):
    title = request.form.get("title")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM top_section WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_title = title if title else news["title"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]

    cursor.execute("UPDATE top_section SET title=%s, image=%s WHERE id=%s", (new_title, new_image, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "title": new_title, "image": new_image}})


@app.route("/telangana/top-section/<int:news_id>", methods=["DELETE"])
def delete_top_section(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM top_section WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM top_section WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})


# ----------------------------
# Telangana page Bottom Cards APIs (full CRUD)
# ----------------------------
@app.route("/telangana/bottom-cards", methods=["GET"])
def get_bottom_cards():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bottom_cards")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/telangana/bottom-cards", methods=["POST"])
def add_bottom_card():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bottom_cards (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path}
    }), 201


@app.route("/telangana/bottom-cards/<int:card_id>", methods=["PUT"])
def update_bottom_card(card_id):
    title = request.form.get("title")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bottom_cards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]

    cursor.execute("UPDATE bottom_cards SET title=%s, image=%s WHERE id=%s", (new_title, new_image, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image}})


@app.route("/telangana/bottom-cards/<int:card_id>", methods=["DELETE"])
def delete_bottom_card(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bottom_cards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM bottom_cards WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Telangana page Right Cards APIs (full CRUD)
# ----------------------------
@app.route("/telangana/right-cards", methods=["GET"])
def get_right_cards():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM right_cards")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/telangana/right-cards", methods=["POST"])
def add_right_card():
    title = request.form.get("title")
    description = request.form.get("description")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO right_cards (title, description) VALUES (%s, %s)", (title, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "description": description}
    }), 201

@app.route("/telangana/right-cards/<int:card_id>", methods=["PUT"])
def update_right_card(card_id):
    title = request.form.get("title")
    description = request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM right_cards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_description = description if description is not None else card.get("description")

    cursor.execute("UPDATE right_cards SET title=%s, description=%s WHERE id=%s", (new_title, new_description, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "title": new_title,
            "description": new_description
        }
    })


@app.route("/telangana/right-cards/<int:card_id>", methods=["DELETE"])
def delete_right_card(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM right_cards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM right_cards WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
#  Telangana page Hyderabad news APIs (full CRUD)
# ----------------------------
@app.route("/telangana/hyderabad-news", methods=["GET"])
def get_hyderabad_news():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hyderabad_news")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/telangana/hyderabad-news", methods=["POST"])
def add_hyderabad_news():
    title = request.form.get("title")
    description=request.form.get("description")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO hyderabad_news (title, image, description) VALUES (%s, %s, %s)", (title, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path,"description":description}
    }), 201


@app.route("/telangana/hyderabad-news/<int:card_id>", methods=["PUT"])
def update_hyderabad_news(card_id):
    title = request.form.get("title")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hyderabad_news WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")

    cursor.execute("UPDATE hyderabad_news SET title=%s, image=%s, description=%s WHERE id=%s", (new_title, new_image,new_description, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image,"description":new_description}})


@app.route("/telangana/hyderabad-news/<int:card_id>", methods=["DELETE"])
def delete_hyderabad_news(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hyderabad_news WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM hyderabad_news WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Telangana page Warangal news APIs (full CRUD)
# ----------------------------
@app.route("/telangana/warangal-news", methods=["GET"])
def get_warangal_news():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warangal_news")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/telangana/warangal-news", methods=["POST"])
def add_warangal_news():
    title = request.form.get("title")
    description=request.form.get("description")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO warangal_news (title, image, description) VALUES (%s, %s, %s)", (title, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path,"description":description}
    }), 201


@app.route("/telangana/warangal-news/<int:card_id>", methods=["PUT"])
def update_warangal_news(card_id):
    title = request.form.get("title")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warangal_news WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")

    cursor.execute("UPDATE warangal_news SET title=%s, image=%s, description=%s WHERE id=%s", (new_title, new_image,new_description, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image,"description":new_description}})


@app.route("/telangana/warangal-news/<int:card_id>", methods=["DELETE"])
def delete_warangal_news(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warangal_news WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM warangal_news WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Crime daata  APIs (full CRUD)
# ----------------------------
@app.route("/crime/crime-data", methods=["GET"])
def get_crime_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_data")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/crime/crime-data", methods=["POST"])
def add_crime_data():
    content = request.form.get("content")
    description=request.form.get("description")
    image = request.files.get("image")
    if not content:
        return jsonify({"error": "content is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO crime_data (content, image, description) VALUES (%s, %s, %s)", (content, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "content": content, "image": image_path,"description":description}
    }), 201


@app.route("/crime/crime-data/<int:card_id>", methods=["PUT"])
def update_crime_data(card_id):
    content = request.form.get("content")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_data WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_content = content if content else card["content"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")

    cursor.execute("UPDATE crime_data SET content=%s, image=%s, description=%s WHERE id=%s", (new_content, new_image,new_description, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "content": new_content, "image": new_image,"description":new_description}})


@app.route("/crime/crime-data/<int:card_id>", methods=["DELETE"])
def delete_crime_data(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_data WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM crime_data WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Crime page  DataList APIs (full CRUD)
# ----------------------------
@app.route("/crime/data-list", methods=["GET"])
def get_crime_datalist():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_datalist")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/crime/data-list", methods=["POST"])
def add_crime_datalist():
    title = request.form.get("title")
    description = request.form.get("description")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO crime_datalist (title, description) VALUES (%s, %s)", (title, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "description": description}
    }), 201

@app.route("/crime/data-list/<int:card_id>", methods=["PUT"])
def update_crime_datalist(card_id):
    title = request.form.get("title")
    description = request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_datalist WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_description = description if description is not None else card.get("description")

    cursor.execute("UPDATE crime_datalist SET title=%s, description=%s WHERE id=%s", (new_title, new_description, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "title": new_title,
            "description": new_description
        }
    })

@app.route("/crime/data-list/<int:card_id>", methods=["DELETE"])
def delete_crime_datalist(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_datalist WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM crime_datalist WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
# crime page  viral news APIs (full CRUD)
# ----------------------------
@app.route("/crime/viral-news", methods=["GET"])
def get_crime_viralnews():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_viralnews")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/crime/viral-news", methods=["POST"])
def add_crime_viralnews():
    headline= request.form.get("headline")
    alt=request.form.get("alt")
    image = request.files.get("image")
    if not headline:
        return jsonify({"error": "Headline is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO crime_viralnews (headline, alt, image) VALUES (%s, %s, %s)", (headline, alt, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "headline": headline, "alt":alt, "image": image_path}
    }), 201



@app.route("/crime/viral-news/<int:card_id>", methods=["PUT"])
def update_crime_viralnews(card_id):
    headline = request.form.get("headline")
    image = request.files.get("image")
    alt=request.form.get("alt")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT *  FROM crime_viralnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_headline = headline if headline else card["headline"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_alt= alt if alt is not None else card.get("alt")

    cursor.execute("UPDATE crime_viralnews SET headline=%s, image=%s, alt=%s WHERE id=%s", (new_headline, new_image,new_alt, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "headline": new_headline, "image": new_image,"alt":new_alt}})


@app.route("/crime/viral-news/<int:card_id>", methods=["DELETE"])
def delete_crime_viralnews(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_viralnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM crime_viralnews WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
# crime page  latest news APIs (full CRUD)
# ----------------------------



@app.route("/crime/crime-latestnews", methods=["GET"])
def get_crime_latestnews():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_latestnews ORDER BY updated_at DESC")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/crime/crime-latestnews", methods=["POST"])
def add_crime_latestnews():
    description = request.form.get("description")
    if not description:
        return jsonify({"error": "Content is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    updated_at = datetime.now()
    cursor.execute(
        "INSERT INTO crime_latestnews (description, updated_at) VALUES (%s, %s)",
        (description, updated_at)
    )
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Description added successfully!",
        "news": {
            "id": news_id,
            "description": description,
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201


@app.route("/crime/crime-latestnews/<int:card_id>", methods=["PUT"])
def update_crime_latestnews(card_id):
    description = request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_latestnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute(
        "UPDATE crime_latestnews SET description=%s, updated_at=%s WHERE id=%s",
        (new_description, updated_at, card_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "description": new_description,
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    })


@app.route("/crime/latestnews/<int:card_id>", methods=["DELETE"])
def delete_crime_latestnews(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crime_latestnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM crime_latestnews WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Home Page News Data 
# ----------------------------
@app.route("/home/newsdata", methods=["GET"])
def get_home_newsdata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_newsdata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/home/newsdata", methods=["POST"])
def add_home_newsdata():
    heading= request.form.get("heading")
    image = request.files.get("image")
    if not heading:
        return jsonify({"error": "Headline is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO home_newsdata (heading,  image) VALUES (%s, %s)", (heading,image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "heading": heading, "image": image_path}
    }), 201


@app.route("/home/newsdata/<int:card_id>", methods=["PUT"])
def update_home_newsdata(card_id):
    heading = request.form.get("heading")
    image = request.files.get("image")
    

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_newsdata WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_heading= heading if heading else card["heading"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    

    cursor.execute("UPDATE home_newsdata SET heading=%s, image=%s  WHERE id=%s", (new_heading, new_image, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "Heading": new_heading, "image": new_image}})


@app.route("/home/newsdata/<int:card_id>", methods=["DELETE"])
def delete_home_newsdata(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_newsdata WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM home_newsdata WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Home Page youtube Data 
# ----------------------------

@app.route("/home/youtube-data", methods=["GET"])
def get_home_youtubedata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_youtubedata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/home/youtube-data", methods=["POST"])
def add_home_youtubedata():
    video_link = request.form.get("video_link")
    video_heading = request.form.get("video_heading")
    if not video_heading:
        return jsonify({"error": "Heading  is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO home_youtubedata (video_link, video_heading) VALUES (%s, %s)", (video_link, video_heading))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "video_link": video_link, "video_heading": video_heading}
    }), 201

@app.route("/home/youtube-data/<int:card_id>", methods=["PUT"])
def update_home_youtubedata(card_id):
    video_link = request.form.get("video_link")
    video_heading = request.form.get("video_heading")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_youtubedata WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_videolink = video_link if video_link else card["video_link"]
    new_videoheading = video_heading if video_heading is not None else card.get("video_heading")
    updated_at = datetime.now()

    cursor.execute("UPDATE home_youtubedata SET video_link=%s, video_heading=%s,updated_at=%s WHERE id=%s", (new_videolink, new_videoheading,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "video_link": new_videolink,
            "video_heading": new_videoheading,
            "updated_at":updated_at
        }
    })

@app.route("/home/youtube-data/<int:card_id>", methods=["DELETE"])
def delete_home_youtubedata(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_youtubedata WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM home_youtubedata WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
# Home Page Politicalnews APIs (full CRUD)
# ----------------------------
@app.route("/home/political-news-data", methods=["GET"])
def get_home_politicsnewsdata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_politicsnews")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/home/political-news-data", methods=["POST"])
def add_home_politicsnewsdata():
    title = request.form.get("title")
    description=request.form.get("description")
    
    if not title:
        return jsonify({"error": "Title is required"}), 400

    

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO home_politicsnews (title, description) VALUES (%s,  %s)", (title, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "description":description}
    }), 201


@app.route("/home/political-news-data/<int:card_id>", methods=["PUT"])
def update_home_politicsnewsdata(card_id):
    title = request.form.get("title")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_politicsnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute("UPDATE home_politicsnews SET title=%s, description=%s,updated_at=%s WHERE id=%s", (new_title,new_description,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title,"description":new_description,"updated_at":updated_at}})


@app.route("/home/political-news-data/<int:card_id>", methods=["DELETE"])
def delete_home_politicsnewsdata(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_politicsnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM home_politicsnews WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
# Home Page political Data 
# ----------------------------
@app.route("/home/politicaldata", methods=["GET"])
def get_home_politicaldata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_politicaldata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route("/home/politicaldata", methods=["POST"])
def add_home_politicaldata():
    heading= request.form.get("heading")
    image = request.files.get("image")
    if not heading:
        return jsonify({"error": "Headline is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO home_politicaldata (heading,  image) VALUES (%s, %s)", (heading,image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "heading": heading, "image": image_path}
    }), 201


@app.route("/home/politicaldata/<int:card_id>", methods=["PUT"])
def update_home_politicaldata(card_id):
    heading = request.form.get("heading")
    image = request.files.get("image")
    

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_politicaldata WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_heading= heading if heading else card["heading"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE home_politicaldata SET heading=%s, image=%s,updated_at=%s  WHERE id=%s", (new_heading, new_image,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "Heading": new_heading, "image": new_image,"updated_at":updated_at}})


@app.route("/home/politicaldata/<int:card_id>", methods=["DELETE"])
def delete_home_politicaldata(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_politicaldata WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM home_newsdata WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
# Home page Telanganadata APIs
# ----------------------------
@app.route("/home/telanganadata", methods=["GET"])
def get_home_telanganadata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_telanganadata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/home/telanganadata", methods=["POST"])
def add_home_telanganadata():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO home_telanganadata (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path}
    }), 201


@app.route("/home/telanganadata/<int:news_id>", methods=["PUT"])
def update_home_telanganadata(news_id):
    title = request.form.get("title")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_telanganadata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_title = title if title else news["title"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE home_telanganadata SET title=%s, image=%s, updated_at=%s WHERE id=%s", (new_title, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "title": new_title, "image": new_image, "updated_at":updated_at}})


@app.route("/home/telanganadata/<int:news_id>", methods=["DELETE"])
def delete_home_telanganadata(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM home_telanganadata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM home_telanganadata WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})



# ----------------------------
# Health page  Healthdata APIs
# ----------------------------


@app.route("/health/healthdata", methods=["GET"])
def get_health_healthdata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM healthdata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/health/healthdata", methods=["POST"])
def add_health_healthdata():
    text = request.form.get("text")
    image = request.files.get("image")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO healthdata (text, image) VALUES (%s, %s)", (text, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "text": text, "image": image_path}
    }), 201


@app.route("/health/healthdata/<int:news_id>", methods=["PUT"])
def update_health_healthdata(news_id):
    text = request.form.get("text")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM healthdata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_text = text if text else news["text"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE healthdata SET text=%s, image=%s, updated_at=%s WHERE id=%s", (new_text, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "text": new_text, "image": new_image, "updated_at":updated_at}})


@app.route("/health/healthdata/<int:news_id>", methods=["DELETE"])
def delete_health_healthdata(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM healthdata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM healthdata WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})



# ----------------------------
# Health page  Heorineimages APIs
# ----------------------------

@app.route("/health/Heorineimages", methods=["GET"])
def get_health_Heorineimages():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Heorineimages")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/health/Heorineimages", methods=["POST"])
def add_health_Heorineimages():
    text = request.form.get("text")
    image = request.files.get("image")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Heorineimages (text, image) VALUES (%s, %s)", (text, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "text": text, "image": image_path}
    }), 201


@app.route("/health/Heorineimages/<int:news_id>", methods=["PUT"])
def update_health_Heorineimages(news_id):
    text = request.form.get("text")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Heorineimages WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_text = text if text else news["text"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE Heorineimages SET text=%s, image=%s, updated_at=%s WHERE id=%s", (new_text, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "text": new_text, "image": new_image, "updated_at":updated_at}})


@app.route("/health/Heorineimages/<int:news_id>", methods=["DELETE"])
def delete_health_Heorineimages(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Heorineimages WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM Heorineimages WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})




# ----------------------------
# Health page  lifestyle data APIs
# ----------------------------

@app.route("/health/lifestyle-data", methods=["GET"])
def get_health_lifestyledata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_lifestyledata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/health/lifestyle-data", methods=["POST"])
def add_health_lifestyledata():
    text = request.form.get("text")
    image = request.files.get("image")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO health_lifestyledata (text, image) VALUES (%s, %s)", (text, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "text": text, "image": image_path}
    }), 201


@app.route("/health/lifestyle-data/<int:news_id>", methods=["PUT"])
def update_health_lifestyledata(news_id):
    text = request.form.get("text")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_lifestyledata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_text = text if text else news["text"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE health_lifestyledata SET text=%s, image=%s, updated_at=%s WHERE id=%s", (new_text, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "text": new_text, "image": new_image, "updated_at":updated_at}})


@app.route("/health/lifestyle-data/<int:news_id>", methods=["DELETE"])
def delete_health_lifestyledata(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_lifestyledata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM health_lifestyledata WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})




# ----------------------------
# Health  latest news headlines APIs (full CRUD)
# ----------------------------



@app.route("/health/health-latestnewsheadlines", methods=["GET"])
def get_health_latestnewsheadlines():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_latestnewsheadlines ORDER BY updated_at DESC")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/health/health-latestnewsheadlines", methods=["POST"])
def add_health_latestnewsheadlines():
    headline = request.form.get("headline")
    if not headline:
        return jsonify({"error": "Content is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    updated_at = datetime.now()
    cursor.execute(
        "INSERT INTO health_latestnewsheadlines (headline, updated_at) VALUES (%s, %s)",
        (headline, updated_at)
    )
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "headline added successfully!",
        "news": {
            "id": news_id,
            "headline": headline,
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201


@app.route("/health/health-latestnewsheadlines/<int:card_id>", methods=["PUT"])
def update_health_latestnewsheadlines(card_id):
    headline = request.form.get("headline")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_latestnewsheadlines WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_headline = headline if headline is not None else card.get("headline")
    updated_at = datetime.now()

    cursor.execute(
        "UPDATE health_latestnewsheadlines SET headline=%s, updated_at=%s WHERE id=%s",
        (new_headline, updated_at, card_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "description": new_headline,
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    })


@app.route("/health/health-latestnewsheadlines/<int:card_id>", methods=["DELETE"])
def delete_health_latestnewsheadlines(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_latestnewsheadlines WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM health_latestnewsheadlines WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# ----------------------------
# National page Top Section APIs
# ----------------------------
@app.route("/National/top-section", methods=["GET"])
def get_national_topsection():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM National_topsection")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/National/top-section", methods=["POST"])
def add_national_topsection():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO National_topsection (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path}
    }), 201


@app.route("/National/top-section/<int:news_id>", methods=["PUT"])
def update_national_topsection(news_id):
    title = request.form.get("title")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM National_topsection WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_title = title if title else news["title"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()


    cursor.execute("UPDATE National_topsection SET title=%s, image=%s, updated_at=%s WHERE id=%s", (new_title, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "title": new_title, "image": new_image,"updated_at": updated_at}})


@app.route("/National/top-section/<int:news_id>", methods=["DELETE"])
def delete_national_topsection(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM National_topsection WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM National_topsection WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})


# ----------------------------
# National page Bottom Cards APIs (full CRUD)
# ----------------------------
@app.route("/National/bottom-cards", methods=["GET"])
def get_national_bottomcards():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_bottomcards")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/National/bottom-cards", methods=["POST"])
def add_national_bottomcardsd():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO national_bottomcards (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path}
    }), 201


@app.route("/National/bottom-cards/<int:card_id>", methods=["PUT"])
def update_national_bottomcards(card_id):
    title = request.form.get("title")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_bottomcards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE national_bottomcards SET title=%s, image=%s, updated_at=%s WHERE id=%s", (new_title, new_image,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image, "updated_at":updated_at}})


@app.route("/National/bottom-cards/<int:card_id>", methods=["DELETE"])
def delete_national_bottomcards(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_bottomcards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM national_bottomcards WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# National  page Right Cards APIs (full CRUD)
# ----------------------------
@app.route("/National/right-cards", methods=["GET"])
def get_national_rightcards():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_rightcards")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/National/right-cards", methods=["POST"])
def add_national_rightcards():
    title = request.form.get("title")
    description = request.form.get("description")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO national_rightcards (title, description) VALUES (%s, %s)", (title, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "description": description}
    }), 201

@app.route("/National/right-cards/<int:card_id>", methods=["PUT"])
def update_national_rightcards(card_id):
    title = request.form.get("title")
    description = request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_rightcards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute("UPDATE national_rightcards SET title=%s, description=%s, updated_at=%s WHERE id=%s", (new_title, new_description,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "title": new_title,
            "description": new_description,
            "updated_at":updated_at
        }
    })


@app.route("/National/right-cards/<int:card_id>", methods=["DELETE"])
def delete_national_rightcards(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_rightcards WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM national_rightcards WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})



# # ----------------------------
# #  National page Hyderabad news APIs (full CRUD)
# # ----------------------------
@app.route("/National/hyderabad-news", methods=["GET"])
def get_national_hyderabadnews():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_hyderabadnews")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/National/hyderabad-news", methods=["POST"])
def add_national_hyderabadnews():
    title = request.form.get("title")
    description=request.form.get("description")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO national_hyderabadnews (title, image, description) VALUES (%s, %s, %s)", (title, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path,"description":description}
    }), 201


@app.route("/National/hyderabad-news/<int:card_id>", methods=["PUT"])
def update_national_hyderabadnews(card_id):
    title = request.form.get("title")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_hyderabadnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute("UPDATE national_hyderabadnews SET title=%s, image=%s, description=%s,updated_at=%s WHERE id=%s", (new_title, new_image,new_description,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image,"description":new_description,"updated_at":updated_at}})


@app.route("/National/hyderabad-news/<int:card_id>", methods=["DELETE"])
def delete_national_hyderabadnews(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_hyderabadnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM national_hyderabadnews WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# National page Warangal news APIs (full CRUD)
# ----------------------------
@app.route("/National/warangal-news", methods=["GET"])
def get_national_warangalnews():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_warangalnews")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/National/warangal-news", methods=["POST"])
def add_national_warangalnews():
    title = request.form.get("title")
    description=request.form.get("description")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO national_warangalnews (title, image, description) VALUES (%s, %s, %s)", (title, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path,"description":description}
    }), 201


@app.route("/National/warangal-news/<int:card_id>", methods=["PUT"])
def update_national_warangalnews(card_id):
    title = request.form.get("title")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM warangal_news WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute("UPDATE national_warangalnews SET title=%s, image=%s, description=%s,updated_at=%s WHERE id=%s", (new_title, new_image,new_description,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image,"description":new_description,"updated_at":updated_at}})


@app.route("/National/warangal-news/<int:card_id>", methods=["DELETE"])
def delete_national_warangalnews(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM national_warangalnews WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM national_warangalnews WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})




# ----------------------------
# lifestyle page  Healthdata APIs
# ----------------------------


@app.route("/lifestyle/healthdata", methods=["GET"])
def get_lifestyle_healthdata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_healthdata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/lifestyle/healthdata", methods=["POST"])
def add_lifestyle_healthdata():
    text = request.form.get("text")
    image = request.files.get("image")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lifestyle_healthdata (text, image) VALUES (%s, %s)", (text, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "text": text, "image": image_path}
    }), 201


@app.route("/lifestyle/healthdata/<int:news_id>", methods=["PUT"])
def update_lifestyle_healthdata(news_id):
    text = request.form.get("text")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_healthdata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_text = text if text else news["text"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE lifestyle_healthdata SET text=%s, image=%s, updated_at=%s WHERE id=%s", (new_text, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "text": new_text, "image": new_image, "updated_at":updated_at}})


@app.route("/lifestyle/healthdata/<int:news_id>", methods=["DELETE"])
def delete_lifestyle_healthdata(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_healthdata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM lifestyle_healthdata WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})



# ----------------------------
# lifestyle  page  Heorineimages APIs
# ----------------------------

@app.route("/lifestyle/Heorineimages", methods=["GET"])
def get_lifestyle_Heorineimages():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_Heorineimages")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/lifestyle/Heorineimages", methods=["POST"])
def add_lifestyle_Heorineimages():
    text = request.form.get("text")
    image = request.files.get("image")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lifestyle_Heorineimages (text, image) VALUES (%s, %s)", (text, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "text": text, "image": image_path}
    }), 201


@app.route("/lifestyle/Heorineimages/<int:news_id>", methods=["PUT"])
def update_lifestyle_Heorineimages(news_id):
    text = request.form.get("text")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_Heorineimages WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_text = text if text else news["text"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE lifestyle_Heorineimages SET text=%s, image=%s, updated_at=%s WHERE id=%s", (new_text, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "text": new_text, "image": new_image, "updated_at":updated_at}})


@app.route("/health/Heorineimages/<int:news_id>", methods=["DELETE"])
def delete_lifestyle_Heorineimages(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_Heorineimages WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM lifestyle_Heorineimages WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})




# # ----------------------------
# # lifestyle page  lifestyle data APIs
# # ----------------------------

@app.route("/lifestyle/lifestyle-data", methods=["GET"])
def get_lifestyle_lifestyledata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_lifestyledata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/lifestyle/lifestyle-data", methods=["POST"])
def add_lifestyle_lifestyledata():
    text = request.form.get("text")
    image = request.files.get("image")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lifestyle_lifestyledata (text, image) VALUES (%s, %s)", (text, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "text": text, "image": image_path}
    }), 201


@app.route("/lifestyle/lifestyle-data/<int:news_id>", methods=["PUT"])
def update_lifestyle_lifestyledata(news_id):
    text = request.form.get("text")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_lifestyledata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_text = text if text else news["text"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE lifestyle_lifestyledata SET text=%s, image=%s, updated_at=%s WHERE id=%s", (new_text, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "text": new_text, "image": new_image, "updated_at":updated_at}})


@app.route("/lifestyle/lifestyle-data/<int:news_id>", methods=["DELETE"])
def delete_lifestyle_lifestyledata(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_lifestyledata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM lifestyle_lifestyledata WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})




# # ----------------------------
# # lifestyle page  latest news headlines APIs (full CRUD)
# # ----------------------------



@app.route("/lifestyle/health-latestnewsheadlines", methods=["GET"])
def get_lifestyle_latestnewsheadlines():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_latestnewsheadlines ORDER BY updated_at DESC")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/lifestyle/health-latestnewsheadlines", methods=["POST"])
def add_lifestyle_latestnewsheadlines():
    headline = request.form.get("headline")
    if not headline:
        return jsonify({"error": "Content is required"}), 400
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    updated_at = datetime.now()
    cursor.execute(
        "INSERT INTO lifestyle_latestnewsheadlines (headline, updated_at) VALUES (%s, %s)",
        (headline, updated_at)
    )
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "headline added successfully!",
        "news": {
            "id": news_id,
            "headline": headline,
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201


@app.route("/lifestyle/health-latestnewsheadlines/<int:card_id>", methods=["PUT"])
def update_lifestyle_latestnewsheadlines(card_id):
    headline = request.form.get("headline")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_latestnewsheadlines WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_headline = headline if headline is not None else card.get("headline")
    updated_at = datetime.now()

    cursor.execute(
        "UPDATE lifestyle_latestnewsheadlines SET headline=%s, updated_at=%s WHERE id=%s",
        (new_headline, updated_at, card_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Card updated successfully!",
        "card": {
            "id": card_id,
            "description": new_headline,
            "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    })


@app.route("/lifestyle/health-latestnewsheadlines/<int:card_id>", methods=["DELETE"])
def delete_lifestyle_latestnewsheadlines(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lifestyle_latestnewsheadlines WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM lifestyle_latestnewsheadlines WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})





# # ----------------------------
# # sports page Herosection-cardsdata APIs (full CRUD)
# # ----------------------------

@app.route("/sports/Herosection-cardsdata", methods=["GET"])
def get_sports_Herosection_cardsdata():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_Herosection_cardsdata")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
   
    return jsonify(rows)


@app.route("/sports/Herosection-cardsdata", methods=["POST"])
def add_sports_Herosection_cardsdata():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image) if image else None

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sports_Herosection_cardsdata (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path}
    }), 201


@app.route("/sports/Herosection-cardsdata/<int:news_id>", methods=["PUT"])
def update_sports_Herosection_cardsdata(news_id):
    title = request.form.get("title")
    image = request.files.get("image")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_Herosection_cardsdata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    new_title = title if title else news["title"]
    new_image = upload_image_to_cloudinary(image) if image else news["image"]
    updated_at = datetime.now()

    cursor.execute("UPDATE sports_Herosection_cardsdata SET title=%s, image=%s, updated_at=%s WHERE id=%s", (new_title, new_image,updated_at, news_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News updated successfully!", "news": {"id": news_id, "title": new_title, "image": new_image, "updated_at":updated_at}})


@app.route("/sports/Herosection-cardsdata/<int:news_id>", methods=["DELETE"])
def delete_sports_Herosection_cardsdata(news_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_Herosection_cardsdata WHERE id=%s", (news_id,))
    news = fetch_one_dict(cursor)
    if not news:
        cursor.close()
        conn.close()
        return jsonify({"error": "News not found"}), 404

    cursor.execute("DELETE FROM sports_Herosection_cardsdata WHERE id=%s", (news_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "News deleted successfully!", "news": news})


# ----------------------------
# Sports page bottomCardsData APIs (full CRUD)
# ----------------------------
@app.route("/sports/bottomCardsData", methods=["GET"])
def get_sports_bottomCardsData():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_bottomCardsData")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/sports/bottomCardsData", methods=["POST"])
def add_sports_bottomCardsData():
    title = request.form.get("title")
    description=request.form.get("description")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sports_bottomCardsData (title, image, description) VALUES (%s, %s, %s)", (title, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path,"description":description}
    }), 201


@app.route("/sports/bottomCardsData/<int:card_id>", methods=["PUT"])
def update_sports_bottomCardsData(card_id):
    title = request.form.get("title")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_bottomCardsData WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute("UPDATE sports_bottomCardsData SET title=%s, image=%s, description=%s,updated_at=%s WHERE id=%s", (new_title, new_image,new_description,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image,"description":new_description,"updated_at":updated_at}})


@app.route("/sports/bottomCardsData/<int:card_id>", methods=["DELETE"])
def delete_sports_bottomCardsData(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_bottomCardsData WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM sports_bottomCardsData WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})


# ----------------------------
# Sports page cricket trending_updates Data APIs (full CRUD)
# ----------------------------

@app.route("/sports/cricket-trending-updates", methods=["GET"])
def get_sports_cricket_trending_updates():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_bottomCardsData")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/sports/cricket-trending-updates", methods=["POST"])
def add_sports_bottomCardsData():
    title = request.form.get("title")
    description=request.form.get("description")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400

    image_path = upload_image_to_cloudinary(image)

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sports_bottomCardsData (title, image, description) VALUES (%s, %s, %s)", (title, image_path, description))
    conn.commit()
    news_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message": "News added successfully!",
        "news": {"id": news_id, "title": title, "image": image_path,"description":description}
    }), 201


@app.route("/sports/cricket-trending-updates/<int:card_id>", methods=["PUT"])
def update_sports_bottomCardsData(card_id):
    title = request.form.get("title")
    image = request.files.get("image")
    description=request.form.get("description")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_bottomCardsData WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    new_title = title if title else card["title"]
    new_image = upload_image_to_cloudinary(image) if image else card["image"]
    new_description = description if description is not None else card.get("description")
    updated_at = datetime.now()

    cursor.execute("UPDATE sports_bottomCardsData SET title=%s, image=%s, description=%s,updated_at=%s WHERE id=%s", (new_title, new_image,new_description,updated_at, card_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card updated successfully!", "card": {"id": card_id, "title": new_title, "image": new_image,"description":new_description,"updated_at":updated_at}})


@app.route("/sports/cricket-trending-updates/<int:card_id>", methods=["DELETE"])
def delete_sports_bottomCardsData(card_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sports_bottomCardsData WHERE id=%s", (card_id,))
    card = fetch_one_dict(cursor)
    if not card:
        cursor.close()
        conn.close()
        return jsonify({"error": "Card not found"}), 404

    cursor.execute("DELETE FROM sports_bottomCardsData WHERE id=%s", (card_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Card deleted successfully!", "card": card})






































































































































# ----------------------------------
# Business Left Data APIs (full CRUD)
# ----------------------------------
@app.route("/business/left-data", methods=["GET"])
def get_business_left_data():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM business_left_data")
    rows = fetch_all_dict(cursor)
    cursor.close()
    conn.close()
    return jsonify(rows)
 
 
@app.route("/business/left-data", methods=["POST"])
def add_business_left_data():
    title = request.form.get("title")
    image = request.files.get("image")
    if not title:
        return jsonify({"error": "Title is required"}), 400
 
    image_path = upload_image_to_cloudinary(image)
 
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("INSERT INTO business_left_data (title, image) VALUES (%s, %s)", (title, image_path))
    conn.commit()
    left_id = cursor.lastrowid 
 
    cursor.close()
    conn.close()
 
    return jsonify({
        "message": "Business Left Data added successfully!",
        "business_left": {"id": left_id, "title": title, "image": image_path}
    }), 201
 
 
 
@app.route("/business/left-data/<int:left_id>", methods=["PUT"])
def update_business_left_data(left_id):
    title = request.form.get("title")
    image = request.files.get("image")
 
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM business_left_data WHERE id=%s", (left_id,))
    left_data = fetch_one_dict(cursor)
    if not left_data:
        cursor.close()
        conn.close()
        return jsonify({"error": "Business Left Data not found"}), 404
 
    new_title = title if title else left_data["title"]
    new_image = upload_image_to_cloudinary(image) if image else left_data["image"]
 
    cursor.execute("UPDATE business_left_data SET title=%s, image=%s WHERE id=%s", (new_title, new_image, left_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({
        "message": "Business Left Data updated successfully!",
        "business_left": {"id": left_id, "title": new_title, "image": new_image}
    })
 
 
@app.route("/business/left-data/<int:left_id>", methods=["DELETE"])
def delete_business_left_data(left_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM business_left_data WHERE id=%s", (left_id,))
    left_data = fetch_one_dict(cursor)
    if not left_data:
        cursor.close()
        conn.close()
        return jsonify({"error": "Business Left Data not found"}), 404
 
    cursor.execute("DELETE FROM business_left_data WHERE id=%s", (left_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Business Left Data deleted successfully!", "business_left": left_data})
 




















































































# ----------------------------
# Run Flask
# ----------------------------
if __name__ == "__main__":
    # Connect to MySQL server and create DB/tables if not exists
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error creating database: {e}")

    # Now connect to DB and create tables if not exist
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS top_section (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bottom_cards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS right_cards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hyderabad_news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                image VARCHAR(255),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP      
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warangal_news (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                image VARCHAR(255),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP      
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crime_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content TEXT NOT NULL,
                description TEXT,
                image VARCHAR(255),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP      
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crime_datalist (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crime_viralnews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                headline TEXT NOT NULL,
                alt TEXT NOT NULL,     
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crime_latestnews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                description TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP                    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS home_newsdata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                heading TEXT NOT NULL,    
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP   
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS home_youtubedata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                video_link VARCHAR(255) NOT NULL,    
                video_heading VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS home_politicsnews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP     
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS home_politicaldata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                heading TEXT NOT NULL,    
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP   
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS home_telanganadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS healthdata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Heorineimages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_lifestyledata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_latestnewsheadlines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                headline TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP                    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS National_topsection (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS national_bottomcards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS national_rightcards (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS national_hyderabadnews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP     
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS national_warangalnews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP      
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lifestyle_healthdata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lifestyle_Heorineimages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lifestyle_lifestyledata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                text TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lifestyle_latestnewsheadlines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                headline TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP                    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sports_Herosection_cardsdata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sports_bottomCardsData (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                image VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP    
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_left_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                image VARCHAR(255),
                       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Connected to MySQL DB: {DB_NAME} with USER={DB_USER}, HOST={DB_HOST}")
    else:
        print("❌ Failed to connect to MySQL DB")

    app.run(debug=True)
