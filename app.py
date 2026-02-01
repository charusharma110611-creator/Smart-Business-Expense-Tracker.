from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "super_secret_key"

# -- DATABASE CONFIG --
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydata.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# -- MODELS (TABLES) --
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    amount = db.Column(db.Integer)

# -- CREATE DB --
with app.app_context():
    db.create_all()

# -- DASHBOARD --
@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        total_income = int(request.form.get("total_income", 0))
        session["total_income"] = total_income

    total_income = session.get("total_income", 0)

    total_products = Inventory.query.count()
    expenses = Expense.query.all()
    total_expenses = sum(exp.amount for exp in expenses)

    remaining_money = total_income - total_expenses

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_expenses=total_expenses,
        remaining_money=remaining_money,
        total_income=total_income
    )

# -- INVENTORY --
@app.route("/inventory", methods=["GET", "POST"])
def inventory_page():
    if request.method == "POST":
        name = request.form["name"]
        price = int(request.form["price"])
        quantity = int(request.form["quantity"])

        new_item = Inventory(name=name, price=price, quantity=quantity)
        db.session.add(new_item)
        db.session.commit()

    inventory = Inventory.query.all()

    low_stock_items = [item for item in inventory if item.quantity < 5]
    total_inventory_value = sum(item.price * item.quantity for item in inventory)

    return render_template(
        "inventory.html",
        inventory=inventory,
        low_stock_items=low_stock_items,
        total_inventory_value=total_inventory_value
    )

# -- EXPENSE --
@app.route("/expense", methods=["GET", "POST"])
def expense_page():
    if request.method == "POST":
        category = request.form["category"]
        amount = int(request.form["amount"])

        new_exp = Expense(category=category, amount=amount)
        db.session.add(new_exp)
        db.session.commit()

    expenses = Expense.query.all()

    total_expenses = sum(exp.amount for exp in expenses)
    total_income = session.get("total_income", 0)
    remaining_money = total_income - total_expenses

    return render_template(
        "expense.html",
        expenses=expenses,
        total_expenses=total_expenses,
        remaining_money=remaining_money,
        total_income=total_income
    )

# -- DELETE --
@app.route("/delete/expense/<int:id>")
def delete_expense(id):
    exp = Expense.query.get(id)
    if exp:
        db.session.delete(exp)
        db.session.commit()
    return redirect(url_for("expense_page"))

@app.route("/delete/product/<int:id>")
def delete_product(id):
    item = Inventory.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("inventory_page"))

# -- RUN APP --
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
