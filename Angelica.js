var prompt = require('prompt-sync')();
const cloneDeep = require('lodash.clonedeep')

A = [['A', 'N', 'G'], 
    ['E', 'L', 'I'],  // 0
    ['C', 'A', '.']]

B = [['A', 'N', 'G'], 
    ['E', '.', 'I'],  // 2
    ['C', 'L', 'A']]

C = [['A', 'N', 'G'], 
    ['L', '.', 'I'],  // 4
    ['E', 'C', 'A']]

D = [['A', 'G', 'I'], 
    ['L', '.', 'N'],  // 8
    ['E', 'C', 'A']]

E = [['A', 'G', 'I'], 
    ['L', '.', 'C'],  // 12
    ['E', 'A', 'N']]

F = [['A', 'I', 'C'], 
    ['L', '.', 'G'],  // 16
    ['E', 'A', 'N']]

G = [['C', 'A', 'N'], 
    ['E', 'A', 'L'],  // 20
    ['I', 'G', '.']]

H = [['.', 'C', 'N'], 
    ['E', 'I', 'A'],  // 24
    ['G', 'L', 'A']]

I = [['A', 'I', 'C'], 
    ['N', 'L', 'E'],  // 31
    ['G', '.', 'A']]

DEFAULT_PUZZLE = B

duplicates = []
maxQueueLength = 0

class Problem {
    constructor(initialState) {
        this.initialState = initialState
        this.dimension = initialState[0].length
        this.operators = [[-1,0], [1, 0], [0,-1], [0,1]]
        this.goalState = [['A', 'N', 'G'], 
                         ['E', 'L', 'I'],
                         ['C', 'A', '.']]
    }

    printBoard() {
        for (let i = 0; i < this.dimension; i++) {
            for (let j = 0; j < this.dimension; j++) {
                process.stdout.write(this.initialState[i][j] + ' ');                                
            }
            console.log('');
        }
    }

    goalTest(currState) {
        if (JSON.stringify(currState) == JSON.stringify(this.goalState)) {
            return true;
        }
        else {
            return false;
        }
    }
}


class Node {
    constructor(initialState) {
        this.goalState = [['A', 'N', 'G'], 
                         ['E', 'L', 'I'],
                         ['C', 'A', '.']]
        this.state = initialState
        this.dimension = initialState[0].length
        this.g = 0                                  
        this.h = 0                                  
        this.f = 0
    }

    printBoard() {
        console.log('g: ' + this.g);
        console.log('h: ' + this.h);
        console.log('f: ' + this.f);
        for (let i = 0; i < this.dimension; i++) {
            for (let j = 0; j < this.dimension; j++) {
                process.stdout.write(this.state[i][j] + ' ');
            }
            console.log('');
        }
    }

    calcF() {
        this.f = this.h + this.g;
    }

    misplacedTile() {
        let hVal = 0;

        // for every tile not matching the goal state, increment hVal
        for (let i = 0; i < this.dimension; i++) {
            for (let j = 0; j < this.dimension; j++) {
                if (this.state[i][j] != this.goalState[i][j]) {
                    hVal = hVal + 1;
                }
            }
        }
        // since the heuristic is not supposed to contain the blank space, decrease it by one in the end
        this.h = hVal - 1
    }

    manhattanDistance() {
        let hVal = 0;

        for (let i = 0; i < this.dimension; i++) {
            for (let j = 0; j < this.dimension; j++) {
                if ((this.state[i][j] != this.goalState[i][j]) && (this.state[i][j] != ".")) {
                    // goatLocation is the location on the goalstate of the number we have
                    let goalLocation = findChar(this.goalState, this.state[i][j]);

                    // Subtract self.state[i][j] - goalLocation
                    let difference = [i - goalLocation[0], j - goalLocation[1]]

                    // abs value of difference list
                    difference[0] = Math.abs(difference[0])
                    difference[1] = Math.abs(difference[1])

                    // add both list items together
                    hVal = hVal + (difference[0] + difference[1])
                }
            }
        }
        this.h = hVal;
    }
}

// NodeQueue object, contains a queue of nodes
// printBoard() prints all of the nodes in the queue
// concat() updates the queue to be the concatenation of it with the new list of nodes
class NodeQueue {
    constructor(initialNode) {
        this.queue = [];
        this.queue.push(initialNode);
    }

    printBoard() {
        console.log('g: ' + this.g);
        console.log('h: ' + this.h);
        console.log('f: ' + this.f);
        for (let i = 0; i < this.dimension; i++) {
            for (let j = 0; j < this.dimension; j++) {
                process.stdout.write(this.initialState[i][j] + ' ');                                
            }
            console.log('');
        }
    }

