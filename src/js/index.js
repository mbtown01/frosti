"use strict";

function updateSettingsValue(setting) {
    fetch('/api/settings').then(function(response) {
        return response.json();
    }).then(function(myJson) {
        document.getElementById(setting).innerHTML = myJson[setting]
    })
}

function updateSensorValue(sensor) {
    fetch('/api/sensors').then(function(response) {
        return response.json();
    }).then(function(myJson) {
        document.getElementById(sensor).innerHTML = myJson['sensors'][sensor]
    })
}

function toggleMode() {
    fetch("/api/action/mode_toggle", {method: 'POST'})
}

function update() {
    fetch('/api/status').then(function(response) {
        return response.json();
    }).then(function(myJson) {
        document.getElementById('temperature').innerHTML = myJson.sensors.temperature
        document.getElementById('pressure').innerHTML = myJson.sensors.pressure
        document.getElementById('humidity').innerHTML = myJson.sensors.humidity
    })

    fetch('/api/settings').then(function(response) {
        return response.json();
    }).then(function(myJson) {
        document.getElementById('comfortMin').innerHTML = myJson.comfortMin
        document.getElementById('comfortMax').innerHTML = myJson.comfortMax
        document.getElementById('mode').innerHTML = myJson.mode
    })
}

