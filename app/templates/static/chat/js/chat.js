// Variables to control the load of messages
let page=1;
let has_next=false;
var oldMsgDate = null;

// Function to preview the image before sending
function imagePreview() {
    const fileInput = document.getElementById('id_image');
    const imagePreview = document.getElementById('image-preview');
    const loadingImage = document.getElementById('loading-image');
    
    fileInput.addEventListener('change', () => {
        const selectedFile = fileInput.files[0];

        if (selectedFile) {
            const imageURL = URL.createObjectURL(selectedFile);
            loadingImage.style.display = 'block';
            imagePreview.onload = function () {
                loadingImage.style.display = 'none'; 
                imagePreview.style.display = 'block';
            };
            imagePreview.src = imageURL;
        } else {
            loadingImage.style.display = 'none'; 
            imagePreview.src = '';
            imagePreview.style.display = 'none';
        }
    });
}


// Function to close the image preview when the user clicks on the close button
function imagePreviewClose() {
    const buttonClose = document.getElementById('image-form-close');
    const buttonSend = document.getElementById('image-form-send');
    const imagePreview = document.getElementById('image-preview');
    const fileInput = document.getElementById('id_image');

    buttonClose.addEventListener('click', () => {
        imagePreview.setAttribute('src', '');
        imagePreview.setAttribute('alt', '');
        fileInput.value = '';
    });

    buttonSend.addEventListener('click', () => {
        setTimeout(function() {
            imagePreview.setAttribute('src', '');
            imagePreview.setAttribute('alt', '');
            fileInput.value = '';
        }, 1000);
    });
}


// Function to auto resize the textarea when the user types
function autoResizeTextArea() {
    const textarea = document.getElementById('autoresizing-textarea');
    textarea.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
    });

    textarea.addEventListener('keydown', function (event) {
        // Verify if the user pressed the Enter key without the Shift key
        if (event.keyCode === 13 && !event.shiftKey) {
            // Prevent the default action of the Enter key (new line)
            event.preventDefault();
            // Submit the form
            const form = document.getElementById('text-form');
            form.submit();
            // Clear the textarea
            textarea.value = '';
        }
    });
}


// Function to scroll the messages to the bottom 
function scrollMessages() {
    const scrollArea = document.getElementById('messages');
    scrollArea.scrollTop = scrollArea.scrollHeight;
}


// Function to clear the textarea when the user clicks on the submit button
function clearTextarea() {
    const textarea = document.getElementById('autoresizing-textarea');
    const submitButton = document.getElementById('text-form-submit-btn');
    const emptyChat = document.getElementById('empty-chat');
    submitButton.addEventListener('click', () => {
        setTimeout(function() {
            textarea.value = '';
        }, 500);
        emptyChat.setAttribute('style', 'display: none;');
    });
}


// Function to connect to the websocket
function connect() {
    // Get the chat id from the url
    const chatId = window.location.pathname.split('/')[2];
    // Verify if the protocol is https or http and set the websocket protocol accordingly
    var websocketProtocol = "ws://";
    if (window.location.protocol === 'https:') {
        websocketProtocol = "wss://";
    }
    const socket = new WebSocket(websocketProtocol + window.location.host + '/ws/chat/' + chatId + '/');

    // When the websocket is connected, log it to the console
    socket.onopen = function(event) {
        console.log('WebSocket (chat) is connected.');
    };

    // When the websocket is closed, try to reconnect in 2 seconds
    socket.onclose = function(event) {
        setTimeout(function() {
            console.error("WebSocket (chat) connection closed unexpectedly, trying to reconnect in 2 seconds...");
            connect()
        }, 2000);
    };

    // When the websocket receives a message, parse it and update the chat list
    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const emptyChat = document.getElementById('empty-chat');

        // If the message is an update, update the chat list
        if (data.type == 'create') {
            const targetElement = document.getElementById('message-list');
            const li = document.createElement('li');
            li.setAttribute("class", "d-flex justify-content-between mb-4");
            li.innerHTML = data.template;
            targetElement.appendChild(li);
            emptyChat.setAttribute('style', 'display: none;');
        }
        scrollMessages();
    };

};


// Function to get the url to get the messages
function getMessagesUrl() { 
    const messagesElem = document.getElementById('messages');
    return messagesElem.getAttribute('data-get-messages-url');
};


