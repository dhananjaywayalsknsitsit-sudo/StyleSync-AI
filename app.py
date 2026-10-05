import os
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from config import Config
from services.images import save_upload, delete_file
from services.fashn import create_tryon
from services.recommender import recommend

load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)

client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=5000)
db = client[app.config["MONGO_DB"]]
users = db.users
tryons = db.tryons
favorites = db.favorites

def current_user():
    uid = session.get("user_id")
    return users.find_one({"_id": ObjectId(uid)}) if uid else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_user():
    return {"logged_user": current_user()}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter all details. Password must be at least 8 characters.", "danger")
            return render_template("register.html")
        if users.find_one({"email": email}):
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))
        role = "admin" if email == app.config["ADMIN_EMAIL"] and app.config["ADMIN_EMAIL"] else "user"
        result = users.insert_one({
            "name": name, "email": email,
            "password": generate_password_hash(password),
            "role": role, "style": "casual", "created_at": datetime.now(timezone.utc)
        })
        session["user_id"] = str(result.inserted_id)
        flash("Account created successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = users.find_one({"email": email})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        session.clear()
        session["user_id"] = str(user["_id"])
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    recent = list(tryons.find({"user_id": str(user["_id"])}).sort("created_at", DESCENDING).limit(4))
    return render_template("dashboard.html", recent=recent)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        style = request.form.get("style", "casual")
        if name:
            users.update_one({"_id": user["_id"]}, {"$set": {"name": name, "style": style}})
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))
    return render_template("profile.html", user=user)

@app.route("/try-on", methods=["GET", "POST"])
@login_required
def try_on():
    if request.method == "POST":
        person_file = request.files.get("person_image")
        garment_file = request.files.get("garment_image")
        category = request.form.get("category", "tops")
        prompt = request.form.get("prompt", "").strip()[:300]
        if not person_file or not garment_file:
            flash("Upload both your photo and clothing photo.", "danger")
            return redirect(url_for("try_on"))
        try:
            person_path = save_upload(person_file, app.config)
            garment_path = save_upload(garment_file, app.config)
            result_url = create_tryon(person_path, garment_path, prompt, app.config)
            doc = {
                "user_id": session["user_id"],
                "person_image": "/" + person_path.replace("\\", "/"),
                "garment_image": "/" + garment_path.replace("\\", "/"),
                "result_url": result_url,
                "category": category, "prompt": prompt,
                "created_at": datetime.now(timezone.utc)
            }
            saved = tryons.insert_one(doc)
            flash("Your virtual try-on is ready!", "success")
            return redirect(url_for("result", item_id=str(saved.inserted_id)))
        except Exception as exc:
            app.logger.exception("Try-on failed")
            flash(str(exc), "danger")
            return redirect(url_for("try_on"))
    return render_template("try_on.html")

@app.route("/result/<item_id>")
@login_required
def result(item_id):
    item = tryons.find_one({"_id": ObjectId(item_id), "user_id": session["user_id"]})
    if not item:
        flash("Result not found.", "warning")
        return redirect(url_for("history"))
    return render_template("result.html", item=item)

@app.route("/history")
@login_required
def history():
    items = list(tryons.find({"user_id": session["user_id"]}).sort("created_at", DESCENDING))
    return render_template("history.html", items=items)

@app.route("/recommendations")
@login_required
def recommendations():
    user = current_user()
    style = user.get("style", "casual")
    return render_template("recommendations.html", outfits=recommend(style), style=style)

@app.route("/favorite/<item_id>", methods=["POST"])
@login_required
def favorite(item_id):
    item = tryons.find_one({"_id": ObjectId(item_id), "user_id": session["user_id"]})
    if not item:
        flash("Try-on result not found.", "warning")
    else:
        favorites.update_one({"user_id": session["user_id"], "tryon_id": item_id},
                             {"$set": {"result_url": item["result_url"], "created_at": datetime.now(timezone.utc)}}, upsert=True)
        flash("Added to favourites.", "success")
    return redirect(request.referrer or url_for("history"))

@app.route("/favorites")
@login_required
def favorites_page():
    items = list(favorites.find({"user_id": session["user_id"]}).sort("created_at", DESCENDING))
    return render_template("favorites.html", items=items)

@app.route("/admin")
@login_required
@admin_required
def admin():
    return render_template("admin.html", user_count=users.count_documents({}),
                           tryon_count=tryons.count_documents({}),
                           latest=list(tryons.find().sort("created_at", DESCENDING).limit(10)))

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(_):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], host="127.0.0.1", port=5000)
