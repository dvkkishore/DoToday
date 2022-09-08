from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://urepwxb23k9c8gxz:5mBF5POn1BNIj31QeO6Z@bgn3aqslms9upamzfmi3-mysql.services.clever-cloud.com:3306/bgn3aqslms9upamzfmi3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(128), nullable = False)
    complete = db.Column(db.Boolean)
    date = db.Column(db.Integer)
    collection = db.Column(db.String(128), nullable = False)
    deleted = db.Column(db.Boolean)

def get_collection_data():
    todo_list = ToDo.query.filter_by( deleted = False )
    collections = []
    is_general_exist = False
    for collection_name in todo_list:
        if collection_name.collection != "general":
            collections.append(collection_name.collection.capitalize())
        else:
            is_general_exist = True
    if(is_general_exist):
        return ["General"] + sorted(list(set(collections)))
    return list(set(collections))

@app.route('/')

def index():
    todo_list = ToDo.query.filter_by( deleted = False)
    return render_template("index.html", todo_list = todo_list, collections = get_collection_data())

@app.route('/add', methods=["POST"])
def add():
    title = request.form.get("title")
    collection = request.form.get("collection")
    date = request.form.get("date")
    if collection == "":
        collection = "General"
    new_todo = ToDo(title = title, complete = False, collection = collection.lower().strip(), date = date, deleted = False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete', methods=["GET"])
def delete():
    id = request.args.get("id")
    del_todo = ToDo.query.filter_by(id = id).first()
    del_todo.deleted = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/permanentdelete', methods=["GET"])
def permanent_delete():
    id = request.args.get("id")
    del_todo = ToDo.query.filter_by(id = id).first()
    db.session.delete(del_todo)
    db.session.commit()
    return redirect(url_for('trash_page'))

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
    restore_todo = ToDo.query.filter_by(id = id).first()
    restore_todo.deleted = False
    db.session.commit()
    return redirect(url_for('trash_page'))

@app.route('/<collection_name>', methods = ["POST", "GET"])
def collection_page(collection_name = None):
    collection_list = ToDo.query.filter_by( collection = collection_name.lower(), deleted = False )
    return render_template("index.html", todo_list = collection_list, collections = get_collection_data())

@app.route('/completed', methods = ["POST", "GET"])
def completed_page():
    completed_list = ToDo.query.filter_by( complete = True, deleted = False )
    return render_template("index.html", todo_list = completed_list, collections = get_collection_data())

@app.route('/overdue', methods = ["POST", "GET"])
def overdue_page():
    req_date = datetime.date.today()
    overdue_list = ToDo.query.filter( ToDo.date < req_date , ToDo.deleted == False)
    print(overdue_list)
    return render_template("index.html", todo_list = overdue_list, collections = get_collection_data())

@app.route('/today', methods = ["POST", "GET"])
def today_page():
    req_date = datetime.date.today()
    today_list = ToDo.query.filter_by( date = req_date, deleted = False )
    return render_template("index.html", todo_list = today_list, collections = get_collection_data())    

@app.route('/tomorrow', methods = ["POST", "GET"])
def tomorrow_page():
    req_date = datetime.date.today()
    req_date += datetime.timedelta(days = 1)
    tomorrow_list = ToDo.query.filter_by( date = req_date, deleted = False )
    return render_template("index.html", todo_list = tomorrow_list, collections = get_collection_data())

@app.route('/upcoming', methods = ["POST", "GET"])
def upcoming_page():
    req_date = datetime.date.today()
    req_date += datetime.timedelta(days = 1)
    overdue_list = ToDo.query.filter( ToDo.date > req_date , ToDo.deleted == False)
    return render_template("index.html", todo_list = overdue_list, collections = get_collection_data())

@app.route('/trash', methods = ["POST", "GET"])
def trash_page():
    trash_list = ToDo.query.filter_by( deleted = True)
    return render_template("index.html", todo_list = trash_list, collections = get_collection_data())    

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)   