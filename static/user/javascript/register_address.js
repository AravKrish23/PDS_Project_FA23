// register_address.js
function openModal() {
    document.getElementById("selectZipcodeModal").style.display = "block";
}

function closeModal() {
    document.getElementById("selectZipcodeModal").style.display = "none";
}

// Close the modal if the user clicks outside of it
window.onclick = function(event) {
    var modal = document.getElementById("selectZipcodeModal");
    if (event.target === modal) {
        closeModal();
    }
};
