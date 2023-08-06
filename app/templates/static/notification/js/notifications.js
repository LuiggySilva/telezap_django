
document.addEventListener("DOMContentLoaded", function() {
    function connect() {
        const socket = new WebSocket(
            'ws://' + window.location.host + '/ws/notification_updates/');
    
        socket.onopen = function(event) {
            console.log('WebSocket is connected.');
        };
    
        socket.onclose = function(event) {
            setTimeout(function() {
                console.error("WebSocket connection closed unexpectedly, trying to reconnect in 2 seconds...");
                connect()
            }, 2000);
        };
              
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            if (data.type == 'update') {
                if (data.group_id != null) {
                    document.getElementById(`grupo-${data.group_id}-${data.id}-status`).innerText = data.status;
                } else {
                    document.getElementById(`amizade-${data.id}-status`).innerText = data.status;
                }

                if (data.finished && data.group_id != null) {
                    document.getElementById("group-finished-remove-form").setAttribute('style', 'display: visible;');
                } else {
                    document.getElementById("friend-finished-remove-form").setAttribute('style', 'display: visible;');
                }
            } else if (data.type == 'new') {
                const elementMap = {
                    group_send: 'group-send-notifications',
                    group_received: 'group-received-notifications',
                    friend_send: 'friend-send-notifications',
                    friend_received: 'friend-received-notifications'
                  };
                
                  let targetElementId;
                
                  if (data.is_group) {
                    targetElementId = data.is_sent ? 'group_send' : 'group_received';
                  } else {
                    targetElementId = data.is_sent ? 'friend_send' : 'friend_received';
                  }
                
                  const targetElement = document.getElementById(elementMap[targetElementId]);
                
                  if (targetElement.getElementsByClassName('m-2').length > 0) {
                    targetElement.getElementsByClassName('m-2')[0].remove();
                  }
                
                  const elem = document.createElement('div');
                  elem.innerHTML = '<hr>' + data.template;
                  targetElement.prepend(elem);
            }
        };
    };

    connect();
});
