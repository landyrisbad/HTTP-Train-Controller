var speedVal = 0;
const angleZero = 210;

var increaseSpeed;
var decreaseSpeed;
var dial;
var speedInfo;
var directionSwitch;
var stop;

document.addEventListener("keydown", function (event) {
    console.log(event.key);
    if (event.key == "ArrowDown") { 
        changeSpeed(null, -1);
    }
    else if (event.key == "ArrowUp") {
        changeSpeed(null, 1);
    }
    else if (event.key == "ArrowRight") {
        setDirection(true);
    }
    else if (event.key == "ArrowLeft") {
        setDirection(false);
    }
    else if (event.key == " ") {
        eSTOP();
    }
});

function setNonDraggable (image) {
    image.draggable = false;
}

function eSTOP () {
    speedVal = 0;
    changeSpeed(null, speedVal);
}

function onload () {
    const images = Array.from(document.getElementsByTagName("img"));
    images.forEach(setNonDraggable)

    dial = document.getElementById("dial");
    speedInfo = document.getElementById("speedVal");
    directionSwitch = document.getElementById("direction");
    directionSwitch.addEventListener("click", setDirection);

    increaseSpeed = document.getElementById("increase");
    decreaseSpeed = document.getElementById("decrease");
    increaseSpeed.addEventListener("click", changeSpeed);
    decreaseSpeed.addEventListener("click", changeSpeed);
    increaseSpeed.speedChangeVal = 1;
    decreaseSpeed.speedChangeVal = -1;
}

async function setDirection(val) {
    var direction = val ? 1 : 0;

    if (val) {
        directionSwitch.src = "direction-off.png";
    }
    else {
        directionSwitch.src = "direction-on.png";
    }

    const setDirection = await fetch(`/direction/${direction}`);
    console.log(await setDirection.ok());
}

async function changeSpeed (event, setValue = 0) {
    if (event != null) {
        speedVal += event.currentTarget.speedChangeVal;
    }
    else {
        speedVal += setValue;   
    }
    if (speedVal < 0) {
        speedVal = 0;
    }
    else if (speedVal > 10) {
        speedVal = 10;
    }

    speedInfo.innerHTML = speedVal * 10
    dial.style.transform = "rotate(" +  getAngle(speedVal) + "deg)";

    const changeSpeed = await fetch(`/speed/${speedVal}`);
    console.log(await changeSpeed.ok());
} 

function getAngle (val) {
    return angleZero + val * 30;
}
