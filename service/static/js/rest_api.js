$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.customer_id);
        $("#product_id").val(res.product_id);
        $("#shopcart_name").val(res.name);
        $("#shopcart_quantity").val(res.quantity);
        $("#shopcart_price").val(res.quantity);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val("");
        $("#product_id").val("");
        $("#shopcart_name").val("");
        $("#shopcart_quantity").val("");
        $("#shopcart_price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a ShopCart
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let product_id = $("#product_id").val();
        let name = $("#shopcart_name").val();
        let quantity = $("#shopcart_quantity").val();
        let price = $("#shopcart_price").val();

        let data = {
            "customer_id": customer_id,
            "product_id": product_id,
            "name": name,
            "quantity": quantity,
            "price": price,
        };

        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "POST",
            url: `/shopcarts/${customer_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a ShopCart
    // ****************************************

    $("#update-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let product_id = $("#product_id").val();
        let name = $("#shopcart_name").val();
        let quantity = $("#shopcart_quantity").val();
        let price = $("#shopcart_price").val();

        let data = {
            "customer_id": customer_id,
            "product_id": product_id,
            "name": name,
            "quantity": quantity,
            "price": price,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${customer_id}/items/${product_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a ShopCart or an item in the ShopCart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        let my_url = `/shopcarts/${customer_id}`;
        if (product_id != "") {
            // Checkout one item in a shopcart
            my_url += `/items/${product_id}`;
        }

        let ajax = $.ajax({
            type: "GET",
            url: my_url,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a ShopCart or an item in ShopCart
    // ****************************************

    $("#delete-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let product_id = $("#product_id").val();
        $("#flash_message").empty();

        let my_url = `/shopcarts/${customer_id}`;
        if (product_id != "") {
            // Delete one item in a shopcart
            my_url += `/items/${product_id}`;
        }

        let ajax = $.ajax({
            type: "DELETE",
            url: my_url,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("ShopCart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customer_id").val("");
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a ShopCart
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#shopcart_name").val();
        let quantity = $("#shopcart_quantity").val();
        let price = $("#shopcart_price").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (quantity) {
            if (queryString.length > 0) {
                queryString += '&quantity=' + quantity
            } else {
                queryString += 'quantity=' + quantity
            }
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            } else {
                queryString += 'price=' + price
            }
        }
        if (queryString.length != 0) {
            queryString = "?" + queryString
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '</tr></thead><tbody>'
            let firstShopCart = "";
            for(let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                table +=  `<tr id="row_${i}"><td>${shopcart.customer_id}</td><td>${shopcart.product_id}</td><td>${shopcart.name}</td><td>${shopcart.quantity}</td><td>${shopcart.price}</td></tr>`;
                if (i == 0) {
                    firstShopCart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstShopCart != "") {
                update_form_data(firstShopCart)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Checkout a ShopCart
    // ****************************************

    $("#checkout-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let product_id = $("#product_id").val();

        let my_url = `/shopcarts/${customer_id}`;
        if (product_id != "") {
            // Checkout one item in a shopcart
            my_url += `/items/${product_id}`;
        }
        my_url += "/checkout";

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: my_url,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("ShopCart has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

})
