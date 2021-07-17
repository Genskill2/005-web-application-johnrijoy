import datetime

from flask import Blueprint
from flask import render_template, request, redirect, url_for, jsonify
from flask import g

from . import db

bp = Blueprint("pets", "pets", url_prefix="")

def format_date(d):
    if d:
        d = datetime.datetime.strptime(d, '%Y-%m-%d')
        v = d.strftime("%a - %b %d, %Y")
        return v
    else:
        return None

@bp.route("/search/<field>/<value>")
def search(field, value):
    # TBD
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id") # TODO. This is currently not used. 
    order = request.args.get("order", "asc")
    # order based on name, bought, sold, id
    # print(" debug: {}, {}".format(oby, order)) 
    if order == "asc":
        command = "select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s, tag t, tags_pets tp where p.species = s.id AND t.name = '{}' AND tp.tag = t.id AND tp.pet = p.id order by p.{}".format(value, oby) 
        cursor.execute(f"{command}")
    else:
        command = "select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s, tag t, tags_pets tp where p.species = s.id AND t.name = '{}' AND tp.tag = t.id AND tp.pet = p.id order by p.{} desc".format(value, oby)
        cursor.execute(f"{command}")
    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order="desc" if order=="asc" else "asc")

@bp.route("/")
def dashboard():
    conn = db.get_db()
    cursor = conn.cursor()
    oby = request.args.get("order_by", "id") # TODO. This is currently not used. 
    order = request.args.get("order", "asc")
    # order based on name, bought, sold, id
    # print(" debug: {}, {}".format(oby, order)) 
    if order == "asc":
        command = "select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.{}".format(oby)
        cursor.execute(f"{command}")
    else:
        command = "select p.id, p.name, p.bought, p.sold, s.name from pet p, animal s where p.species = s.id order by p.{} desc".format(oby)
        cursor.execute(f"{command}")
    pets = cursor.fetchall()
    return render_template('index.html', pets = pets, order="desc" if order=="asc" else "asc")


@bp.route("/<pid>")
def pet_info(pid): 
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
    pet = cursor.fetchone()
    cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
    tags = (x[0] for x in cursor.fetchall())
    name, bought, sold, description, species = pet
    data = dict(id = pid,
                name = name,
                bought = format_date(bought),
                sold = format_date(sold),
                description = description, #TODO Not being displayed
                species = species,
                tags = tags)
    return render_template("petdetail.html", **data)

@bp.route("/<pid>/edit", methods=["GET", "POST"])
def edit(pid):
    conn = db.get_db()
    cursor = conn.cursor()
    if request.method == "GET":
        cursor.execute("select p.name, p.bought, p.sold, p.description, s.name from pet p, animal s where p.species = s.id and p.id = ?", [pid])
        pet = cursor.fetchone()
        cursor.execute("select t.name from tags_pets tp, tag t where tp.pet = ? and tp.tag = t.id", [pid])
        tags = (x[0] for x in cursor.fetchall())
        name, bought, sold, description, species = pet
        data = dict(id = pid,
                    name = name,
                    bought = format_date(bought),
                    sold = format_date(sold),
                    description = description,
                    species = species,
                    tags = tags)
        return render_template("editpet.html", **data)
    elif request.method == "POST":
        description = request.form.get('description')
        sold = request.form.get("sold")
        # TODO Handle sold
        # current model only allows to mark as sold for a previuosly unsold entry
        # print('Debug: {}'.format(sold))
        
        cursor.execute("UPDATE pet SET description = ? WHERE id = ?;", [description, pid])
        conn.commit()
        
        if sold == '1':
            cursor.execute("select sold from pet where id = ?", [pid])
            date = cursor.fetchone()[0]
            print(date)
            if date == '':            
                today = datetime.date.today()
                #print(today)
                #print(type(today))
                cursor.execute("UPDATE pet SET sold = ? WHERE id = ?;", [today, pid])
                conn.commit()        
        return redirect(url_for("pets.pet_info", pid=pid), 302)
        
    



