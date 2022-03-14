from calendar import c
from crypt import methods
from dis import dis
import os
import re
from shutil import move
from sre_constants import SUCCESS
import numpy as np
import copy

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
container_locs_unload = []


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
   global global_ship_grids
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
          global_ship_grids.append(ship_grid)
          ship_grid_flipped = ship_grid[::-1][:]
      option = request.form['services']
      print(len(global_ship_grids))
      if option == 'Transfer':
          return render_template('initialTransferService.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len)
      else:
          return render_template('initialBalancePage.html',ship_grid=ship_grid_flipped, enumerate=enumerate,len=len)

#Transfer functions and html templates

@app.route('/starttransfer', methods = ['POST'])
def starttransfer():
    global global_ship_grids
    global container_locs_unload
    print(len(global_ship_grids))
    if request.method == 'POST':

        #User inputed contaienrs for unload and grid coordinates for load
        ret = request.get_json()
        unload_containers = ret['unloading']
        load_coordinations = ret['loading']

        container_values = []
        for dictionary in unload_containers:
            container_values.append(list(dictionary.values()))

        load_coords = []
        for dictionary in load_coordinations:
            load_coords.append(dictionary['grid position'])

        #Open manifest to create grid and update it with the proper containers
        filePath = session.get('filePath', None)
        openFile = open(filePath,'r')
        containers = []
        ship_grid = utils.create_ship_grid(8,12)
        openFile = open(filePath,'r')
        utils.update_ship_grid(openFile,ship_grid,containers)


        # Finding which containers are we need to unload from the ship
        for container in containers:
            for values in container_values:
                name, weight = values[0], int(values[1])
                if ship_grid[container[0]][container[1]].container.name == name and \
                    ship_grid[container[0]][container[1]].container.weight == weight:
                    
                    container_locs_unload.append(container)

        # flip container locations
        #'[7,3]','[7,4]'
        adjusted_load_coords = []
        for idx, container in enumerate(load_coords):
            r,c = [int(val) for val in container.strip('[]').split(',')]
            adjusted_load_coords.append([7 - r, c])        
        
        #loading 
        invalid_locs = 0
        for container in adjusted_load_coords:
            r, c = container[0], container[1]
            if r > 0:
                if ship_grid[r - 1][c].available is True:
                    if [r-1, c] not in adjusted_load_coords:
                    # invalid location
                        return redirect(url_for('error'))

        if len(load_coords) > 0:
            session['load_coords'] = load_coords
            return redirect(url_for('load_container_form'))
        else:
            return redirect(url_for('process_transfer'))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/loadcontainerform', methods = ['GET','POST'])
def load_container_form():

    load_coords = session.get('load_coords',None)
    adjusted_load_coords = []
    for idx, container in enumerate(load_coords):
        r,c = [int(val) for val in container.strip('[]').split(',')]
        adjusted_load_coords.append([7 - r+1, c+1])      
    return render_template('loadContainerForm.html',enumerate=enumerate,load_coords=load_coords,adjusted_load_coords=adjusted_load_coords)

@app.route('/transferprocessing', methods = ['GET','POST'])
def process_transfer():
    global global_ship_grids
    global container_locs_unload
    print(len(global_ship_grids))
    containers_and_locs = []
    if request.method == 'POST':
        load_coords = session.get('load_coords',None)
        for i in range(len(load_coords)):
            name_form = 'nameform' + str(i)
            nameForm = request.form.get(name_form)
            weight_form = 'weightform' + str(i)
            weightForm = request.form.get(weight_form)
            r,c = [int(val) for val in load_coords[i].strip('[]').split(',')]
            containers_and_locs.append((utils.Container(nameForm, int(weightForm)), [7 - r, c]))
    
    all_steps, ship_grids = None, []
    if not containers_and_locs:
        ship_grid = copy.deepcopy(global_ship_grids[0])
        all_steps, ship_grids = utils.unload(container_locs_unload, ship_grid)
    else:
        ship_grid = copy.deepcopy(global_ship_grids[0])
        all_steps, ship_grids = utils.load(containers_and_locs, ship_grid)
        ship_grid = copy.deepcopy(ship_grids[-1])
        if len(container_locs_unload) > 0:
            new_steps, new_ship_grids = utils.unload(container_locs_unload, ship_grid)

            for steps in new_steps:
                all_steps.append(steps)
        
        ship_grids.append(new_ship_grids)
        r, c = np.array(global_ship_grids[0]).shape
        ship_grids = utils.reformat_grid_list(ship_grids, r, c)

    global_ship_grids = ship_grids
    ship_grid_flipped = global_ship_grids[0][::-1][:]
    global_ship_grids = global_ship_grids[1:]

    display_list = []
    path_list = []
    if len(all_steps) > 0:
        for step in all_steps[0]:
            if not step:
                continue
            numbers = re.findall(r"[^\[\],\sa-z]",step)
            path_numbers = [chr(ord('7')-ord(numbers[0])+ord('0')),numbers[1],chr(ord('7')-ord(numbers[2])+ord('0')),numbers[3]]
            adjusted_numbers = [chr(ord(num)+1) for num in numbers]
            path_step = "["+path_numbers[0]+", "+path_numbers[1]+"] to ["+path_numbers[2]+", "+path_numbers[3]+"]"
            display_step = "["+adjusted_numbers[0]+", "+adjusted_numbers[1]+"] to ["+adjusted_numbers[2]+", "+adjusted_numbers[3]+"]"
            display_list.append(display_step)
            path_list.append(path_step)
    next_move_list = all_steps[1:]
    session['next_move_list'] = next_move_list
    return render_template('transferService.html', ship_grid=ship_grid_flipped, enumerate=enumerate, len=len,display_list=display_list,path_list=path_list,next_move_list=next_move_list)

@app.route('/transfersteps', methods = ['GET','POST'])
def transfer_steps():
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
            print(move_list[0][-1][10:])
            next_move_list = move_list[1:]
            session['next_move_list'] = next_move_list
            return render_template('transferService.html', ship_grid=ship_grid_flipped, enumerate=enumerate, len=len,display_list=display_list,path_list=path_list,next_move_list=next_move_list)

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
        move_list,ship_grids,success = utils.balance(ship_grid,containers)
        ship_grid_flipped = ship_grids[0][::-1][:]
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
            print(move_list[0][-1][10:])
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
