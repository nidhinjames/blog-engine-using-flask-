import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash
app = Flask(__name__)
app.config.from_object(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
DATABASE=os.path.join(app.root_path, 'blog.db'),
DEBUG=True,
SECRET_KEY='development key',
USERNAME='nidhin',
PASSWORD='kurisunkal'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db




@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)






@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title, text) values (?, ?)',
			[request.form['title'], request.form['text']])
	db.commit()
	flash('New entry was successfully posted')
	
	return redirect(url_for('show_entries'))





@app.route('/post/<post_title>',methods=['GET','POST'])
def show_post(post_title):
	title = post_title
	db = get_db()
	cur = db.execute('select text from entries where title = (?)',[post_title])
	text = cur.fetchall()
	cur = db.execute('select  c_name, comment from comments where c_id = (?) order by c_name desc',[title])
        entries = cur.fetchall()
        return render_template('comment_entries.html',title = title, text = text, entries=entries)





@app.route('/comment_entry/<title>', methods=['GET','POST'])
def comment_entry(title):
	db = get_db()	
	name = request.form['name']
	text = request.form['text']
	db.execute('insert into comments(c_id,c_name,comment) values (?,?,?)',[title,name,text])
	db.commit()
	cur = db.execute('select  c_name, comment from comments where c_id = (?) order by c_name desc',[title])
        entries = cur.fetchall()
	flash('New entry was successfully posted')
#       return redirect(url_for('show_entries'))
	return render_template('comment_entries.html', title = title, text = text, entries = entries)



 
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
			return redirect(url_for('show_entries'))
	return render_template('login.html', error = error)
	


	

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))






@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()





if __name__ == '__main__':
  app.run()
