document.getElementById('searchBtn').addEventListener('click', () => {
    let productID = document.getElementById('search').value
    fetch('/product/searchProduct', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({productID: productID})
    })
    .then(response => {
        if(!response.ok){
            throw new Error("Something Went Wrong")
        }
        return response.json();
    })
    .then(data => {
        if ('msg' in data && data.msg === 'The given ID does not exist') {
            document.getElementById('errorDiv').innerHTML="<small></b>The given ID does not exist</b></small>"
        } else {
            // Handle actual product information
            document.getElementById("productName").value = data.productName;
            document.getElementById("productCategory").value = data.productCategory;
            document.getElementById("productPrice").value = data.productPrice;
            document.getElementById("productDescription").value = data.productDescription;
            document.getElementById("productQuantity").value = data.productQuantity;
            // Handle image and zip filenames if needed
        }
    })
    .catch(error => {
        console.log("Error" + error)
    })
})
