from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "secretStuff" 

@app.route("/")
def home():
    return render_template("home.html")

# Route for handling the login page logic
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if(request.method == 'POST'):
        username = request.form.get('username')
        session['user'] = username
        return redirect('/dashboard')

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if('user' in session):
        return render_template("dashboard.html", username=session['user'])

    return '<h1>You are not logged in.</h1>'


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')
