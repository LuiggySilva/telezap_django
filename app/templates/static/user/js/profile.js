(() => {
    const card = document.getElementById('password-card');
    const inputs = card.querySelectorAll('input');
    inputs.forEach(input => {
        input.setAttribute('class', 'form-control');
    });
  
    
    const fileInput = document.getElementById('id_photo');
    const profilePhoto = document.getElementById('profile-photo');
    
    fileInput.addEventListener('change', () => {
      const selectedFile = fileInput.files[0];
      const fileName = selectedFile.name;
    
      const reader = new FileReader();
      reader.onload = (event) => {
        const fileURL = event.target.result;

        profilePhoto.setAttribute('src', fileURL);
        profilePhoto.setAttribute('alt', fileName);
      };
      reader.readAsDataURL(selectedFile);
    });


    const textarea = document.getElementById('id_status');
    const emojis = document.querySelectorAll('.emoji-icon');
    emojis.forEach(emoji => {
      emoji.addEventListener('click', () => {
        if (parseInt(textarea.getAttribute('maxlength')) > textarea.value.length) {
          const emojiValue = emoji.innerHTML;
          textarea.value += emojiValue;
        }
      });
    });

})();


