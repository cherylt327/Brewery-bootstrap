from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import string


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://brew:Bauser76!@localhost:3306/brewery_inv'
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
@app.route('/recipe', methods=['GET', 'POST'])
def recipe():
    recipe_id= request.args.get('id')
    recipe = Recipe_ingredients.query.filter_by(recipe_id=recipe_id).all()
    
    if request.method == 'POST':
        
        for row in recipe:
            ingredient_id = row.ingredient_id
            inventory = Inventory.query.filter_by(ingredient_id=ingredient_id).first()
            inventory.grams = inventory.grams - row.grams
            inventory.ounces = inventory.ounces - row.ounces
            db.session.commit()
        return redirect('/recipe?id='+(recipe_id))
            
        
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

        ounces = request.form.getlist('Ounces')
        lbs = request.form.getlist('Lbs')
        grams = request.form.getlist('Grams')
        id_list = request.form.getlist('ID')
        
        for id in id_list:
            inventory = Inventory.query.filter_by(id=id).first()
            index = id_list.index(id)
            g = int(grams[index])
            p = int(lbs[index])
            o = int(ounces[index])
            new_ounces = inventory.ounces + (p * 16) + o
            new_grams = inventory.grams + g
        
            inventory.grams = new_grams
            inventory.ounces = new_ounces
            db.session.commit()
        inventory = Inventory.query.all()  
        recipes = Recipes.query.all()
        return render_template('index.html',title="Inventory", inventory=inventory, recipes=recipes)
    
    
    else:
        inventory = Inventory.query.all()
        return render_template('add_inv.html', title="Add Inventory", inventory=inventory)          
    

if __name__ == '__main__':
    app.run()
