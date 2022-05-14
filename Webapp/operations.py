import json
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
    global tot_distance
    tot_distance += distance
    global moves
    moves += 1
    global move_Dict
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
                print(j+1, i)
                return j+1, i
        return -1, -1

def findFirstLeftCol(y, x, sampleJson):                         # Returns y and x coordinate if there is a space available 
    for i in range(x-1, 0, -1):                                 # in the columns to the left, else, return (-1, -1) to go right 
        for j in range(8):
            if checkDesc(j+1, i, sampleJson) == "UNUSED":
                print(j+1, i)
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
with open('./loadUnloadTest3.json', 'r') as f:
    operations_dict = json.load(f)

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
        
print(operations_dict["manifest"])
print(move_Dict)