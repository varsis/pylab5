#!/usr/bin/env python

import sqlite3
from flask import Flask,render_template, redirect,url_for,request,session, flash, abort
#conn = sqlite3.connect('pylab4.db')

app = Flask(__name__)
conn = None

# default login/password = username/password

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def get_conn():
	global conn
	if conn is None:
		conn = sqlite3.connect('pylab4.db')
		conn.row_factory = sqlite3.Row
	return conn

def close_connection():
	global conn
	if conn is not None:
		conn.close()
		conn = None

def query_db(query, args=(), one=False):
	cur = get_conn().cursor()
	cur.execute(query,args)
	r = cur.fetchall()
	cur.close()
	return (r[0] if r else None) if one else r

def add_task(task):
	query_db("insert into tasks(category,priority,description) values(?,?,?)",task, one=True)
	get_conn().commit();
	
def remove_task(rowid):
	query_db("delete from tasks where rowid=?",rowid, one=True)
	get_conn().commit();

def cols():
	return ["category","priority","description"]

def is_logged_in(): 
	return session['username']

#idealy use ajax and use delete...
@app.route('/tasks/delete',methods=["POST"])
def delete():
	if not is_logged_in():
		abort(401)
	rowid = request.form['id']	
	remove_task(rowid)
	return redirect(url_for('tasks'))

# log the user in. Redirect to home
@app.route('/login',methods=["POST"])
def login():
	form = request.form
	username = form['username']
	password = form['password']
	user = query_db("select * from user where username = ? and password = ?",(username,password));
	if user:
		session['username'] = request.form['username']
		flash('Login successful',"success")
	else:
		flash('Incorrect password or login','danger')
	return redirect(url_for('tasks'))
	

#remove the sessions
@app.route('/logout')
def logout():
	session.pop('username', None)
	flash('Logout successful',"success")
	return redirect(url_for('tasks'))
	

#main tasks
@app.route('/',methods=["GET","POST"])
def tasks(name=None):
	if request.method == "POST":
		if not is_logged_in():
			abort(401)
		form = request.form
		try:  
			formPriority = int(form['priority'])
			if formPriority > 100 or formPriority < 0:
				raise Exception
		except:
			return "Bad priority"
				
		task = (form['category'],form['priority'],form['description'])	
		add_task(task)
		flash('Task added',"success")
		return redirect(url_for('tasks'))

	#get 
	elif request.method == "GET":
		tasks = query_db("select rowid,* from tasks order by priority DESC");
		return render_template('main.html', name=name, cols=cols(),tasks=tasks)

if __name__ == "__main__":
	app.debug = True
	app.run()
