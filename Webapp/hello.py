from cmath import log
from contextlib import redirect_stdout
from crypt import methods
from curses import nonl
from glob import glob
from tkinter import filedialog
from unicodedata import name
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import make_response
from datetime import datetime
from datetime import date
import re
import json
from random import sample
import easygui
import os

app = Flask(__name__)


selectedPuzzle = "default"
defaultpuzzle = [['A', 'N', 'G'], ['E', '.', 'I'], ['C', 'L', 'A']]
custompuzzle = []

@app.route("/", methods=['GET','POST'])
def sign_in():
    return render_template('sign_in.html')

@app.route("/storeCreds", methods=['GET', 'POST'])
def storeCreds():
    if request.method == 'POST':
        tag = request.form['tag']
        if tag == "Default Puzzle":
            # global selectedPuzzle
            # selectedPuzzle = "defaultPuzzle"
            return redirect(url_for('defaultpuzzle'))
        elif tag == "Custom Puzzle":
            # global selectedPuzzle
            # selectedPuzzle = "customPuzzle"
            return redirect(url_for('custompuzzle'))

@app.route("/defaultpuzzle", methods=['GET', 'POST'])
def defaultpuzzle():
    return render_template('defaultpuzzle.html')

@app.route("/custompuzzle", methods=['GET', 'POST'])
def custompuzzle():
    return render_template('custompuzzle.html')

@app.route("/algorithmSelection", methods=['GET', 'POST'])
def algorithmSelection():
    if request.method == 'POST':
        tag = request.form['tag']
        print("request------------------")
        print(request)
        if tag == "Uniform Cost Search":
            return redirect(url_for('UniformCostSearch'))
        elif tag == "A* with the Misplaced Tile heuristic":
            return redirect(url_for('MisplacedTile'))
        elif tag == "A* with the Manhattan distance heuristic":
            return redirect(url_for('Manhattan'))
        
@app.route("/UniformCostSearch", methods=['GET', 'POST'])
def UniformCostSearch():
    if selectedPuzzle == "defaultPuzzle":
        return render_template('UniformCostSearch.html', puzzle=defaultpuzzle)
    else:
        return render_template('UniformCostSearch.html', puzzle=custompuzzle)

@app.route("/MisplacedTile", methods=['GET', 'POST'])
def MisplacedTile():
    return render_template('MisplacedTile.html')

@app.route("/Manhattan", methods=['GET', 'POST'])
def Manhattan():
    return render_template('Manhattan.html')















@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('home.html')






@app.route("/operations")
def operations():
    manifestPath = easygui.fileopenbox()                                            # Prompts the user with the file explorer to choose a manifest
    print(manifestPath)
    
    global manifestFilePath
    manifestFilePath = manifestPath
    
    # manifestPath = "Manifests/ShipCase4.txt"                     
    with open(manifestPath, mode = 'r', encoding= 'utf-8-sig') as f:                # Uses manifest path to open file
        lines = f.readlines()                                                       # List containing lines of file
        columns = ['position', 'weight', 'description']                             # Creates a list of column names
        infoList = []

        i = 1
        for line in lines:
            line = line.strip()                                                     # Remove the leading/trailing white spaces
            if line:
                d = {}
                data = [item.strip() for item in re.split(',(?![^\[]*])', line)]    # Uses regex to split the manifest data by the correct commas
                for index, elem in enumerate(data):
                    d[columns[index]] = data[index]
            infoList.append(d)
    return render_template('operations.html', text = infoList)

