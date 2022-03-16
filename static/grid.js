let index = 0;
let cont = 0;

function UnloadContainer(cellId,positionI,positionJ){
    element = document.getElementById(cellId);
    cssObj = getComputedStyle(element,null)
    bgColor = cssObj.getPropertyValue("background-color")
    if (bgColor === "rgb(38, 100, 245)") {
        element.style.backgroundColor = "Red"
    }
    else {
        element.style.backgroundColor = "#2664F5"
    }
}

function LoadContainer(cellCoordinates) {
    element = document.getElementById(cellCoordinates);
    cssObj = getComputedStyle(element, null)
    bgColor = cssObj.getPropertyValue("background-color")
    if (bgColor=== "rgb(255, 255, 255)"){
        element.style.backgroundColor = "#055a05";
        cont = cont + 1;
    }
    else {
        element.style.backgroundColor = "#FFFFFF";
        cont = cont - 1;
    }
}

function TurnPink(cellId,count,totalMoves) {
    console.log(cellId)
    element = document.getElementById(cellId);
    element.style.backgroundColor = "Pink";
}

function CurrentContainer(cellId){
    console.log(cellId)
    element = document.getElementById(cellId);
    element.style.backgroundColor = "Red";
}

function popupFunction() {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
  }

var unloading_containers = [];
var loading_coordinates = [];

function FinalizeContainers(){

    //Finalize containers that are going to be unloaded
    var elements = document.getElementsByClassName("containerButtonWrapper")
    for (let i = 0; i < elements.length; i++){
        cssObj = getComputedStyle(elements[i], null)
        bgColor = cssObj.getPropertyValue("background-color")
        if (bgColor === "rgb(255, 0, 0)") {
            var weight = elements[i].getAttribute("data-weight")
            var container = {'name':elements[i].id, 'weight':weight}
            unloading_containers.push(container)
        }
    }

    //Finalize poisitons that are going to be loaded
    var positions = document.getElementsByClassName("emptySlotWrapper")
    for (let i = 0; i < positions.length; i++){
        cssObj = getComputedStyle(positions[i], null)
        bgColor = cssObj.getPropertyValue("background-color")
        if (bgColor === "rgb(5, 90, 5)") {
            var container = {'grid position':positions[i].id}
            loading_coordinates.push(container)
        }
    }
    // Sending to FLASK
    alert('Locations Submitted To System!');
    grid_data = {'unloading':unloading_containers, 'loading':loading_coordinates}
    var unloading_containers_JSON = JSON.stringify(grid_data);


    $.ajax({
        type:"POST",
        contentType: "application/json",
        url:"/jsresponse",
        data: unloading_containers_JSON,
        dataType: "json",
        success: function(response) {
            console.log(response);
        },
        error: function(err) {
            console.log(err);
        }
    });


    // starttransferURL goes to start_transfer function in python
    // fetch(jsresponseURL, {
    //     method: 'POST',
    //     credentials: "include",
    //     body: unloading_containers_JSON,
    //     cache: "no-cache",
    //     redirect: "follow",
    //     headers: new Headers({
    //         "content-type": "application/json"
    //     })
    // })
    // .then(response =>{
    //     // Grab redirect link and follow through with it
    //     if (response.redirected){
    //         window.location.href = response.url;
    //     }

    // })
    // .catch(function(err) {
    //     console.info(err + " url: ");
    // });

}



//var json_unload_containers = JSON.stringify(unloading_containers);