import os
from flask import Flask, abort, render_template, request, redirect, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = "secretStuff"
app.config['UPLOAD_EXTENSIONS'] = ['.txt']
app.config['UPLOAD_PATH'] = 'uploads' 

@app.route("/")
def home():
    return render_template("home.html")

# Route for handling the login page logic
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        session['user'] = username
        return redirect('/dashboard')

    return render_template("login.html")


@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():
    if 'user' in session:

        return render_template("dashboard.html", username=session['user'])

    return '<h1>You are not logged in.</h1>'
	
@app.route('/service', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      if f != '':
          file_ext = os.path.splitext(filename)[1]
          if file_ext not in app.config['UPLOAD_EXTENSIONS']:
              return "Invalid file", 400
          f.save(os.path.join(app.config['UPLOAD_PATH'],filename))
      option = request.form['services']
      if option == 'Transfer':
          return render_template('transferService.html')
      else:
          return render_template('balanceService.html')


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')
