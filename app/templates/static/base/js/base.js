
// Function to connect to the websocket
function navbarWebSocketConnect() {
  // Verify if the protocol is https or http and set the websocket protocol accordingly
  var websocketProtocol = "ws://";
  if (window.location.protocol === 'https:') {
      websocketProtocol = "wss://";
  }
  const socket = new WebSocket(websocketProtocol + window.location.host + '/ws/navbar/');

  // When the websocket is connected, log it to the console
  socket.onopen = function(event) {
      console.log('WebSocket (navbar) is connected.');
  };

  // When the websocket is closed, try to reconnect in 2 seconds
  socket.onclose = function(event) {
      setTimeout(function() {
          console.error("WebSocket (navbar) connection closed unexpectedly, trying to reconnect in 2 seconds...");
          connect()
      }, 2000);
  };

  // When the websocket receives a message, parse it and update the chat list
  socket.onmessage = function(e) {
      const data = JSON.parse(e.data);
      const type = data['type'];
      const value = data['value'];

      const elements = {
          'navbar_chat_unviewed_messages': "nav-chats",
          'navbar_notification_pending_notifications': "nav-notifications",
          'navbar_groupchat_unviewed_messages': "nav-group",
      }

      const element = document.getElementById(elements[type]);
      if (value == true) {
          element.setAttribute("class", "blinking-text");
      } else {
          element.removeAttribute("class");
      }
      
  };

};

(() => {
    'use strict';

    const getStoredLanguage = () => localStorage.getItem('language');
    const setStoredLanguage = language => localStorage.setItem('language', language);
  
    const getPreferredLanguage = () => {
      const storedLanguage = getStoredLanguage()
      if (storedLanguage) {
        return storedLanguage;
      }
      return window.matchMedia('(prefers-language-scheme: portuguese)').matches ? 'portuguese' : 'english';
    }
  
    const setLanguage = language => {
      if (language === 'auto' && window.matchMedia('(prefers-language-scheme: portuguese)').matches) {
        document.documentElement.setAttribute('data-bs-language', 'portuguese');
      } else {
        document.documentElement.setAttribute('data-bs-language', language);
      }
    }
  
    setLanguage(getPreferredLanguage())
  
    const showActiveLanguage = (language, focus = false) => {
      const languageSwitcher = document.querySelector('#bd-language');
      if (!languageSwitcher) {
        return
      }
  
      const languageSwitcherText = document.querySelector('#bd-language-text');
      const activeLanguageIcon = document.querySelector('.language-icon-active');
      const btnToActive = document.querySelector(`[data-bs-language-value="${language}"]`);
  
      document.querySelectorAll('[data-bs-language-value]').forEach(element => {
        element.classList.remove('active');
        element.setAttribute('aria-pressed', 'false');
      })
  
      btnToActive.classList.add('active');
      btnToActive.setAttribute('aria-pressed', 'true');
      if (language === 'portuguese') {
        activeLanguageIcon.innerText = "🇧🇷";
      } else {
        activeLanguageIcon.innerText = "🇺🇸";
      }
    }
  
    window.matchMedia('(prefers-language-scheme: portuguese)').addEventListener('change', () => {
      const storedLanguage = getStoredLanguage();
      if (storedLanguage !== 'english' && storedLanguage !== 'portuguese') {
        setLanguage(getPreferredLanguage());
      }
    })
  
    window.addEventListener('DOMContentLoaded', () => {
      showActiveLanguage(getPreferredLanguage());
  
      document.querySelectorAll('[data-bs-language-value]')
        .forEach(toggle => {
          toggle.addEventListener('click', () => {
            const language = toggle.getAttribute('data-bs-language-value');
            setStoredLanguage(language);
            setLanguage(language);
            showActiveLanguage(language, true);
          })
      });

      navbarWebSocketConnect();
    });

  })();
  