from app import app
from app.forms import LoginForm

from flask import flash, render_template, redirect


@app.route('/')
def index():
    users = {'username': 'Mixalis'}	

    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template('index.html', title='Home', user=users, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, password {}'.format(form.username.data, form.password.data))
        return redirect('/')

    return render_template('login.html', title='Sign In', form=form)
