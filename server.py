#!/usr/bin/env python

import sqlite3
from flask import Flask,render_template, redirect,url_for,request
#conn = sqlite3.connect('pylab4.db')

app = Flask(__name__)
conn = None

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

@app.route('/')
def hello_world():
    return 'Hello, World!'

#idealy use ajax and use delete...
@app.route('/tasks/delete',methods=["POST"])
def delete():
	rowid = request.form['id']	
	remove_task(rowid)
	return redirect(url_for('tasks'))

@app.route('/tasks',methods=["GET","POST"])
def tasks(name=None):
	if request.method == "POST":
		form = request.form
		try: 
			formPriority = int(form['priority'])
			if formPriority > 100 or formPriority < 0:
				raise Exception
		except:
			return "Bad priority"
				
		task = (form['category'],form['priority'],form['description'])	
		add_task(task)
		return redirect(url_for('tasks'))

	#get 
	elif request.method == "GET":
		tasks = query_db("select rowid,* from tasks order by priority DESC");
		return render_template('main.html', name=name, cols=cols(),tasks=tasks)

'''@app.route('/task1',methods=["GET","POST"])
def task():
	#post
	if request.method == "POST":
		category = request.form['category']
		tasks.append({'category': category})
		return redirect(url_for('task'))

	#get 
	elif request.method == "GET":
		cols = ["category","priority","description"]
		return render_template('main.html',cols=cols())
'''		

if __name__ == "__main__":
	app.debug = True
	app.run()
