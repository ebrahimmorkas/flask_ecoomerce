console.log("Hello World")
document.getElementById('signupForm').addEventListener('submit', (e) => {
    e.preventDefault()
    nameField = document.getElementById('name').value
    if(nameField === "")
    {
        alert("Name field should be not empty")
        return false
    }
    else
    {
        console.log(nameField)
        this.submit()
    }
})