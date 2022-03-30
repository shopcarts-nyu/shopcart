"""
ShopCart Service
Paths:
------
GET /shopcarts - Returns a list all of the ShopCarts
POST /shopcarts - creates a new ShopCart record in the database
POST /shopcarts/{customer_id}/items - add an item to the shopcart for customer_id
GET /shopcarts/{customer_id} - Returns the ShopCart with a given id number
GET /shopcarts/{customer_id}/items - Returns the ShopCart with a given id number
GET /shopcarts/{customer_id}/items/{product_id} - Returns an item in the ShopCart with a given id number
PUT /shopcarts/{customer_id}/items/{product_id} - updates a ShopCart record in the database
DELETE /shopcarts/{customer_id} - deletes a ShopCart record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import ShopCart, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        {"message": "Welcome to ShopCarts!"},
        status.HTTP_200_OK,
    )

######################################################################
# ADD A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_empty_shopcarts():
    """
    Creates a ShopCart
    This endpoint will create a ShopCart based the data in the body that is posted
    """
    app.logger.info("Request to create a ShopCart")
    check_content_type("application/json")
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())
    # shopcart.create()
    message = {"customer_id": shopcart.customer_id}
    location_url = url_for("get_shopcarts", customer_id=shopcart.customer_id, _external=True)

    app.logger.info("Shopcart for customer [%s] created.", shopcart.customer_id)
    return make_response(
        message, status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# ADD A NEW ITEM TO SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items", methods=["POST"])
def create_shopcarts_with_item(customer_id):
    """
    Add an item to an existing ShopCart 
    This endpoint will create a ShopCart based the data in the body that is posted
    """
    app.logger.info("Request to create a ShopCart")
    check_content_type("application/json")
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())
    if shopcart.customer_id != customer_id:
        abort(status.HTTP_400_BAD_REQUEST, "Customer ID in data must be {} as requested in URI. ".format(customer_id)) 
    shopcart.create()
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts_with_item_id", customer_id=shopcart.customer_id, 
                                            product_id=shopcart.product_id, _external=True)

    app.logger.info("Shopcart for customer [%s] for product [%s] created.", shopcart.customer_id, shopcart.product_id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# RETRIEVE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["GET"])
@app.route("/shopcarts/<int:customer_id>/items", methods=["GET"])
def get_shopcarts(customer_id):
    """
    Retrieve a single ShopCart
    This endpoint will return a ShopCart based on it's id
    """
    app.logger.info("Request for shopcart with id: %s", customer_id)
    shopcart = ShopCart.find_by_customer_id(customer_id)
    if shopcart.count() == 0:
        raise NotFound("ShopCart with id '{}' was not found.".format(customer_id))

    results = [product.serialize() for product in shopcart]
    app.logger.info("Returning %d shopcarts", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK) 

######################################################################
# RETRIEVE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["GET"])
def get_shopcarts_with_item_id(customer_id, product_id):
    """
    Retrieve a single ShopCart
    This endpoint will return a ShopCart based on it's id
    """
    app.logger.info("Request for shopcart with id: %s", customer_id)
    shopcart = ShopCart.find((customer_id, product_id))
    if not shopcart:
        raise NotFound("ShopCart with id '{}' was not found.".format(customer_id))

    app.logger.info("Returning shopcart: %s", shopcart.name)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK) 

######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["PUT"])
def update_shopcarts(customer_id, product_id):
    """
    Update a shopcart
    This endpoint will update a shopcart based the body that is posted
    """
    app.logger.info("Request to update shopcart with id [%s] for product [%s]", customer_id, product_id)
    check_content_type("application/json")
    shopcart = ShopCart.find((customer_id, product_id))
    if not shopcart:
        raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format((customer_id, product_id)))
    shopcart.deserialize(request.get_json())
    shopcart.customer_id = customer_id
    shopcart.product_id= product_id
    shopcart.update()

    app.logger.info("shopcart with ID [%s] for product [%s] updated.", shopcart.customer_id, shopcart.product_id)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A SHOPCART (INCLUDING ALL ITEMS IN IT)
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["DELETE"])
def delete_shopcarts(customer_id):
    """
    Delete a Shopcart
    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %s", customer_id)
    shopcarts = ShopCart.find_by_customer_id(customer_id)
    for shopcart in shopcarts:
        shopcart.delete()

    app.logger.info("Shopcart with ID [%s] delete complete.", customer_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# DELETE A SHOPCART (A SPECIFIC ITEM)
######################################################################
@app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["DELETE"])
def delete_item_shopcarts(customer_id,product_id):
    """
    Delete a Shopcart
    This endpoint will delete a specific product item in Shopcart based the id specified in the path
    """
    app.logger.info("Request to delete product with id [%s] for shopcart [%s]", customer_id, product_id)
    shopcart = ShopCart.find((customer_id, product_id))
    if not shopcart:
        raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format((customer_id, product_id)))
    shopcart.delete()

    app.logger.info("shopcart with ID [%s] for product [%s] deleted.", shopcart.customer_id, shopcart.product_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
# LIST ALL SHOPCARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the ShopCarts"""
    app.logger.info("Request for shopcart list")
    shopcarts = []
    price = request.args.get("price")
    quantity = request.args.get("quantity")
    if price:
        shopcarts = ShopCart.find_by_price(price)
    elif quantity:
        shopcarts = ShopCart.find_by_quantity(quantity)
    else:
        shopcarts = ShopCart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    app.logger.info("Returning %d shopcarts", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK) 

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """ Initializes the SQLAlchemy app """
    global app
    ShopCart.init_db(app)

def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
