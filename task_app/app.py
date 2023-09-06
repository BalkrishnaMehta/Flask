from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'secret_key'

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY,
              password TEXT,
              is_head INTEGER DEFAULT 0)''')
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              task TEXT,
              status TEXT DEFAULT 'Pending',
              username TEXT,
              FOREIGN KEY (username) REFERENCES users(username))''')

c.execute("SELECT * FROM users WHERE username=?", ('admin',))
user = c.fetchone()

if not user:
    hashed_password = generate_password_hash('admin')
    c.execute("INSERT INTO users (username, password, is_head) VALUES (?, ?, ?)",
              ('admin', hashed_password, 1))
    conn.commit()

conn.close()

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    submit = SubmitField('Assign Task')

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('tasks'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['username'] = username
            session['is_head'] = bool(user[2])
            flash('Login successful!', 'success')
            return redirect(url_for('tasks'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('tasks'))

    form = SignupForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if not re.search(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            flash('Password must have at least 8 characters, 1 uppercase letter, 1 symbol, and 1 number.', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
        else:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()

            if user:
                flash('Username already exists. Please choose a different username.', 'danger')
            else:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
                conn.commit()
                flash('Account created successfully! You can now login.', 'success')
                return redirect(url_for('login'))

            conn.close()

    return render_template('signup.html', form=form)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'username' not in session:
        return redirect(url_for('login'))

    if session['is_head']:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE is_head=0")  # Exclude project heads
        users = c.fetchall()

        tasks = []
        for user in users:
            c.execute("SELECT id, task, status FROM tasks WHERE username=? ORDER BY CASE status WHEN 'Pending' THEN 1 WHEN 'In-Progress' THEN 2 WHEN 'Done' THEN 3 END", (user[0],))
            user_tasks = c.fetchall()
            tasks.append((user[0], user_tasks))

        conn.close()

        form = TaskForm()

        if request.method == 'POST':
            assigned_user = request.form.get('assigned_user')
            task = form.task.data

            conn = sqlite3.connect('users.db')
            c = conn.cursor()

            c.execute("INSERT INTO tasks (task, status, username) VALUES (?, ?, ?)",
                      (task, 'Pending', assigned_user))

            conn.commit()
            conn.close()

            flash('Task assigned successfully!', 'success')
            return redirect(url_for('tasks'))

        return render_template('tasks.html', form=form, tasks=tasks, is_head=True)

    else:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT id, task, status FROM tasks WHERE username=? ORDER BY CASE status WHEN 'Pending' THEN 1 WHEN 'In-Progress' THEN 2 WHEN 'Done' THEN 3 END", (session['username'],))
        tasks = c.fetchall()

        conn.close()
        form = TaskForm()
        return render_template('tasks.html', tasks=tasks, is_head=False, user=session['username'], form=form)

@app.route('/tasks/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    task = c.fetchone()

    if not task:
        flash('Task does not exist.', 'danger')
    elif task[3] != session['username']:
        flash('You are not authorized to update this task.', 'danger')
    else:
        new_status = request.form.get('status')

        c.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
        conn.commit()
        flash('Task status updated successfully!', 'success')

    conn.close()
    return redirect(url_for('tasks'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