// Function to append the messages to the message list
function appendMessages(messageList) {
    const scrollArea = document.getElementById('messages');
    const currentScrollHeight = scrollArea.scrollHeight;
    const spanClassName = "d-flex justify-content-center badge rounded-pill text-bg-secondary text-center mt-1 mb-2"
    
    const messageListUlElem = document.getElementById("message-list");
    for (let i = 0; i < messageList.length; i++) {
        const li = document.createElement("li");
        // If the message is the last unviewed message, add the id to the li element and set the tabindex to 0 to allow the user to focus on it
        if (messageList[i]["is_last_unviewed_message"]) {
            li.setAttribute("id", "last-unviewed-message");
            li.setAttribute("tabindex", "0");
        }
        li.setAttribute("class", "d-flex justify-content-between mb-3");
        li.innerHTML = messageList[i]["template"];
        messageListUlElem.prepend(li);
        // If the message has a separator, add it to the message list
        if (messageList[i]['separator']) {
            const msgSeparator = document.createElement("span");
            msgSeparator.setAttribute("class", spanClassName);
            msgSeparator.innerText = messageList[i]['separator'];
            messageListUlElem.prepend(msgSeparator);
        }
    }
    
    // Fix the scroll position after appending the messages
    const scrollDifference = scrollArea.scrollHeight - currentScrollHeight;
    scrollArea.scrollTop += scrollDifference;
};


// Function to load more messages and append them to the message list
function loadMoreMessages() {
    const get_messages_url = getMessagesUrl() + `?page=${page}`;
    const loadingMessagesElem = document.getElementById('loading-messages');
    loadingMessagesElem.setAttribute('style', 'display: block;');
    const emptyChat = document.getElementById('empty-chat');

    fetch(get_messages_url)
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        // If there are no more messages, return
        if (!data["message_list"]) {
            return;
        } else {
            // If the last loaded messages has_next is true, append the messages to the message list
            if (has_next) {
                appendMessages(data["message_list"]);
            }
        }
        // If there are more messages, update the page and has_next variables
        if (data["has_next"] === true) {
            page++;
            has_next = true;
        } else {
            has_next = false;
        }
        loadingMessagesElem.setAttribute('style', 'display: none;');
        emptyChat.setAttribute('style', 'display: none;');
    });
}


// Function to load more messages when the user scrolls to the top of the message list
function loadMoreMessagesOnScroll() {
    const scrollArea = document.getElementById('messages');
    scrollArea.addEventListener("scroll", function () {
        if (scrollArea.scrollTop === 0) {
            loadMoreMessages();
        }
    });
}


// Function to show the load more messages button if the message list height is less than the scroll area height
function showLoadMoreMessagesButton() {
    const scrollArea = document.getElementById('messages');
    const messageList = document.getElementById('message-list');
    const loadMoreMessagesDiv = document.getElementById('load-more-messages');
    const loadMoreMessagesButton = document.getElementById('load-more-messages-btn');

    loadMoreMessagesButton.addEventListener('click', () => {
        loadMoreMessages();
        loadMoreMessagesDiv.setAttribute('style', 'display: none;');
    });

    if (messageList.clientHeight <= scrollArea.offsetHeight) {
        loadMoreMessagesDiv.setAttribute('style', 'display: block;');
    } else {
        loadMoreMessagesDiv.setAttribute('style', 'display: none;');
    }
}   


// Function to insert the emoji in the textarea when the user clicks on it
function activeEmojis() {
    const textarea = document.getElementById('autoresizing-textarea');
    const emojis = document.querySelectorAll('.emoji-icon');
    
    emojis.forEach(emoji => {
        emoji.addEventListener('click', () => {
            const emojiValue = emoji.innerHTML;
            textarea.value += emojiValue.trim();

            const event = new Event('input', {
                bubbles: true,  // Permite que o evento borbulhe na árvore DOM
                cancelable: true // Permite que o evento seja cancelado
            });
            textarea.dispatchEvent(event);
        });
    });
}


document.addEventListener("DOMContentLoaded", function() {
    connect();
    imagePreview();
    imagePreviewClose();
    autoResizeTextArea();
    clearTextarea();
    activeEmojis();
    
    const get_messages_url = getMessagesUrl();
    const emptyChat = document.getElementById('empty-chat');
    const loadingMessagesElem = document.getElementById('loading-messages');
    loadingMessagesElem.setAttribute('style', 'display: block;');

    // Get the messages (first page) from the server and append them to the message list 
    fetch(get_messages_url) 
    .then((response) => {
        return response.json();
    }).then((data) => {
        // If there are no messages, show the empty chat message
        if (!data["message_list"]) {
            loadingMessagesElem.setAttribute('style', 'display: none;');
            emptyChat.setAttribute('style', 'display: block;');
        } else { // If there are messages, append them to the message list
            if (data["has_next"] === true) {
                page++;
                has_next = true;
            }
            appendMessages(data["message_list"]);
            setTimeout(scrollMessages, 500);
            setTimeout(showLoadMoreMessagesButton, 500);
            setTimeout(() => {
                try {
                    document.getElementById('last-unviewed-message').focus();
                } catch (error) {
                    console.log("No last unviewed message");
                }
            }, 500);
        }
        loadingMessagesElem.setAttribute('style', 'display: none;');
    });
    
    loadMoreMessagesOnScroll();
});