    concat(newNodes) {
        let concatenation = newNodes.concat(this.queue);
        this.queue = concatenation;
    }
}

function maxQueue(length) {
    if (length > maxQueueLength) {
        maxQueueLength = length;
    }
}

function findChar(state, char) {
    let listNum = 0;
    let indexNum = 0;
    for (let i = 0; i < state.length; i++) {
        for (let j = 0; j < state[i].length; j++) {
            if (state[i][j] == char) {
                return [listNum, indexNum]
            }
            indexNum = indexNum + 1;
        }
        listNum = listNum + 1;
        indexNum = 0;
    }
}

// expand function returns a list of all of the possible legal child expansions of the node passed in
function expand(node, operators) {
    // calculates the furthest index of the list
    max = node.dimension - 1;

    // children will be the list of nodes that is returned
    children = [];

    // swaps will contain all of the coordinate locations of the legal moves
    swaps = [];

    // blankLocation is a list of 2 integers which show the locations of the blank space
    blankLocation = findChar(node.state, '.');

    //operators are all of the legal moves the blank could make (up, down, left, and right)
    for (let i = 0; i < operators.length; i++) {
        x = blankLocation[0] - operators[i][0]
        y = blankLocation[1] - operators[i][1]
        
        // checks if the calculated move is on the game board
        if ((((x >= 0) && (x <= max)) && ((y >= 0) && (y <= max)))) {
            // if it is a legal move, the move's coordinates are added to swaps
            swaps.push([x,y])
        }
    }

    // for every new location the . can go to
    for (let i = 0; i < swaps.length; i++) {
        // creates a copy of the passed in node
        child = cloneDeep(node)

        // increments depth because it is a new child node
        child.g = child.g + 1;

        // swaps the value on the game board with the blank
        tempVal = child.state[swaps[i][0]][swaps[i][1]]
        child.state[swaps[i][0]][swaps[i][1]] = '.'
        child.state[blankLocation[0]][blankLocation[1]] = tempVal

        // child node is appended to the list of new children
        children.push(child)
    }
    return children;
}


function queueingFunction(flag, prevNodes, newNodes) {
    for (let i = 0; i < newNodes.length; i++) {
        let dup = false
        for (let j = 0; j < duplicates.length; j++) {           
            if (JSON.stringify(newNodes[i].state) === JSON.stringify(duplicates[j])) {
                dup = true
            }
        }
        if (dup) {
            newNodes.splice(i, 1);
        }
        else {
            duplicates.push(newNodes[i].state)
        }
        // if (newNodes[i].state in duplicates) {
        //     newNodes.splice(i, 1);
        // }
        // else {
        //     duplicates.push(newNodes[i].state);
        // }
    }
    if (flag == 1) {
        prevNodes.concat(newNodes);
        return prevNodes;
    }
    else if (flag == 2) {
        for (let i = 0; i < newNodes.length; i++) {
            newNodes[i].misplacedTile();
            newNodes[i].calcF()
        }
        prevNodes.concat(newNodes)

        console.log(typeof prevNodes.queue)
        // prevNodes.queue.sort();
        prevNodes.queue.sort(function(a, b) {
            return b.f - a.f;
        })
        // prevNodes.queue.reverse();

        winnerF = prevNodes.queue[prevNodes.queue.length - 1].f

        tieBreakers = []
        // for (i in prevNodes.queue.reverse()) {
        //     if (i.f == winnerF) {
        //         tieBreakers.push(prevNodes.queue.pop())
        //     }
        //     else {
        //         break;
        //     }
        // }

        for (let i = prevNodes.queue.length - 1; i > 0; i--) {
            if (prevNodes.queue[i].f == winnerF) {
                tieBreakers.push(prevNodes.queue.pop())
            }
            else {
                break;
            }
        }

        tieBreakers.sort();
        tieBreakers.reverse();

        prevNodes.queue = prevNodes.queue.concat(tieBreakers)
        return prevNodes
    }
    else if (flag == 3) {
        for (let i = 0; i < newNodes.length; i++) {
            newNodes[i].manhattanDistance()
            newNodes[i].calcF()
        }
        prevNodes.concat(newNodes);
        // prevNodes.sort();
        prevNodes.queue.sort(function(a, b) {
            return b.f - a.f;
        })
        // prevNodes.reverse();

        winnerF = prevNodes.queue[prevNodes.queue.length - 1].f
        // winnerF = prevNodes.queue[-1].f

        tieBreakers = []
        // for (i in prevNodes.queue.reverse()) {
        //     if (i.f == winnerF) {
        //         tieBreakers.push(prevNodes.queue.pop())
        //     }
        //     else {
        //         break;
        //     }
        // }
        for (let i = prevNodes.queue.length - 1; i > 0; i--) {
            if (prevNodes.queue[i].f == winnerF) {
                tieBreakers.push(prevNodes.queue.pop())
            }
            else {
                break;
            }
        }
        tieBreakers.sort()
        tieBreakers.reverse()
        // prevNodes.queue = prevNodes.queue + tieBreakers
        prevNodes.queue = prevNodes.queue.concat(tieBreakers)

        return prevNodes
    }
}

