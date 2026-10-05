document.querySelectorAll('input[type="file"][data-preview]').forEach(input => {
  input.addEventListener('change', () => {
    const file = input.files && input.files[0];
    const img = document.getElementById(input.dataset.preview);
    if (!img) return;
    if (file) { img.src = URL.createObjectURL(file); img.style.display = 'block'; }
    else { img.removeAttribute('src'); img.style.display = 'none'; }
  });
});
