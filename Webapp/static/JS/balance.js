// This is the change list json object to be filled and sent to the backend
var changeList = new Object();

// Getting all of the container div elements
const containerButtonArr = document.getElementsByClassName("containerButtonContainer");

for (var i = 0; i < containerButtonArr.length; i++) {
    // console.log(containerButtonArr[i].children[0].id);
    if (containerButtonArr[i].children[0].children[2].textContent == "NAN") {
        containerButtonArr[i].children[0].style.backgroundColor = "rgb(105, 105, 105)";
    }
    else if(containerButtonArr[i].children[0].children[2].textContent !== "UNUSED") {
        containerButtonArr[i].children[0].style.backgroundColor = "lightgreen";
    }
}

// Getting the div element of the "begin balancing" submit button
const beginBalanceButton = document.getElementById("inputSubmitButton");

// Checking for when someone clicks on either of the mode changing buttons
// Checking if someone clicks on the button and then forwarding it to next and Submit
beginBalanceButton.addEventListener("click", nextAndSubmit);

function nextAndSubmit(ev) {
    ev.preventDefault();

    // Goes through all of the containers and formats them in a JSON object for algorithm
    for (let i = 0; i < containerButtonArr.length; i++) {
        var containerPosition = containerButtonArr[i].children[0].id;
        var containerWeight = containerButtonArr[i].children[0].children[1].textContent;
        var containerDescription = containerButtonArr[i].children[0].children[2].textContent;

        var obj = new Object();
        // obj.position = containerPosition;
        obj.weight = containerWeight.slice(1, -1);
        obj.description = containerDescription;

        changeList[containerPosition] = obj;        
    }

    // The changeList is now formatted and able to be sent to the backend to balance!
    console.log(changeList);
    var changeListJson = JSON.stringify(changeList);
    console.log(changeListJson);

    fetch(urlForAlgo, {
        method: 'POST',
        credentials: "include",
        body: changeListJson,
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(function(response) {
        if (response.status !== 200) {
          console.log(`Looks like there was a problem. Status code: ${response.status}`);
          return;
        }
        response.json().then(function(data) {
          console.log(data);
          displayBalancing(data);
        });
      })
      .catch(function(error) {
        console.log("Fetch error: " + error);
    });    
}

var currentStep = 1;

function displayBalancing(data) {
    console.log("Inside displayBalancing");

    timeRemaining = data["time"];
    console.log("timeRemaining");
    console.log(timeRemaining);

    var currentDate = new Date();
    currentDate.setMinutes(currentDate.getMinutes() + timeRemaining);

    hoursRemaining = currentDate.getHours();
    hoursRemaining = (hoursRemaining).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false});

    minutesRemaining = currentDate.getMinutes();
    minutesRemaining = (minutesRemaining).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false});

    const timeDisplay = document.getElementById("timeDisplay");
    timeDisplay.textContent = "Estimated Time at Finish:\n" + hoursRemaining + ":" + minutesRemaining;

    // Display instructions on balancing
    const helpDisplayText = document.getElementById("helpDisplayText");
    const helpDisplay = document.getElementById("helpDisplay");
    helpDisplayText.textContent = "Move the Blue Container to the Red Position, and then select Next";
    helpDisplay.style.backgroundColor = "white";
    
    // We need to disable the submit div so we can see the containers
    const beginBalanceButton = document.getElementById("informationInputContainer");
    beginBalanceButton.style.display = "none";
    
    // GO THROUGH every item in the returned json and show the steps of balancing!

    const nextButton = document.getElementById("nextButton");
    var currentStep = 1;
    nextButton.addEventListener("click", nextBalanceOperation);
    nextButton.data = data;

    highlightCurrentOperation(data[1]["origin"], data[1]["destination"]);

    console.log(data);
    // for (var element in data) {
    //     console.log(data[element]["origin"]);
    //     console.log(data[element]["destination"]);
    // }
}