@app.route("/balance")
def balance():
    manifestPath = easygui.fileopenbox()                                            # Prompts the user with the file explorer to choose a manifest
    print(manifestPath)
    
    global manifestFilePath
    manifestFilePath = manifestPath
    
    # manifestPath = "Manifests/ShipCase5.txt"                     
    with open(manifestPath, mode = 'r', encoding= 'utf-8-sig') as f:                # Uses manifest path to open file
        lines = f.readlines()                                                       # List containing lines of file
        columns = ['position', 'weight', 'description']                             # Creates a list of column names
        infoList = []

        i = 1
        for line in lines:
            line = line.strip()                                                     # Remove the leading/trailing white spaces
            if line:
                d = {}
                data = [item.strip() for item in re.split(',(?![^\[]*])', line)]    # Uses regex to split the manifest data by the correct commas
                for index, elem in enumerate(data):
                    d[columns[index]] = data[index]
            infoList.append(d)
    return render_template('balance.html', text = infoList)

# Where the manifest json is sent in correct format, needing to be balanced
@app.route("/balanceAlgorithm", methods=["POST"])
def balanceAlgorithm():
    # This is where we can implement the python coding for algorithm
    req = request.get_json()
    # print("Printing JSON of changes to be made")
    # print(req)

    # ADD BALANCING FUNCTION HERE
    moves = 0
    move_Dict = {}
    tot_distance = 0
    all_best_balances = []

    def balance(sampleJson):
        
        right_weight, left_weight, maxWeight, max_Index, isBalanced, total = getWeights(sampleJson)

        # Code to check if things are balanceable
        rest_of_weight = right_weight + left_weight - maxWeight
        # if maxWeight * .9 > rest_of_weight:
        #     print("Unbalanceable! IMPLEMENT SPECIAL CASE HERE")
        #     sift(sampleJson)
        #     return

        # print(left_weight, right_weight)
        if left_weight == 0:
            balance_ratio = 1/right_weight
        elif right_weight == 0:
            balance_ratio = left_weight/1
        else:
            balance_ratio = left_weight/right_weight
        best_balance = 100000.0 #This value will hold the ratio closest to balanced
        best_index = ""
        curr_balance = 100000.0 #This value will hold the ratio of the containers we are currently considering swapping.
        
        if isBalanced == True: #When ship is balanced
            print("The ship is already balanced!")
            
        while(balance_ratio > 1.1 or balance_ratio < .9):
            all_best_balances.append(best_balance)
            if len(all_best_balances) >= 2:
                if all_best_balances[-2] == all_best_balances[-1]:
                    # print("UNBALANCEABLE SHIP. EXECUTING SIFT")
                    sift(sampleJson)
                    return
                    
            if balance_ratio > 1.1: #Left side is heavier we need to move something from here to right side
                
                for i in range(8,0,-1):
                    for j in range(6,0,-1):
                        left_cont = makeIndex(i,j) #left_cont is just the index so we can access the weight values
                        new_left = left_weight - int(sampleJson[left_cont]["weight"])
                        new_right = right_weight + int(sampleJson[left_cont]["weight"])
                        if new_left == 0:
                            curr_balance = 1/new_right
                        elif new_right == 0:
                            curr_balance = new_left/1
                        else:
                            curr_balance = new_left/new_right
                        if curr_balance < 1.1 and curr_balance > 0.9:
                            #MOVE left_cont to nearest rightside spot CODE MUST BREAK HERE SINCE WE BALANCED THE SHIP
                            dest_y, dest_x = ifRightEmpty(sampleJson)
                            if dest_y != -1 and dest_x != -1:
                                move(i, j, dest_y, dest_x, sampleJson)
                                return #BREAK SINCE WE BALANCED THE CODE
                        else:
                            if abs(curr_balance-1) < abs(best_balance-1):
                                best_balance = curr_balance
                                best_y, best_x = i, j
                
                #If we made it here in our code that means that no move balanced the ship, so we will make the best move we can currently make.
                #MOVE best_index to the nearest rightside spot, and continue the while loop.
                dest_y, dest_x = ifRightEmpty(sampleJson)
                if dest_y != -1 and dest_x != -1:
                    # print("Left to Right:", best_y, best_x, dest_y, dest_x)
                    move(best_y, best_x, dest_y, dest_x, sampleJson)
                
            if balance_ratio < .9: #Right side is heavier we need to move something from here to left side.
                
                for i in range(8,0,-1):
                    for j in range(7,13):
                        right_cont = makeIndex(i,j)
                        new_right = right_weight - int(sampleJson[right_cont]["weight"])
                        new_left = left_weight + int(sampleJson[right_cont]["weight"])
                        if new_left == 0:
                            curr_balance = 1/new_right
                        elif new_right == 0:
                            curr_balance = new_left/1
                        else:
                            curr_balance = new_left/new_right
                        if curr_balance < 1.1 and curr_balance > 0.9:
                            #Move right_cont to nearest leftside spot CODE MUST BREAK HERE SINCE WE BALANACED THE SHIP
                            dest_y, dest_x = ifLeftEmpty(sampleJson)
                            if dest_y != -1 and dest_x != -1:
                                move(i, j, dest_y, dest_x, sampleJson)
                                return #BREAK SINCE WE BALANCED THE CODE
                        else:
                            if abs(curr_balance-1) < abs(best_balance-1):
                                best_balance = curr_balance
                                best_y, best_x = i,j
                                
                #If we made it here in our code that means that no move balanced the ship, so we will make the best move we can currently make.
                #Move best_index to the nearest leftside spot, and continue the while loop.
                dest_y, dest_x = ifLeftEmpty(sampleJson)
                if dest_y != -1 and dest_x != -1:
                    # print("Right to Left:", best_y, best_x, dest_y, dest_x)
                    move(best_y, best_x, dest_y, dest_x, sampleJson)
                
            #After making some sort of change by either doing the right and left movement, we need to recalculate balance_ratio.
            left_weight = getLeftWeight(sampleJson)
            right_weight = getRightWeight(sampleJson)
            balance_ratio = left_weight/right_weight
            # print(left_weight, right_weight, balance_ratio)
    #----------------------------------------------------------balance() ends here--------------------------------------------------------------#

    def sift(sampleJson):                                                   # Sift is only done when the ship is not balanceable
        # moves = 0                                   
        # move_Dict = {}
        # tot_distance = 0
        sorted_array = []                                                   # To figure out which containers are heaviest to lightest
        for i in range(8):                                                  # Grabs all containers with weight to sort
            for j in range(12): 
                index = makeIndex(i+1,j+1)
                if sampleJson[index]["weight"] != "00000":
                    entry = (int(sampleJson[index]["weight"]), sampleJson[index]["description"], i+1, j+1)
                    sorted_array.append(entry)
        sorted_array.sort(key = lambda x: x[0], reverse=True)

        # Flag_x tells us if we need to place to the left or to the right, with help of column and rebound to go from 6 to 7, then to 5, then 8, etc, with a "rebounding" motion
        # When a column is completely filled, go up a row, and reset rebound to 0
        flag_x = 0
        column = 6
        row = 1
        rebound = 0

        for i in range(len(sorted_array)):                              # For all containers with weight in the manifest
            if checkDesc(row, column, sampleJson) != "UNUSED" and checkDesc(row, column, sampleJson) != "NAN": # CANNOT MOVE CONTAINER TO NAN 
                if checkDesc(row, column, sampleJson) != sorted_array[i][1]: # Don't move a container if it's already where it should be
                    move_blocking_container_to_y = 0                         # This case handles moving to the optimal spot if there is another container in the way
                    move_blocking_container_to_x = 0
                    if flag_x == 0:
                        move_blocking_container_to_y, move_blocking_container_to_x = findFirstLeftCol(row, column, sampleJson)
                    else: # if flag == 1
                        move_blocking_container_to_y, move_blocking_container_to_x = findFirstRightCol(row, column, sampleJson)
                    move(row, column, move_blocking_container_to_y, move_blocking_container_to_x, sampleJson, 0)
                    move(sorted_array[i][2], sorted_array[i][3], row, column, sampleJson, 0)
            elif (checkDesc(row, column, sampleJson) == "UNUSED"):          # If there is no container at optimal spot, no moveout needed
                    move(sorted_array[i][2], sorted_array[i][3], row, column, sampleJson, 0)
            else:
                i -= 1

            sorted_array = []                                               # Resort array to update positions with potential changes
            for it in range(8):
                for j in range(12):
                    index = makeIndex(it+1,j+1)
                    if sampleJson[index]["weight"] != "00000":
                        entry = (int(sampleJson[index]["weight"]), sampleJson[index]["description"], it+1, j+1)
                        sorted_array.append(entry)
            sorted_array.sort(key = lambda x: (x[0], x[1]), reverse=True)

            if flag_x == 0:                                                 # First move to the right
                flag_x = 1
                column = column + rebound + 1
            else:
                flag_x = 0                                                  # Then move back to the left, one more position away from last container
                column = column - rebound - 1
            if column == 0 or column == 12:                                 # Reset rebound if column is filled, and go up a row
                column = 6
                row += 1
                rebound = 0
            rebound = rebound + 1
                
    #----------------------------------------------------------Helper-Functions-----------------------------------------------------------------#
    def makeIndex(y, x):
        if y > 9:   # If the index if greater than 9, then we format as a double digit instead of appending a 0 to the end
            if x > 9: # Same situation as y
                index = "["+ str(y) + "," + str(x) + "]"
            else:
                index = "["+ str(y) + ",0" + str(x) + "]"
        else:
            if x > 9:
                index = "[0"+ str(y) + "," + str(x) + "]"
            else:
                index = "[0"+ str(y) + ",0" + str(x) + "]"
        return index

    def checkDesc(y, x, sampleJson): #This function will take the y and x as well as the Json we are operating on and check the description of the package
        index = makeIndex(y,x) 
        return sampleJson[index]["description"]

    def ifLeftEmpty(sampleJson): # This function needs to be workshopped into finding the nearest empty space TO FIX
        for i in range(6,0,1):
            for j in range(1,9):
                index = makeIndex(j,i)
                if checkDesc(j,i,sampleJson) == "UNUSED":
                    return j,i
        return -1, -1

    def ifRightEmpty(sampleJson): # This function needs to be workshopped into finding the nearest empty space TO FIX
        for i in range(7,13):
            for j in range(1,9):
                index = makeIndex(j,i)
                if checkDesc(j,i,sampleJson) == "UNUSED":
                    return j, i
        return -1, -1

    def getLeftWeight(sampleJson): #This function will return as a int the entire weight of the left hand side.
        total = 0
        for i in range(8): #Height
            for j in range(6):
                index = makeIndex(i+1,j+1)
                total += int(sampleJson[index]["weight"])
        return total

    def getRightWeight(sampleJson): #This function will return as a int the entire weight of the right hand side.
        total = 0
        for i in range(8): #Height
            for j in range(6):
                index = makeIndex(i+1,j+7)
                total += int(sampleJson[index]["weight"])
                
        return total

    def getWeights(sampleJson): #This function will return 5 values, int right_weight, int left_weight, int maxWeight, string max_Index, int total, and string heavy.
        total = 0
        maxWeight = 0
        max_Index = ""
        isBalanced = False
        right_weight = getRightWeight(sampleJson)
        left_weight = getLeftWeight(sampleJson)
        
        for i in range(8):
            for j in range(12):
                index = makeIndex(i+1,j+1)
                currWeight = int(sampleJson[index]["weight"])
                total += currWeight
                if currWeight > maxWeight:
                    maxWeight = currWeight
                    max_Index = index
                    
        
        if left_weight == 0 and right_weight == 0:
            isBalanced = True
        elif left_weight == 0 or right_weight == 0:
            isBalanced = False
        elif left_weight/right_weight < 1.1 and left_weight/right_weight > .9:
            isBalanced = True
        
        return right_weight, left_weight, maxWeight, max_Index, isBalanced, total


    #-----------------------------------------------------Move Functions---------------------------------------------------------------------#
                
    def move(start_y, start_x, dest_y, dest_x, sampleJson, flag=0):
        
        clearPath(start_y, start_x, sampleJson) #This function will ensure we only move a container once all containers above it are gone
        
        if flag == 1: # This is for when we move containers to the nearest unused spot, since it can change while in clearPath, we must reassess what is the nearestUnused spot
            dest_y, dest_x = findNearestUnused(start_y, start_x, sampleJson)
            move(start_y, start_x, dest_y, dest_x, sampleJson)
            return
        
        start_index = makeIndex(start_y, start_x)
        goal_index = makeIndex(dest_y, dest_x)
        start_Weight = sampleJson[start_index]["weight"]
        start_Desc = checkDesc(start_y, start_x, sampleJson)
        
        distance = abs(start_y-dest_y) + abs(start_x-dest_x)
        nonlocal tot_distance
        tot_distance += distance
        nonlocal moves
        moves += 1
        nonlocal move_Dict
        move_Dict[str(moves)] = {}
        move_Dict[str(moves)]["origin"] = start_index
        move_Dict[str(moves)]["destination"] = goal_index
        
        #We only move to UNUSED containers, so by swapping it simulates the movement perfectly
        sampleJson[start_index]["weight"] = sampleJson[goal_index]["weight"]
        sampleJson[start_index]["description"] = sampleJson[goal_index]["description"]
        
        sampleJson[goal_index]["weight"] = start_Weight
        sampleJson[goal_index]["description"] = start_Desc
        

    def clearPath(y, x, sampleJson):                                # Will move containers above our start container if nessessary-
        if y < 8:
            if checkDesc(y+1,x,sampleJson) != "UNUSED":       # URGENT: Check if y != 8 before checkDesc
                dest_y, dest_x = findNearestUnused(y+1, x, sampleJson)
                move(y+1, x, dest_y, dest_x, sampleJson, 1)

    def findNearestUnused(y,x,sampleJson):                          # Finds nearest column to move blocking containers to
        if x < 7:                                                   # If container is on the left half, we ideally want to move it left
            if x == 1:                                              # Leftmost column can't move more left
                return findFirstRightCol(y, x, sampleJson)
            else:       
                dest_y, dest_x = findFirstLeftCol(y, x, sampleJson) # If no space on left, then search to the right
                if dest_y == -1 and dest_x == -1:
                    return findFirstRightCol(y, x, sampleJson)
                else:
                    return dest_y, dest_x
        else:                                                       # Containers on right half want to go more right
            if x == 12:                                             # Rightmost container can't move more right
                return findFirstLeftCol(y, x, sampleJson)           
            else:                                                   # If no space on right, then search to the left
                dest_y, dest_x = findFirstRightCol(y, x, sampleJson)
                if dest_y == -1 and dest_x == -1:
                    return findFirstLeftCol(y, x, sampleJson)
                else:
                    return dest_y, dest_x
                
    def findFirstRightCol(y, x, sampleJson):                        # Returns y and x coordinate if there is a space available
        for i in range(x+1, 7):                                     # in the columns to the right, else, return (-1, -1) to go left
            for j in range(8):
                if checkDesc(j+1, i, sampleJson) == "UNUSED":
                    return j+1, i
            return -1, -1

    def findFirstLeftCol(y, x, sampleJson):                         # Returns y and x coordinate if there is a space available 
        for i in range(x-1, 0, -1):                                 # in the columns to the left, else, return (-1, -1) to go right 
            for j in range(8):
                if checkDesc(j+1, i, sampleJson) == "UNUSED":
                    return j+1, i
        return -1, -1
        

    #-----------------------------------------------------MAIN CODE---------------------------------------------------------------------------#
    #Pass Json here
    sampleJson = req

    balance(sampleJson)

    print("moveDict")
    print(move_Dict)

    move_Dict["time"] = tot_distance

    res = make_response(jsonify(move_Dict), 200)

    return res

