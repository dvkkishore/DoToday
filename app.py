from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///db.sqlite'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    complete = db.Column(db.Boolean)
    date=db.Column(db.Date)
    collection = db.Column(db.String, nullable = False)
    deleted = db.Column(db.Boolean)

class Trashed(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    complete = db.Column(db.Boolean)
    date=db.Column(db.Date)
    collection = db.Column(db.String, nullable = False)
    deleted = db.Column(db.Boolean)    

def get_collection_data():
    todo_list = ToDo.query.all()
    collections = []
    for collection_name in todo_list:
        collections.append(collection_name.collection.capitalize())
    return list(set(collections))

@app.route('/')
def index():
    todo_list = ToDo.query.all()
    return render_template("index.html", todo_list = todo_list, collections = get_collection_data())

@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    collection = request.form.get("collection")
    if collection == "":
        collection = "General"
    new_todo = ToDo(title = title, complete = False, collection = collection.lower().strip(), date = datetime.now(), deleted = False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete', methods=["GET"])
def delete():
    id = request.args.get("id")
    del_todo = ToDo.query.filter_by(id = id).first()
    trashed_todo = Trashed(title = del_todo.title, complete = del_todo.complete, collection = del_todo.collection, date = del_todo.date, deleted = True)
    db.session.add(trashed_todo)
    db.session.delete(del_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/permanentdelete', methods=["GET"])
def permanent_delete():
    id = request.args.get("id")
    del_todo = Trashed.query.filter_by(id = id).first()
    db.session.delete(del_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update', methods=["GET"])
def update():
    id = request.args.get("id")
    todo = ToDo.query.filter_by(id=id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/restore', methods=["GET"])
def restore():
    id = request.args.get("id")
    trash_todo = Trashed.query.filter_by(id = id).first()
    restore_todo = ToDo(title = trash_todo.title, complete = trash_todo.complete, collection = trash_todo.collection, date = trash_todo.date, deleted = False)
    db.session.add(restore_todo)
    db.session.delete(trash_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/<collection_name>', methods = ["POST", "GET"])
def collection_page(collection_name = None):
    collection_list = ToDo.query.filter_by( collection = collection_name.lower() )
    return render_template("index.html", todo_list = collection_list, collections = get_collection_data())

@app.route('/completed', methods = ["POST", "GET"])
def completed_page():
    completed_list = ToDo.query.filter_by( complete = True )
    return render_template("index.html", todo_list = completed_list, collections = get_collection_data())

@app.route('/trash', methods = ["POST", "GET"])
def trash_page():
    trash_list = Trashed.query.all()
    return render_template("index.html", todo_list = trash_list, collections = get_collection_data())    

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)   