"""
ShopCart Service
Paths:
------
GET /shopcarts - Returns a list all of the ShopCarts
GET /shopcarts/{customer_id}/{product_id} - Returns the ShopCart with a given id number
POST /shopcarts - creates a new ShopCart record in the database
PUT /shopcarts/{customer_id}/{product_id} - updates a ShopCart record in the database
// TODO: Add more paths here
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
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )

######################################################################
# ADD A NEW SHOPCART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a ShopCart
    This endpoint will create a ShopCart based the data in the body that is posted
    """
    app.logger.info("Request to create a ShopCart")
    check_content_type("application/json")
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())
    shopcart.create()
    message = shopcart.serialize()
    location_url = url_for("get_shopcarts", customer_id=shopcart.customer_id, 
                                            product_id = shopcart.product_id, _external=True)

    app.logger.info("Shopcart for customer [%s] for product [%s] created.", shopcart.customer_id, shopcart.product_id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# RETRIEVE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>", methods=["GET"])
def get_shopcarts(customer_id):
    """
    Retrieve a single ShopCart
    This endpoint will return a ShopCart based on it's id
    """
    app.logger.info("Request for shopcart with id: %s", customer_id)
    shopcart = ShopCart.find(customer_id)
    if not shopcart:
        raise NotFound("ShopCart with id '{}' was not found.".format(customer_id))

    app.logger.info("Returning shopcart: %s", shopcart.name)
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:customer_id>/<int:product_id>", methods=["PUT"])
def update_shopcarts(customer_id, product_id):
    """
    Update a shopcart
    This endpoint will update a shopcart based the body that is posted
    """
    app.logger.info("Request to update shopcart with id [%s] for product [%s]", shopcart.customer_id, shopcart.product_id)
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
