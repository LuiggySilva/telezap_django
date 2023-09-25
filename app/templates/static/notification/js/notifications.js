// Function to get Cookie 
function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}

// Function to generate a CSRF input as a string
function generateCSRFInputAsString() {
    var csrfToken = getCookie("csrftoken");
    var csrfInputString = '<input type="hidden" name="csrfmiddlewaretoken" value="' + csrfToken + '">';

    return csrfInputString;
}

document.addEventListener("DOMContentLoaded", function() {
    function connect() {
        // Verify if the protocol is https or http and set the websocket protocol accordingly
        var websocketProtocol = "ws://";
        if (window.location.protocol === 'https:') {
            websocketProtocol = "wss://";
        }
        const socket = new WebSocket(websocketProtocol + window.location.host + '/ws/notification_updates/');
        
        // When the websocket is connected, log it to the console
        socket.onopen = function(event) {
            console.log('WebSocket (notifications) is connected.');
        };
        
        // When the websocket is closed, try to reconnect in 2 seconds
        socket.onclose = function(event) {
            setTimeout(function() {
                console.error("WebSocket (notifications) connection closed unexpectedly, trying to reconnect in 2 seconds...");
                connect()
            }, 2000);
        };
              
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            // If the message is an update, update the chat list
            if (data.type == 'update') {
                // If the notification is a group notification, update the group notification status
                if (data.group_id != null) {
                    document.getElementById(`grupo-${data.group_id}-${data.id}-status`).innerText = data.status;
                } else { // If the notification is a friend notification, update the friend notification status
                    document.getElementById(`amizade-${data.id}-status`).innerText = data.status;
                }

                // If the notification is a group notification and it is finished, show the remove form
                if (data.finished && data.group_id != null) {
                    document.getElementById("group-finished-remove-form").setAttribute('style', 'display: visible;');
                } else { // If the notification is a friend notification and it is finished, show the remove form
                    document.getElementById("friend-finished-remove-form").setAttribute('style', 'display: visible;');
                }
            } else if (data.type == 'new') { // If the message is a new notification, add it to the notification list
                const elementMap = {
                    group_send: 'group-send-notifications',
                    group_received: 'group-received-notifications',
                    friend_send: 'friend-send-notifications',
                    friend_received: 'friend-received-notifications'
                };

                let targetElementId;

                // If the notification is a group notification, set the target element id to the group notification list
                if (data.is_group) {
                    targetElementId = data.is_sent ? 'group_send' : 'group_received';
                } else {
                    targetElementId = data.is_sent ? 'friend_send' : 'friend_received';
                }

                const targetElement = document.getElementById(elementMap[targetElementId]);

                // Remove the empty notification list element if it exists
                if (targetElement.getElementsByClassName('m-2').length > 0) {
                    targetElement.getElementsByClassName('m-2')[0].remove();
                }

                // Create a new notification list element and add it to the notification list
                const elem = document.createElement('div');
                // Add CSRF token to the form of the notification 
                const regex = /<form action="\/notificacoes\/reply\/" method="POST">/g;
                const template = data.template.replaceAll(
                    regex,
                    '<form action="/notificacoes/reply/" method="POST">' + '\n' + generateCSRFInputAsString()
                );
                elem.innerHTML = '<hr>' + template;

                targetElement.prepend(elem);
            }
        };
    };

    connect();
});
