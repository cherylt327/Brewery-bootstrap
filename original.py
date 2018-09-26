from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import string


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://brew:test1234@localhost:3306/brewery_inv'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'jskdfjlsdkfj123'


class Recipe_ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))
    grams = db.Column(db.Integer) 
    ounces = db.Column(db.Integer)

    def __init__(self, recipe_id, ingredient_id, grams, ounces):
        self.recipe_id = recipe_id
        self.ingredient_id = ingredient_id
        self.grams = grams
        self.ounces = ounces


class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    recipe_ingredients = db.relationship('Recipe_ingredients', backref='recipe_ingredients')

    def __init__(self, name):
        self.name = name

class Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    ingredients = db.relationship('Inventory', backref='ingredients')
    ri = db.relationship('Recipe_ingredients', backref='ri')

    def __init__(self, name):
        self.name = name        


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))
    grams = db.Column(db.Integer) 
    ounces = db.Column(db.Integer)

    def __init__(self, ingredient_id, grams, ounces):
        self.ingredient_id = ingredient_id
        self.grams = grams
        self.ounces = ounces



#Main page, displays invetory and links to recipes
@app.route('/', methods=['POST', 'GET'])
def main_display():
    inventory = Inventory.query.all()
    recipes = Recipes.query.all()
    return render_template('index.html',title="Inventory", inventory=inventory, recipes=recipes)




#recipe page... display ingredients and needed items based on missing inventory
@app.route('/recipe', methods=['GET'])
def recipe():
    recipe_id= request.args.get('id')
    recipe = Recipe_ingredients.query.filter_by(recipe_id=recipe_id).all()
    inventory = Inventory.query.all()
        
    return render_template('recipe.html', recipe=recipe, inventory=inventory)


@app.route('/reconcile', methods=['POST', 'GET'])
def reconcile():
    if request.method == 'POST':
        ounces = int(request.form['Ounces'])
        lbs = int(request.form['Lbs'])
        grams = int(request.form['Grams'])
        id = request.form['ID']

        if ounces == '' and lbs == '' and grams == '':
            inventory = Inventory.query.all()
            return render_template('reconcile.html', title="Reconcile", inventory=inventory) 
        else:
            converted_ounces = (lbs * 16) + ounces
            inventory = Inventory.query.filter_by(id=id).first()
            inventory.grams = grams
            inventory.ounces = converted_ounces
            db.session.commit()
            inventory = Inventory.query.all()
            return render_template('reconcile.html', title="Reconcile", inventory=inventory)  
    
    else:
        inventory = Inventory.query.all()
        return render_template('reconcile.html', title="Reconcile", inventory=inventory)   





@app.route('/addinv', methods=['POST', 'GET'])
def add_inventory():
    if request.method == 'POST':
        ounces = int(request.form['Ounces'])
        lbs = int(request.form['Lbs'])
        grams = int(request.form['Grams'])
        id = request.form['ID']
        inventory = Inventory.query.filter_by(id=id).first()

        new_ounces = inventory.ounces + (lbs * 16) + ounces
        new_grams = inventory.grams + grams

        inventory.grams = new_grams
        inventory.ounces = new_ounces
        db.session.commit()
        inventory = Inventory.query.all()  
        return render_template('add_inventory.html', title="Add Inventory", inventory=inventory)  
    
    else:
        inventory = Inventory.query.all()
        return render_template('add_inventory.html', title="Add Inventory", inventory=inventory)          
    

if __name__ == '__main__':
    app.run()
