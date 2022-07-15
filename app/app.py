import os

from psycopg2.extras import RealDictCursor
from psycopg2.errors import RaiseException
from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from auth_middleware import is_user
from db import *


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
bcrypt = Bcrypt(app)


# TODO: Redirect to login if not logged in
@app.route('/', methods=['GET'])
@is_user
def index():
    context = {
        'units': get_units(),
        'items': get_all_items(),
        'warehouses': get_warehouses()
    }
    return render_template('index.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT pass, username FROM person WHERE email = %s", (request.form["email"],))
        res = cur.fetchone()
        if not res:
            flash("No user found with these credentials.")
            return redirect(url_for('index'))
        bcrypt_password = bytes(res["pass"])
        username = res["username"]
        close_cursor(conn, cur)
        if bcrypt.check_password_hash(bcrypt_password, request.form["password"]):
            session["username"] = username
        else:
            flash("No user found with these credentials.")
        return redirect(url_for('index'))


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        form = request.form
        if not form["username"] or not form["email"] or not form["phone"] or not form["phone"] or not form["name"] or not form["surname"]:
            flash("All fields required")
            return render_template('register.html')
        elif len(form["password"]) < 8:
            flash("Password must be at least 8 characters long")
            return render_template('register.html')
        else:
            try:
                conn, cur = get_cursor()
                cur.execute(
                    "INSERT INTO person(username, pass, email, phone, name, surname) VALUES(%s, %s, %s, %s, %s, %s)",
                    (form["username"],
                     psycopg2.Binary(bcrypt.generate_password_hash(form["password"])),
                     form["email"],
                     form["phone"],
                     form["name"],
                     form["surname"]
                     ))

                conn.commit()
                close_cursor(conn, cur)
            except RaiseException as e:
                if "username already in use" in str(e):
                    flash("Username in use!")
                    return render_template('register.html')
                # TODO: HANDLE EXCEPTION
    return redirect(url_for('login'))


@app.route('/users/<user>', methods=['GET'])
@is_user
def users(user):
    context = {
        'units': get_units(),
        'items': get_items_of_owner(user),
        'user_info': get_user_info(user),
        'warehouses': get_warehouses()
    }
    return render_template('user.html', **context)


@app.route('/storage_units/<unit>', methods=['GET'])
@is_user
def storage_units(unit):
    context = {
        'unit_info': get_unit_info(unit),
        'units': get_units(),
        'items': get_items_of_owner(unit),
        'warehouses': get_warehouses()
    }
    return render_template('unit.html', **context)


@app.route('/items/<item>', methods=['GET'])
@is_user
def items(item):
    context = {
        'units': get_units(),
        'items': get_item_ownerships(item),
        'warehouses': get_warehouses(),
        'itemname': item
    }
    return render_template('item.html', **context)


@app.route('/api/add', methods=['POST'])
@is_user
def new_item():
    if not request.form["quantity"].isnumeric():
        flash("What did you do!")
    else:
        form = request.form
        conn, cur = get_cursor()
        cur.execute("SELECT add_new_ownership(%s, %s, %s);",
                    (form["owner"],
                     form["name"],
                     form["quantity"]
                     ))
        conn.commit()
        close_cursor(conn, cur)
    return redirect(url_for('index'))

# TODO: Na svinei apo ton palio kai na tsekarei oti htan warehouse
# TODO: Na dexetai alla quantities

@app.route('/api/claim', methods=['POST'])
@is_user
def claim():
    if not request.form["quantity"].isnumeric():
        flash("Only positive numbers are allowed (you filthy boye).")
        return redirect(url_for('index'))
    try:
        conn, cur = get_cursor()
        cur.execute("SELECT transfer_possession(%s, %s, %s, %s);",
                    (session["username"],
                     request.form["owner"],
                     request.form["id"],
                     request.form["quantity"]
                     ))
        conn.commit()
        close_cursor(conn, cur)
    except RaiseException as e:
        if "Requested more than existing" in str(e):
            flash("Requested more than existing.")
        else:
            flash("Something went wrong. Contact an admin.")
    except Exception as e:
        print(e)
    return redirect(url_for('index'))


@app.route('/api/return', methods=['POST'])
@is_user
def return_api():
    if not request.form["quantity"].isnumeric():
        flash("Only positive numbers are allowed (you filthy boye).")
        return redirect(url_for('index'))
    conn, cur = get_cursor()
    cur.execute("SELECT transfer_possession(%s, %s, %s, %s);",
                (request.form["owner"],
                 session["username"],
                 request.form["id"],
                 request.form["quantity"]
                 ))
    conn.commit()
    close_cursor(conn, cur)
    return redirect(url_for('index'))


@app.route('/api/new_warehouse', methods=['POST'])
@is_user
def new_warehouse():
    form = request.form
    conn, cur = get_cursor()
    cur.execute("INSERT INTO warehouse VALUES(%s, %s)", (form["name"], form["location"]))
    conn.commit()
    close_cursor(conn, cur)
    return redirect(url_for('index'))


@app.route('/api/rename_item', methods=['POST'])
@is_user
def rename_item():
    form = request.form
    conn, cur = get_cursor()
    cur.execute("UPDATE item SET itemname = %s WHERE itemname = %s", (form["new_name"], form["old_name"]))
    conn.commit()
    close_cursor(conn, cur)
    return redirect(url_for('index'))


@app.route('/api/delete_item', methods=['POST'])
@is_user
def delete_item():
    form = request.form
    conn, cur = get_cursor()
    cur.execute("DELETE FROM item WHERE itemname = %s", (form["name"],))
    conn.commit()
    close_cursor(conn, cur)
    return redirect(url_for('index'))


@app.route('/api/delete_warehouse', methods=['POST'])
@is_user
def delete_warehouse():
    form = request.form
    conn, cur = get_cursor()
    cur.execute("DELETE FROM storage WHERE EXISTS (SELECT storagename FROM warehouse WHERE storagename=%s AND storage.storagename = warehouse.storagename)", (form["name"],))
    conn.commit()
    close_cursor(conn, cur)
    return redirect(url_for('index'))


def get_units():
    conn, cur = get_cursor()
    cur.execute("""SELECT username, 'person' type FROM person
    UNION SELECT storagename, 'storage' type from warehouse
    ORDER BY type, username""")
    units = [(unit[0], unit[1]) for unit in cur]
    close_cursor(conn, cur)
    return units


def get_items_of_owner(owner):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """SELECT id, itemname, storagename, quantity, ownership_date, COALESCE(type, 'storage') type FROM has NATURAL JOIN item
    LEFT JOIN
    (SELECT *, 'person' type FROM person) a
    ON a.username = has.storagename where storagename = %s ORDER BY itemname""",
        (owner,))
    items = cur.fetchall()
    close_cursor(conn, cur)
    return items


