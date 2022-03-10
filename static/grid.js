let index = 0;
function TurnRed(cellId,positionI,positionJ){
    element = document.getElementById(cellId);
    colors = ["Red","#2664F5"]
    element.style.backgroundColor = colors[index];
    index = index >= colors.length - 1 ? 0 : index + 1; 
}

function TurnGreen(cellId) {
    element = document.getElementById(cellId);
    colors = ["#055a05","White"]
    element.style.backgroundColor = colors[index];
    index = index >= colors.length - 1 ? 0 : index + 1; 
}

function TurnPink(cellId) {
    console.log(cellId)
    element = document.getElementById(cellId);
    element.style.backgroundColor = "Pink";
}