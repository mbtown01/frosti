"use strict";


fetch("/api/sensors/temperature").then(function(response) {
    response.text().then(function(text) {
        document.getElementById('temperature').innerHTML = text;
    });
});
