
function engine(){
    var container = document.getElementById("container");
    i = 0;
    while (i < 150){
        var img = document.createElement("IMG");
        img.src = './../boards/board'+i+'.SVG';
        img.style = 'display:none';
        img.id = i;
        container.appendChild(img);
        i++;
    }

}

var position = 0;
var running = true;
var speed = 1000;

setInterval(function(){ 

    if (running){

        lastPos = position-1;
        if (lastPos >= 0){
            var tempImg = document.getElementById(lastPos).setAttribute("style", "display:none");
        }
        var tempImg = document.getElementById(position).setAttribute("style", "display:block");

        position+=1
    }
    

}, speed);


engine()