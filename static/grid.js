let index = 0;
function TurnRed(cellId){
    element = document.getElementById(cellId);
    colors = ["Red","#2664F5"]
    element.style.backgroundColor = colors[index];
    index = index >= colors.length - 1 ? 0 : index + 1; 
}

function TurnGree(cellId) {
    element = document.getElementById(cellId);
    colors = ["White","#055a05"]
    element.style.backgroundColor = colors[index];
    index = index >= colors.length - 1 ? 0 : index + 1; 
}