document.getElementById('deleteBtn').addEventListener('click', (event) => {
    event.preventDefault();
})
function deleteProduct(id){
    console.log("Delere Request Receieved")
    fetch('/product/deleteProduct', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({productID: id})
    })
    .then(response => {
        // console.log(response.json())
        if(!response.ok){
            throw new Error("Something Went Wrong")
        }
        
        return response.json()
    })
    .then(data => {
        let table_body = document.getElementById('table-body');
        console.log(data)
        console.log(data.length)
        // for (let i = 0; i < data.length; i++) {
        //     console.log("Hello")
        //     let row = document.createElement("tr");
        //     let cell1 = document.createElement("td");
        //     cell1.innerText = data.data`${i}`[1];
        //     let cell2 = document.createElement("td");
        //     cell2.innerText = data.data`${i}`[2];
        //     let cell3 = document.createElement("td");
        //     cell3.innerText = data.data`${i}`[3];
        //     let cell4 = document.createElement("td");
        //     cell4.innerText = data.data`${i}`[5];
        //     let a1 = document.createElement("a")
        //     let a2 = document.createElement("a")
        //     let a3 = document.createElement("a")
        //     a1.innerText = "View"
        //     a2.innerText = "Update"
        //     a3.innerText = "Delete"
        //     // a3.href = 
        //     let cell5 = document.createElement("td");
        //     let cell6 = document.createElement("td");
        //     let cell7 = document.createElement("td");
        //     row.appendChild(cell1)
        //     row.appendChild(cell2)
        //     row.appendChild(cell3)
        //     row.appendChild(cell5)
        //     table_body.appendChild(row)
        //     location.reload()
        // }
        table_body.removeChild(document.getElementById(data.product))
    })
    .catch(error => {
        console.log(error)
    })
}