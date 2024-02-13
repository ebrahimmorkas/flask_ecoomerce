// Function to open the modal
function deleteModal() {
    document.getElementById("myModalDel").style.display = "flex";
}

// Function to close the modal
function closeDelModal() {
    document.getElementById("myModalDel").style.display = "none";
    location.reload()
}

document.getElementById('modalBtnDel').addEventListener('click', event => {
    event.preventDefault()
    // console.log("HI")
    document.getElementById('myModalDel').style.visibility='visible'
})