function emojiNotItalic(string) {
    var newString = "";
    for (const char of string) {
        if (/\p{RGI_Emoji}/v.test(char)) {
            newString += '<span class="no-italic">' + char + '</span>';
        } else {
            newString += char;
        }
    }
    return newString;
}

  
document.addEventListener("DOMContentLoaded", function() {
    function connect() {
        // Verify if the protocol is https or http and set the websocket protocol accordingly
        var websocketProtocol = "ws://";
        if (window.location.protocol === 'https:') {
            websocketProtocol = "wss://";
        }
        const socket = new WebSocket(websocketProtocol + window.location.host + '/ws/chats/');
        
        // When the websocket is connected, log it to the console
        socket.onopen = function(event) {
            console.log('WebSocket (chat_list) is connected.');
        };
        
        // When the websocket is closed, try to reconnect in 2 seconds
        socket.onclose = function(event) {
            setTimeout(function() {
                console.error("WebSocket (chat_list) connection closed unexpectedly, trying to reconnect in 2 seconds...");
                connect()
            }, 2000);
        };

        // When the websocket receives a message, parse it and update the chat list
        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);

            // If the message is an update, update the chat list
            if (data.type == 'update') {
                // Update the chat list
                const chatDateElement = document.getElementById(`chat-${data.chat_id}-date`);
                chatDateElement.innerText = data.chat_message_date;
                
                // Update the chat message
                const chatMessageElement = document.getElementById(`chat-${data.chat_id}-content`);
                chatMessageElement.innerHTML = emojiNotItalic(data.chat_message_content);
                
                // Update the chat unviewed messages count
                const chatUnviewedMessagesCountElement = document.getElementById(`chat-${data.chat_id}-count`);
                chatUnviewedMessagesCountElement.innerText = data.chat_unviewed_messages_count;
                chatUnviewedMessagesCountElement.style.visibility = data.chat_unviewed_messages_count > 0 ? 'visible' : 'hidden';
                
                // Update the chat author
                const chatAuthorElement = document.getElementById(`chat-${data.chat_id}-author`);
                chatAuthorElement.innerText = data.chat_message_author + ': ';
            // If the message is a new chat, add it to the chat list
            } else if (data.type == 'create') {
                // Create a new chat list element
                const fragment = document.createRange().createContextualFragment(data.template).querySelector('a');

                // Add the new chat list element to the chat list
                const chatListElement = document.getElementById('chat-list');
                chatListElement.prepend(fragment);

                // Remove the empty chat list element if it exists
                const emptyChatListElement = document.getElementById('empty-chat-list');
                if (emptyChatListElement) {
                    emptyChatListElement.remove();
                }
            }
        };
    };

    connect();
});