# Where the manifest json is sent in correct format, needing to be balanced
@app.route("/operationsAlgorithm", methods=["POST"])
def operationsAlgorithm():
    # This is where we can implement the python coding for algorithm
    req = request.get_json()
    # print("Printing JSON of changes to be made in operationsAlgo")
    # print(req)

    # ADD load/unload FUNCTION HERE

    moves = 0
    move_Dict = {}
    tot_distance = 0        
            
    #------------------------------------------------------Helper Functions------------------------------------------------------------#
    def move(start_y, start_x, dest_y, dest_x, sampleJson, flag=0):
        
        clearPath(start_y, start_x, sampleJson) #This function will ensure we only move a container once all containers above it are gone
        
        if flag == 1: # This is for when we move containers to the nearest unused spot, since it can change while in clearPath, we must reassess what is the nearestUnused spot
            dest_y, dest_x = findNearestUnused(start_y, start_x, sampleJson)
            move(start_y, start_x, dest_y, dest_x, sampleJson)
            return
        
        start_index = makeIndex(start_y, start_x)
        goal_index = makeIndex(dest_y, dest_x)
        start_Weight = sampleJson[start_index]["weight"]
        start_Desc = checkDesc(start_y, start_x, sampleJson)
        
        distance = abs(start_y-dest_y) + abs(start_x-dest_x)
        nonlocal tot_distance
        tot_distance += distance
        nonlocal moves
        moves += 1
        nonlocal move_Dict
        move_Dict[str(moves)] = {}
        move_Dict[str(moves)]["origin"] = start_index
        move_Dict[str(moves)]["destination"] = goal_index
        move_Dict[str(moves)]["condition"] = 0
        
        #We only move to UNUSED containers, so by swapping it simulates the movement perfectly
        sampleJson[start_index]["weight"] = sampleJson[goal_index]["weight"]
        sampleJson[start_index]["description"] = sampleJson[goal_index]["description"]
        
        sampleJson[goal_index]["weight"] = start_Weight
        sampleJson[goal_index]["description"] = start_Desc
        

    def clearPath(y, x, sampleJson):                                # Will move containers above our start container if nessessary-
        if y < 8:
            if checkDesc(y+1,x,sampleJson) != "UNUSED":       # URGENT: Check if y != 8 before checkDesc
                dest_y, dest_x = findNearestUnused(y+1, x, sampleJson)
                move(y+1, x, dest_y, dest_x, sampleJson, 1)

    def findNearestUnused(y,x,sampleJson):                          # Finds nearest column to move blocking containers to
        if x < 7:                                                   # If container is on the left half, we ideally want to move it left
            if x == 1:                                              # Leftmost column can't move more left
                return findFirstRightCol(y, x, sampleJson)
            else:       
                dest_y, dest_x = findFirstLeftCol(y, x, sampleJson) # If no space on left, then search to the right
                if dest_y == -1 and dest_x == -1:
                    return findFirstRightCol(y, x, sampleJson)
                else:
                    return dest_y, dest_x
        else:                                                       # Containers on right half want to go more right
            if x == 12:                                             # Rightmost container can't move more right
                return findFirstLeftCol(y, x, sampleJson)           
            else:                                                   # If no space on right, then search to the left
                dest_y, dest_x = findFirstRightCol(y, x, sampleJson)
                if dest_y == -1 and dest_x == -1:
                    return findFirstLeftCol(y, x, sampleJson)
                else:
                    return dest_y, dest_x
                
    def findFirstRightCol(y, x, sampleJson):                        # Returns y and x coordinate if there is a space available
        for i in range(x+1, 7):                                     # in the columns to the right, else, return (-1, -1) to go left
            for j in range(8):
                if checkDesc(j+1, i, sampleJson) == "UNUSED":
                    # print(j+1, i)
                    return j+1, i
            return -1, -1

    def findFirstLeftCol(y, x, sampleJson):                         # Returns y and x coordinate if there is a space available 
        for i in range(x-1, 0, -1):                                 # in the columns to the left, else, return (-1, -1) to go right 
            for j in range(8):
                if checkDesc(j+1, i, sampleJson) == "UNUSED":
                    # print(j+1, i)
                    return j+1, i
        return -1, -1

    def makeIndex(y, x):
        if y > 9:   # If the index if greater than 9, then we format as a double digit instead of appending a 0 to the end
            if x > 9: # Same situation as y
                index = "["+ str(y) + "," + str(x) + "]"
            else:
                index = "["+ str(y) + ",0" + str(x) + "]"
        else:
            if x > 9:
                index = "[0"+ str(y) + "," + str(x) + "]"
            else:
                index = "[0"+ str(y) + ",0" + str(x) + "]"
        return index

    def checkDesc(y, x, sampleJson): #This function will take the y and x as well as the Json we are operating on and check the description of the package
        index = makeIndex(y,x) 
        return sampleJson[index]["description"]

    def ifLeftEmpty(sampleJson): # This function needs to be workshopped into finding the nearest empty space TO FIX
        for i in range(8):
            for j in range(6,0,-1):
                index = makeIndex(i+1,j)
                if checkDesc(i+1,j,sampleJson) == "UNUSED":
                    return i+1, j
        return -1, -1

    def ifRightEmpty(sampleJson): # This function needs to be workshopped into finding the nearest empty space TO FIX
        for i in range(8):
            for j in range(7,13):
                index = makeIndex(i+1,j)
                if checkDesc(i+1,j,sampleJson) == "UNUSED":
                    return i+1, j
        return -1, -1

    def getLeftWeight(sampleJson): #This function will return as a int the entire weight of the left hand side.
        total = 0
        for i in range(8): #Height
            for j in range(6):
                index = makeIndex(i+1,j+1)
                total += int(sampleJson[index]["weight"])
        return total

    def getRightWeight(sampleJson): #This function will return as a int the entire weight of the right hand side.
        total = 0
        for i in range(8): #Height
            for j in range(6):
                index = makeIndex(i+1,j+7)
                total += int(sampleJson[index]["weight"])
                
        return total

    def getWeights(sampleJson): #This function will return 5 values, int right_weight, int left_weight, int maxWeight, string max_Index, int total, and string heavy.
        total = 0
        maxWeight = 0
        max_Index = ""
        isBalanced = False
        right_weight = getRightWeight(sampleJson)
        left_weight = getLeftWeight(sampleJson)
        
        for i in range(8):
            for j in range(12):
                index = makeIndex(i+1,j+1)
                currWeight = int(sampleJson[index]["weight"])
                total += currWeight
                if currWeight > maxWeight:
                    maxWeight = currWeight
                    max_Index = index
                    
        
        if left_weight == 0 and right_weight == 0:
            isBalanced = True
        elif left_weight == 0 or right_weight == 0:
            isBalanced = False
        elif left_weight/right_weight < 1.1 and left_weight/right_weight > .9:
            isBalanced = True
        
        return right_weight, left_weight, maxWeight, max_Index, isBalanced, total


    #-----------------------------------------------------------------------MAIN CODE--------------------------------------------------------------------------------#
    # with open('./loadUnloadTest3.json', 'r') as f:
    #     operations_dict = json.load(f)
    operations_dict = req

    #operations_dict has on layer 1: manifest, or changes. Manifest = sampleJson and operations_dict is changes
    for i in operations_dict["changes"]:
        index = i
        final_loc = makeIndex(8,1)
        y, x = int(index[1:3]), int(index[4:6])
        if operations_dict["changes"][i]["loadUnload"] == 2: #Unload 
            move(y,x,8,1,operations_dict["manifest"])
            move_Dict[str(moves)]["condition"] = 2
            move_Dict[str(moves)]["destination"] = i
            move_Dict[str(moves)]["origin"] = "NAN"
            operations_dict["manifest"][final_loc]["weight"] = "00000"
            operations_dict["manifest"][final_loc]["description"] = "UNUSED"
            tot_distance += 3
        else: #Load
            tot_distance += abs(8-y) + abs(1-x) + 3
            operations_dict["manifest"][i]["weight"] = "00000"
            operations_dict["manifest"][i]["description"] = "NEWCONTAINER"
            moves += 1
            move_Dict[str(moves)] = {}
            move_Dict[str(moves)]["origin"] = "NAN"
            move_Dict[str(moves)]["destination"] = i
            move_Dict[str(moves)]["condition"] = 1
            
    # print(operations_dict["manifest"])
    # print(move_Dict)

    move_Dict["time"] = tot_distance

    res = make_response(jsonify(move_Dict), 200)

    return res

