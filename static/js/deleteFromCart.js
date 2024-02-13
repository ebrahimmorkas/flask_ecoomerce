function deleteFromCart(productID) {
    id = productID
    fetch('/deleteFromCart', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            "productID": productID
        })
    })
    .then(response => {
        if(!response.ok) {
            throw new Error("Something went Wrong")
        }
        return response.json()
    })
    .then(data => {
        document.getElementById('modalBtnDel').click()
    })
}