function generalSearch(problem, queueingFunctionFlag) {
    // Create root node with the problem state
    rootNode = new Node(problem.initialState);
    console.log("rootNode: " + rootNode.state);

    // Create a queue of Nodes, initialized with the root node
    nodes = new NodeQueue(rootNode);

    // x keeps track of the iterations
    let x = 0;

    // loops while the nodes list is not empty
    while (nodes.queue.length > 0) {
        // pops the top of the queue off and uses that as the current node, this node is also the most efficient
        currNode = nodes.queue.pop();
        console.log("currNode:");
        currNode.printBoard();
        
        // checks the current node's state, enters conditional if it is the goal state
        if (problem.goalTest(currNode.state)) {
            console.log("Found the goal state!");
            console.log("iteration: " + x);
            return currNode;
        }
        
        // console.log(typeof nodes.queue);
        // calls the queueing function, passes in the flag for the type of queueing function, the original nodes,
        // and the expanded children. The expand function uses the current node and the problem operators
        nodes = queueingFunction(queueingFunctionFlag, nodes, expand(currNode, problem.operators));

        maxQueue(nodes.queue.length)

        x = x + 1
    }
    return false
}
  
function userInput() {
    console.log("Welcome to Luccap's Angelica puzzle solver. Type “1” to use a premade puzzle, or “2” to enter your own puzzle.");
    var puzzleSelection = prompt();
    // puzzleSelection = 1;

    if (puzzleSelection == 1) {
        console.log("\nEnter your choice of algorithm:\n1. Uniform Cost Search\n2. A* with the Misplaced Tile heuristic\n3. A* with the Manhattan distance heuristic");
        var algoChoice = prompt();
        // algoChoice = 2;
        console.log("");

        // Creates the Problem object by passing in the default game board
        problem = new Problem(DEFAULT_PUZZLE)

        // Adds the first state to the list of duplicates
        duplicates = [problem.initialState]

        // Starts program timer
        let t0 = Date.now();

        // Runs general search algorithm and returns the result node/boolean
        Result = generalSearch(problem, algoChoice)

        // Ends program timer
        let t1 = Date.now();
        
        // Calculate time elapsed
        totalTime = t1-t0
        console.log("Time elapsed: " + totalTime + " milliseconds")
        return Result
    }
    else if (puzzleSelection == 2) {
        console.log("Enter your puzzle");
        console.log("Enter your first row, use space between letters");
        firstRow = prompt();
        console.log("Enter the second row, use space between letters");
        secondRow = prompt();
        console.log("Enter the third row, use space between letters");
        thirdRow = prompt();

        // # Take string inputs, split them into strings, and then map the strings to ints, finally putting them all in a list
        // x = [list(map(int, firstRow.split())), list(map(int, secondRow.split())), list(map(int, thirdRow.split()))]
        // Problem = Problem(x)
        // duplicates = [Problem.initialState]
        
        // algoChoice = input("Enter your choice of algorithm:\n1. Uniform Cost Search\n2. A* with the Misplaced Tile heuristic\n3. A* with the Manhattan distance heuristic\n")
        
        // t0 = time.time()
        // Result = generalSearch(Problem, int(algoChoice))
        // t1 = time.time()
        // totalTime = t1-t0
        // print("Time elapsed: " + str(totalTime) + " seconds")
        // return Result
    }




    return Problem
}



Result = userInput()
console.log(Result);
Result.printBoard();
console.log("Result.depth: " + Result.g);
console.log("Max Queue Length: " + maxQueueLength);
// if (Result == false) {
//     console.log("Failed to find a solution");
// }
// else {
//     Result.printBoard()
//     console.log("Result.depth: " + Result.g);
//     console.log("Max Queue Length: " + maxQueueLength);
// }