@app.route("/exportManifest", methods=['POST'])
def exportManifest():
    # print(request)
    req = request.get_json()
    # print("Printing JSON of new Manifest")
    # print(req)

    # manifestDirPath = easygui.diropenbox(msg="Select where you would like to download the new manifest")                                            # Prompts the user with the file explorer to choose a manifest

    global manifestFilePath
    basename = os.path.basename(manifestFilePath)
    
    # today = date.today()
    # today_formated = today.strftime("%b-%d-%Y")
    # time = datetime.now()
    # currTime = time.strftime("%H %M")
            
    with open("OutboundManifests/Outbound " + basename, "a") as f:
        for key, file_dir in sorted(list(req.items()), key=lambda x:x[0].lower(), reverse=False):
            f.write(key + ", {" + file_dir["weight"] + "}, " + file_dir["description"] + "\n")
        f.close()

    # print("redirecting")
    return redirect(url_for('home'))
    # # res = make_response(jsonify(req), 200)

    # return res

@app.route("/commentLog", methods=['POST'])
def commentLog():
    req = request.get_json()
    print(req)
    
    today = date.today()
    today_formated = today.strftime("%b-%d-%Y")
    time = datetime.now()
    currTime = time.strftime("%H:%M:%S")
    
    with open("CommentLog/comments.txt", "a") as f:
        f.write("[" + today_formated + "] " + currTime + "\n" + req + "\n\n")
        f.close()

    return "whats good"