def get_all_items():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT id, itemname, storagename, quantity, ownership_date, COALESCE(type, 'storage') type FROM has NATURAL JOIN item
    LEFT JOIN
    (SELECT *, 'person' type FROM person) a
    ON a.username = has.storagename ORDER BY itemname""")
    items = cur.fetchall()
    close_cursor(conn, cur)
    return items


def get_item_ownerships(item):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT id, itemname, storagename, quantity, ownership_date, COALESCE(type, 'storage') type FROM has NATURAL JOIN item
    LEFT JOIN
    (SELECT *, 'person' type FROM person) a
    ON a.username = has.storagename
    WHERE itemname = %s ORDER BY itemname""", (item,))
    items = cur.fetchall()
    close_cursor(conn, cur)
    return items


def get_user_info(username):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT name || ' ' || surname name, username, phone FROM person where username = %s""", (username,))
    info = cur.fetchone()
    close_cursor(conn, cur)
    return info


def get_unit_info(unit):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT storagename, location FROM warehouse NATURAL JOIN storage WHERE storagename = %s""", (unit,))
    info = cur.fetchone()
    close_cursor(conn, cur)
    return info


def get_warehouses():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT storagename FROM warehouse""")
    warehouses = cur.fetchall()
    close_cursor(conn, cur)
    return warehouses


# TODO: Make admin decorator check that redirects to no access
if __name__ == '__main__':
    Flask.run(app, debug=True)
