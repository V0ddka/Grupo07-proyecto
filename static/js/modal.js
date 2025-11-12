const btnAbrirModal = document.getElementById('btn-abrir-modal');
const btnCerrarModal = document.getElementById('btn-cerrar-modal');
const modal = document.getElementById('modal-container');

btnAbrirModal.addEventListener("click",()=>{
    modal.classList.add('show');
})

btnCerrarModal.addEventListener("click",()=>{
    modal.classList.remove('show');
})