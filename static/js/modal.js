// Function to open the modal
function openModal() {
    document.getElementById("myModal").style.display = "flex";
}

// Function to close the modal
function closeModal() {
    document.getElementById("myModal").style.display = "none";
}

document.getElementById('modalBtn').addEventListener('click', event => {
    event.preventDefault()
    // console.log("HI")
    document.getElementById('myModal').style.visibility='visible'
})