function nextBalanceOperation(evt) {
    currentStep = currentStep + 1;

    // Get the data object
    data = evt.currentTarget.data;
    
    // Everytime we click "next", we need to clear the previous operation
    var prevOrigin = data[currentStep - 1]["origin"];
    var prevDestination = data[currentStep - 1]["destination"];
    
    // Get the previous origin and destination container
    const prevOriginContainer = document.getElementById(prevOrigin);
    const prevDestinationContainer = document.getElementById(prevDestination);

    // Grab the weight and description so that we can swap them after the move is done
    prevOriginContainerWeight = prevOriginContainer.children[1].textContent;
    prevOriginContainerDescription = prevOriginContainer.children[2].textContent;
    
    prevDestinationContainerWeight = prevDestinationContainer.children[1].textContent;
    prevDestinationContainerDescription = prevDestinationContainer.children[2].textContent;

    // Swap the weights and descriptions 
    prevDestinationContainer.children[1].textContent = prevOriginContainerWeight;
    prevDestinationContainer.children[2].textContent = prevOriginContainerDescription;

    prevOriginContainer.children[1].textContent = prevDestinationContainerWeight;
    prevOriginContainer.children[2].textContent = prevDestinationContainerDescription;

    // Finalize the previous operation by turning it back to white
    if (prevOriginContainer.children[2].textContent == "UNUSED") {
        prevOriginContainer.style.backgroundColor = "white";
    }
    else {
        prevOriginContainer.style.backgroundColor = "lightgreen";
    }
    if (prevDestinationContainer.children[2].textContent == "UNUSED") {
        prevDestinationContainer.style.backgroundColor = "white";
    }
    else {
        prevDestinationContainer.style.backgroundColor = "lightgreen";
    }

    // prevOriginContainer.style.backgroundColor = "white";
    // prevDestinationContainer.style.backgroundColor = "white";

    // Since the last step was successfully completed, we need to log the move as complete in case of power-shutoff
    prevStepJson = JSON.stringify(data[currentStep - 1]);

    console.log(prevStepJson);
    
    fetch(urlForStepSave, {
        method: 'POST',
        credentials: "include",
        body: prevStepJson,
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(response => {
        // Grab redirect link and follow through with it
        console.log("Step logged!");
    })
    .catch(function(err) {
        // console.info(err + " url: " + url);
        console.log("error logging last step");
    });    

    // Get the next operation and pass it into the highlight function
    // In a try block because it will eventually reach the end of the data object
    try {
        var origin = data[currentStep]["origin"];
        var destination = data[currentStep]["destination"];
    
        highlightCurrentOperation(origin, destination);
    } catch (error) {
        // We reached the end and can now proceed in our direction
        console.log("Reached end of the data object");

        // TODO IMPLEMENT THE NEXT STEP IN THE PROCESS

        // Create a new object that will contain the final manifest information on the screen
        newManifest = new Object();
        for (let i = 0; i < containerButtonArr.length; i++) {
            var containerPosition = containerButtonArr[i].children[0].id;
            var containerWeight = containerButtonArr[i].children[0].children[1].textContent;
            var containerDescription = containerButtonArr[i].children[0].children[2].textContent;
    
            var obj = new Object();
            // obj.position = containerPosition;
            obj.weight = containerWeight.slice(1, -1);
            obj.description = containerDescription;
    
            newManifest[containerPosition] = obj;        
        }

        console.log("newManifest:");
        console.log(newManifest);
        console.log(urlForExportManifest);
        newManifestJson = JSON.stringify(newManifest);

        // Send this new manifest data to the python side to trigger a download and redirect to home page
        fetch(urlForExportManifest, {
            method: 'POST',
            credentials: "include",
            body: newManifestJson,
            cache: "no-cache",
            redirect: "follow",
            headers: new Headers({
                "content-type": "application/json"
            })
        })
        .then(response => {
            // Grab redirect link and follow through with it
            if(response.redirected){
                window.location.href = response.url;
            }
        })
        .catch(function(err) {
            console.info(err + " url: " + url);
        });
    }
}

function highlightCurrentOperation(origin, destination) {
    const originContainer = document.getElementById(origin);
    const destinationContainer = document.getElementById(destination);

    originContainer.style.backgroundColor = "blue";
    destinationContainer.style.backgroundColor = "red";
}

commentInputSubmission = document.getElementById("commentInputSubmission");
commentInputSubmission.addEventListener("click", commentSubmission);

function commentSubmission() {
    commentInput = document.getElementById("commentInput");
    commentInput = commentInput.value;

    console.log(commentInput);

    commentInputJson = JSON.stringify(commentInput);

    console.log(commentInputJson);
    
    fetch(urlForCommentLog, {
        method: 'POST',
        credentials: "include",
        body: commentInputJson,
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
    .then(response => {
        // Grab redirect link and follow through with it
        console.log("comment pooped!");
        commentInput = document.getElementById("commentInput");
        commentInput.value = '';
    })
    .catch(function(err) {
        // console.info(err + " url: " + url);
    });
}