@app.route("/stepSaveOperations", methods=['POST'])
def stepSaveOperations():
    req = request.get_json()
    print(req)
    
    today = date.today()
    today_formated = today.strftime("%b-%d-%Y")
    time = datetime.now()
    currTime = time.strftime("%H:%M:%S")
    
    with open("CurrentSave/currentSave.txt", "a") as f:
        if req["condition"] == 0:
            f.write("[" + today_formated + "] " + currTime + "\n" + "Container was moved from " + req["origin"] + " to " + req["destination"] + "\n\n")
        elif req["condition"] == 1:
            f.write("[" + today_formated + "] " + currTime + "\n" + "Container was loaded into " + req["destination"] + "\n\n")
        elif req["condition"] == 2:
            f.write("[" + today_formated + "] " + currTime + "\n" + "Container was unloaded from " + req["destination"] + "\n\n")
        f.close()

    return "whats good"

@app.route("/stepSaveBalance", methods=['POST'])
def stepSaveBalance():
    req = request.get_json()
    print(req)
    
    today = date.today()
    today_formated = today.strftime("%b-%d-%Y")
    time = datetime.now()
    currTime = time.strftime("%H:%M:%S")
    
    with open("CurrentSave/currentSave.txt", "a") as f:        
        f.write("[" + today_formated + "] " + currTime + "\n" + "Container was moved from " + req["origin"] + " to " + req["destination"] + "\n\n")
        f.close()

    return "whats good"

