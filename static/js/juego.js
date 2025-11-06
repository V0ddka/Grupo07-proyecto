

document.addEventListener('DOMContentLoaded', function () {
  const overlay = document.querySelector('.overlay');
  const botonCerrar = document.getElementById('botoncerrar');

  // Solo si el overlay existe (cuando hay result)
  if (overlay && botonCerrar) {
    botonCerrar.addEventListener('click', function () {
      // Oculpamos el overlay añadiendo la clase "oculto"
      overlay.classList.add('oculto');
    });
  }
});