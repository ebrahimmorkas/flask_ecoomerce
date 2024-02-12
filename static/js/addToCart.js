function addToCart(productID) {
    fetch('/addToCart', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"productID": productID})
    })
    .then(response => {
        if(!response.ok){
            throw new Error("Something went wrong")
        }
        return response.json()
    })
    .then(data => {
        if(data.msg == "Product added to cart") {
            document.getElementById('modalBtn').click()
            // console.log("Product added successfully")
        }
        else {
            console.log("Couldn't add product")
        }
    })
    .catch(error => {
        console.log(error)
    })
}