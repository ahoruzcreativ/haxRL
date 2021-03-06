//TODO 
//Direkten bazen hayvan gibi dönme şeysini düzelt
//Borderları start end diye refactor et

//Epsilon annealing gibi son algoritma tricklerini implement et, parametreleri guzellestir
//Jsona yazıp okumayı implement et sonra timeoutsuz calistir


//LAYERS REFACTOR
//-activation ayri layer
//-networke input shape init


// Gets the handles for rendering
var canvas = document.getElementById("gameCanvas");
var canvas2 = document.getElementById("agentVisionCanvas");
var ctx = canvas.getContext('2d');
var cHeight = canvas.height;
var cWidth = canvas.width;
// Init keypress events
var keys = {};
window.onkeydown = function (evt) {
    keys[evt.key] = true;
};
window.onkeyup = function (evt) {
    keys[evt.key] = false;
};

// Parameters
var bgColor = Color.green;
var redColor = Color.red;
var blueColor = Color.blue;
var playerMass = 3;
var ballMass = 2;
var playerRestitution = 0.45;
var borderRestitution = 1;
var ballRestitution = 0.45;
var playerDamping = 0.93;
var playerkickDamping = 0.87;
var playerkickPower = 15;
var playerRadius = 16;
var ballRadius = 10;
var ballDamping = 0.98;
var topbottomMargin = 40;
var leftrightMargin = 55;
var goalLength = 140;
var middleFieldRadius = 83;
var postRadius = 8.5;
var scaleH = 0.20;
var scaleW = 0.20;
//
var env = new Environment( /*render*/ true, /*sound*/ true, /*resetDelay*/ true, /*randomStart*/ false);
env.addAgent(new HumanAgent("w", "s", "a", "d", "q"), Side.red);
//env.addAgent(new HumanAgent("ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "."), Side.blue);
env.addAgent(new HumanAgent("8", "5", "4", "6", "0"), Side.blue);

env.draw();


setInterval(() => {
    env.update();
}, 30);