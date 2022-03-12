from crypt import methods
from dis import dis
import os
import re
from shutil import move
from sre_constants import SUCCESS

from numpy import char
import utils
from flask import Flask, abort, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.secret_key = "secretStuff"
app.config['UPLOAD_EXTENSIONS'] = ['.txt']
app.config['UPLOAD_PATH'] = 'uploads' 
global_ship_grids = []


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
          filePath = os.path.join(app.config['UPLOAD_PATH'],filename)
          f.save(filePath)
          session['filePath'] = filePath
          openFile = open(filePath,'r')
          containers = []
          ship_grid = utils.create_ship_grid(8,12)
          utils.update_ship_grid(openFile,ship_grid,containers)
          ship_grid_flipped = ship_grid[::-1][:]
      option = request.form['services']
      if option == 'Transfer':
          return render_template('initialTransferService.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len)
      else:
          return render_template('initialBalancePage.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len)

#Transfer functions and html templates

@app.route('/starttransfer', methods = ['GET','POST'])
def start_transfer():
    if request.method == 'POST':
        filePath = session.get('filePath', None)
        openFile = open(filePath,'r')
        containers = []
        ship_grid = utils.create_ship_grid(8,12)
        openFile = open(filePath,'r')
        utils.update_ship_grid(openFile,ship_grid,containers)
        ship_grid_flipped = ship_grid[::-1][:]
    return render_template('transferService.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len,display_list=display_list,path_list=path_list,next_move_list=next_move_list)

@app.route('/transfersteps', methods = ['GET','POST'])
def next_step_transfer():
    return render_template('transferService.html')

@app.route('/transfercomplete', methods = ['GET', 'POST'])
def transfered():
    return render_template('transfered.html')

#Balance functions and html templates

@app.route('/startbalance', methods = ['GET','POST'])
def start_balance():
    global global_ship_grids
    if request.method == 'POST':
        filePath = session.get('filePath', None)
        openFile = open(filePath,'r')
        containers = []
        ship_grid = utils.create_ship_grid(8,12)
        openFile = open(filePath,'r')
        utils.update_ship_grid(openFile,ship_grid,containers)
        ship_grid_flipped = ship_grid[::-1][:]
        move_list,ship_grids,success = utils.balance(ship_grid,containers)
        global_ship_grids = ship_grids[1:]
        if move_list is not None:
            display_list = []
            path_list = []
            for step in move_list[0]:
                if not step:
                    continue
                numbers = re.findall(r"[^\[\],\sa-z]",step)
                path_numbers = [chr(ord('7')-ord(numbers[0])+ord('0')),numbers[1],chr(ord('7')-ord(numbers[2])+ord('0')),numbers[3]]
                adjusted_numbers = [chr(ord(num)+1) for num in numbers]
                path_step = "["+path_numbers[0]+", "+path_numbers[1]+"] to ["+path_numbers[2]+", "+path_numbers[3]+"]"
                display_step = "["+adjusted_numbers[0]+", "+adjusted_numbers[1]+"] to ["+adjusted_numbers[2]+", "+adjusted_numbers[3]+"]"
                display_list.append(display_step)
                path_list.append(path_step)
            next_move_list = move_list[1:]
            session['next_move_list'] = next_move_list
            #if next_move_list is not None:
            return render_template('balanceService.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len,display_list=display_list,path_list=path_list,next_move_list=next_move_list)
            #else:
        else:
            return render_template('balanced.html')

@app.route('/balancesteps', methods = ['GET' , 'POST'])
def next_step_balance():
    global global_ship_grids
    if request.method == 'POST':
        move_list = session.get('next_move_list',None)
        ship_grid = global_ship_grids[0]
        global_ship_grids = global_ship_grids[1:]
        ship_grid_flipped = ship_grid[::-1][:]
        if move_list is not None:
            display_list = []
            path_list = []
            for step in move_list[0]:
                if not step:
                    continue
                numbers = re.findall(r"[^\[\],\sa-z]",step)
                path_numbers = [chr(ord('7')-ord(numbers[0])+ord('0')),numbers[1],chr(ord('7')-ord(numbers[2])+ord('0')),numbers[3]]
                adjusted_numbers = [chr(ord(num)+1) for num in numbers]
                path_step = "["+path_numbers[0]+", "+path_numbers[1]+"] to ["+path_numbers[2]+", "+path_numbers[3]+"]"
                display_step = "["+adjusted_numbers[0]+", "+adjusted_numbers[1]+"] to ["+adjusted_numbers[2]+", "+adjusted_numbers[3]+"]"
                display_list.append(display_step)
                path_list.append(path_step)
            next_move_list = move_list[1:]
            session['next_move_list'] = next_move_list
        if move_list is not None:
            return render_template('balanceService.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len,display_list=display_list,path_list=path_list,next_move_list=next_move_list)
        else:
            return render_template('balanced.html')

@app.route('/balanced', methods = ['GET','POST'])
def balanced():
    return render_template('balanced.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')
