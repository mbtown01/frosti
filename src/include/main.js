"use strict";

function update() {
    fetch('/api/status').then(function(response) {
        return response.json();
    }).then(function(myJson) {
        document.getElementById('temperature').innerHTML = myJson.sensors.temperature
        document.getElementById('pressure').innerHTML = myJson.sensors.pressure
        document.getElementById('humidity').innerHTML = myJson.sensors.humidity
        document.getElementById('state').innerHTML = myJson.state
    })

    fetch('/api/settings').then(function(response) {
        return response.json();
    }).then(function(myJson) {
        document.getElementById('comfortMin').innerHTML = myJson.comfortMin
        document.getElementById('comfortMax').innerHTML = myJson.comfortMax
        document.getElementById('mode').innerHTML = myJson.mode
    })
}

function nextMode() {
    fetch("/api/action/nextMode", {method: 'POST'})
    .then(function(response) {
        update();
    });
}

function raiseComfort() {
    fetch("/api/action/raiseComfort", {method: 'POST'}).then(update());
}

function lowerComfort() {
    fetch("/api/action/lowerComfort", {method: 'POST'}).then(update());
}