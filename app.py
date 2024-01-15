import math
import os
from flask import Flask, render_template, request, redirect, url_for,flash
import requests
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "personal"

# Provide the parameters
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_PASSWORD"] = os.environ.get("PYTHON_EMAIL_PASSWORD")
app.config["MAIL_USERNAME"] = os.environ.get("PYTHON_EMAIL")
# Initialize the Flask Mail
mail = Mail(app)
mail.init_app(app)
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        category_name = request.form.get("category")
        if category_name:
            return redirect(url_for("category", name=category_name))
        
    name_list = ["paneer", "pasta", "chilli", "bean"]
    item_data = []
    for i in name_list:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={i}"
        response = requests.get(url)
        data = response.json()["meals"][0]
        name = data['strMeal']
        category = data["strCategory"]
        image = data["strMealThumb"]
        item_data.append({"name":name, "category":category, "image":image})
    return render_template("index.html", item_data=item_data,)

@app.route("/contact",methods=["GET", "POST"] )
def contact():
    if request.method == "POST":
        # Get the form data
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        # Send an email to the user
        msg = Message(
            subject="New Message from Recipa",
            sender=email,
            recipients=[os.environ.get("PYTHON_EMAIL")],
            body=f"Message from Recipa\n From: {name}\nEmail: {email} Message: {message}",
        )
        try:
            mail.send(msg)
            flash("Message Sent..!", "success")
        except Exception as e:
            flash(f"Something Error..! {e}", "error")
        return redirect(url_for("contact"))
    return render_template("contact_us.html")

@app.route("/recipe", methods=["GET", "POST"])
def recipe():
    if request.method == "POST":
        food_name = request.form.get("food_name")
        return redirect(url_for("search_food", food_name=food_name))

    item_data = []
    for i in range(0, 6):
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        response = requests.get(url)
        data = response.json()["meals"][0]
        name = data['strMeal']
        category = data["strCategory"]
        image = data["strMealThumb"]
        tags = data["strTags"]
        item_data.append({"name": name, "category": category, "image": image, "tags": tags})
        
    def featured_dish():
        featured_item = []
        url = "https://www.themealdb.com/api/json/v1/1/search.php?s=lime"
        response = requests.get(url)
        data = response.json()["meals"][0]
        name = data['strMeal']
        category = data["strCategory"]
        image = data["strMealThumb"]
        tags = data["strTags"]
        featured_item.append({"name": name, "category": category, "image": image, "tags": tags})
        return featured_item
    
    featured_dish = featured_dish()
    return render_template("recipes.html", item_data=item_data, featured_dish=featured_dish, food_name=None)


@app.route("/recipe/<string:food_name>", methods=["GET", "POST"])
def search_food(food_name):
    items = []
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={food_name}"
    response = requests.get(url)
    
    # Check if the response contains meals
    if "meals" in response.json():
        meals = response.json()["meals"]
        for meal in meals:
            name = meal['strMeal']
            category = meal["strCategory"]
            image = meal["strMealThumb"]
            tags = meal["strTags"]
            items.append({"name": name, "category": category, "image": image, "tags": tags})
    
    return render_template("recipeonsearch.html", items=items)


@app.route("/recipe/<string:food_name>/detail")
def recipe_detail(food_name):
    details = []
    ingredients = []
    measures = []
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={food_name}"
    # Fetch detailed information about the recipe using the food_name parameter
    # You can use the same API or other data sources to get additional details
    response = requests.get(url)
    data = response.json()["meals"][0]
    name = data['strMeal']
    category = data["strCategory"]
    image = data["strMealThumb"]
    Tags = data["strTags"]
    instructions = data["strInstructions"]
    source = data["strYoutube"]
    details.append({"name":name, "category":category, "image":image, "tags":Tags, "ins":instructions,"Youtube":source})
    # For demonstration purposes, let's create a dummy detail dictionary
    for i in range(1,21):
        ingredient = f"strIngredient{i}"
        if ingredient in data:
            if data[ingredient] != '': 
                ingredients.append(data[ingredient])
        measure = f"strMeasure{i}"
        if measure in data:
            if data[measure] != '': 
                measures.append(data[measure])

    return render_template("recipe_detail.html", detail=details, ingredient = ingredients, measures = measures)


@app.route("/category/<string:name>", methods=["POST", "GET"])
def category(name):
    items = []
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?c={name}"
    response = requests.get(url)
    meals = response.json()["meals"]
    for meal in meals:
        items.append({"name":meal["strMeal"], "image":meal["strMealThumb"], })
    print(items)
    return render_template('category_detail.html', items = items)
    
if __name__ == '__main__':
    app.run(debug=True)
