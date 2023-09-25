var oldImagePreview;

(() => {
  const card = document.getElementById('password-card');
  const inputs = card.querySelectorAll('input');
  inputs.forEach(input => {
    input.setAttribute('class', 'form-control');
  });


  const fileInput = document.getElementById('id_photo');
  const imagePreview = document.getElementById('profile-photo');
  const loadingImage = document.getElementById('loading-image');


  fileInput.addEventListener('change', () => {
    const selectedFile = fileInput.files[0];

    if (selectedFile) {
      const imageURL = URL.createObjectURL(selectedFile);
      oldImagePreview = imagePreview.src;
      loadingImage.style.display = 'block';
      imagePreview.src = imageURL;

      imagePreview.onload = function () {
        const width = this.width;
        const height = this.height;

        // Defina as proporções máximas aceitáveis
        const proporcaoMaxima = 1.75; 
        const proporcaoMinima = 0.75;

        // Calcule a proporção da imagem
        const proporcao = width / height;

        // Verifique se a proporção está dentro da faixa aceitável
        if (proporcao >= proporcaoMinima && proporcao <= proporcaoMaxima) {
            // A proporção está dentro da faixa aceitável, continue com o processamento ou exibição
            console.log('Imagem dentro da proporção aceitável');
        } else {
            // A imagem não está dentro da faixa aceitável, avise o usuário e redefina o input
            alert('Por favor, selecione uma imagem com proporção adequada (quadrada).');
            fileInput.value = ''; // Redefina o valor do input para remover o arquivo não válido
            imagePreview.src = oldImagePreview; // Redefina a imagem para a imagem anterior
        }
      };

      } else {
        loadingImage.style.display = 'none';
        imagePreview.src = '';
        imagePreview.style.display = 'none';
      }
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


