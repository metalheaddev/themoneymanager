import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3

#create application object
app = Flask(__name__)
app.config.from_object(__name__)

#Load default config and override config from environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'tmm.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
#Loads config from environment variable if exists
app.config.from_envvar('TMM_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv
    
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        
######VIEWS#######

@app.route('/')
def display_expenses():
    db = get_db()
    cur = db.execute('select date, amount, description, category from expenses order by date desc')
    expenses = cur.fetchall()
    return render_template('display_expenses.html', expenses=expenses)
    
@app.route('/add', methods=['POST'])
def add_entry():
    #Checks if user is logged in
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into expenses (date, amount, description, category) values (?, ?, ?, ?)',
            [request.form['date'], request.form['amount'], request.form['description'], request.form['category']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('display_expenses'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('display_expenses'))
    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('display_expenses'))



def get_db():
    """opens a new database connection if there is none yet for the current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__=='__main__':
    app.run()
