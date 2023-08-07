var speedVal = 0;
const angleZero = 210;

var increaseSpeed;
var decreaseSpeed;
var dial;
var speedInfo;
var directionSwitch;
var stop;
var directionVal;
var canSwitch = false;
var doChangeAngle = false;
var controllingZone = 0;
var zoneDiv;

var isManual;

setInterval(function () { document.activeElement.blur() }, 1);

document.addEventListener("keydown", function (event) {
    if (isManual.checked) {
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
    }   
    if (event.key == " ") {
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

function toRadians(degrees) {
    return degrees * Math.PI / 180;
}
function toDegrees(radians) {
    return radians * 180 / Math.PI;
}

function calcDialAngle (event) {
    if (!doChangeAngle) { return; }

    var lat2 = toRadians(event.clientX);
    var long2 = toRadians(event.clientY);

    var dialBoundingBox = document.getElementById("knob").getBoundingClientRect();
    var lat1 = toRadians(dialBoundingBox.x + dialBoundingBox.width / 2) 
    var long1 = toRadians(dialBoundingBox.y);
    console.log(dialBoundingBox.x + dialBoundingBox.width / 2, dialBoundingBox.y);
    console.log(lat2, long2); 

    var angle = Math.atan2(
        Math.sin(long2 - long1) * Math.cos(lat2),
        Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(long2 - long1)
    )

    angle = (toDegrees(angle) + 360) % 360;

    console.log(angle);

    dial.style.transform = "rotate(" + angle + "deg)";
}

function onload () {
    const images = Array.from(document.getElementsByTagName("img"));
    images.forEach(setNonDraggable)

    dial = document.getElementById("dial");
    window.addEventListener("mousemove", calcDialAngle);
    /* dial.addEventListener("mousedown", () => {
        doChangeAngle = true;
    });
    window.addEventListener("mouseup", () => {
        doChangeAngle = false;
    }); */

    speedInfo = document.getElementById("speedVal");
    directionSwitch = document.getElementById("direction");
    directionSwitch.addEventListener("click", setDirection);

    increaseSpeed = document.getElementById("increase");
    decreaseSpeed = document.getElementById("decrease");
    increaseSpeed.addEventListener("click", changeSpeed);
    decreaseSpeed.addEventListener("click", changeSpeed);
    increaseSpeed.speedChangeVal = 1;
    decreaseSpeed.speedChangeVal = -1;

    isManual = document.getElementById("isManual");
    isManual.addEventListener("change", setManualControls);

    zoneDiv = document.getElementById("zone-control")
    setZones();
}

function setManualControls () {
    var val = isManual.checked;

    if (val) {
        document.getElementById("manual-controls").style.display = "block";
        document.getElementById("auto-controls").style.display = "none";
        zoneDiv.style.display = "block";
    }
    else {
        document.getElementById("manual-controls").style.display = "none";
        document.getElementById("auto-controls").style.display = "block";
        zoneDiv.style.display = "none";
    }
}

async function setDirection(val) {
    if (speedVal > 1  && !canSwitch) {
        if (confirm("It is not advisable to change direction at speed. Do you wish to continue (and ignore future warnings)?")) {
            canSwitch = true;
        } else {
            canSwitch = false;
        }
    }

    if (!canSwitch && speed > 2) {
        return
    }

    if (typeof val == "object") {
        val = !directionVal;
    }

    var direction = val ? 1 : 0;
    directionVal = direction;

    if (val) {
        directionSwitch.src = "direction-off.png";
    }
    else {
        directionSwitch.src = "direction-on.png";
    }

    const setDirection = await fetch(`/direction/${controllingZone}/${direction}`);
    console.log(await setDirection.text());
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

    const changeSpeed = await fetch(`/speed/${controllingZone}/${speedVal}`);
    console.log(await changeSpeed.text());
} 

function getAngle (val) {
    return angleZero + val * 30;
}

function zoneTemplate (id, defaultZone) {
    var checked = id == 0 ? "checked" : "";
    return `<label for="zone${id}">Zone ${id + 1}</label><input type="radio" name="zone" id="zone${id}" onclick="updateCurrentZone(this);" value="${id}" ${checked}></input>`;
}

async function updateCurrentZone (radio) {
    controllingZone = radio.value;
    const zone = await fetch(`/speed/${controllingZone}`);
    const zoneSpeed = int(await zone.text());
    speedVal = zoneSpeed;
    setDisplaySpeed(null, zoneSpeed);
}

async function setZones () {
    var numZones;
    var defaultZone;

    try {
        const zones = await fetch(`/zoneinfo`);
        var zoneInfo = (await zones.text()).split(",");
        numZones = zoneInfo[0];
        defaultZone = zoneInfo[1];
    } catch {
        var numZones = 2;
        var defaultZone = 0;
    }

    for (let i = 0; i < numZones; i++) {
        var span = document.createElement("span");
        span.innerHTML = zoneTemplate(i, defaultZone);
        zoneDiv.append(span);
    }
}