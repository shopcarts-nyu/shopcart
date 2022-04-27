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
PUT /shopcarts/{customer_id}/checkout - checkout all items in the shopcart
PUT /shopcarts/{customer_id}/items/{product_id}/checkout - checkout one item in the shopcart
DELETE /shopcarts/{customer_id} - deletes a ShopCart record in the database
"""

import os
import sys
import logging
from flask import Flask, request, url_for, make_response, abort
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import ShopCart, DataValidationError, DatabaseConnectionError
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
    """Base URL for our service"""
    return app.send_static_file("index.html")

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='ShopCart Demo REST API Service',
          description='This is a sample server ShopCart store server.',
          default='shopcartss',
          default_label='ShopCart shop operations',
          doc='/apidocs' # default also could use doc='/apidocs/'
         )

# Define the model so that the docs reflect what can be sent
create_model = api.model('ShopCart', {
    'customer_id': fields.Integer(required=True,
                          description='The customer id of the ShopCart'),
    'product_id': fields.Integer(required=True,
                          description='The product id of the ShopCart'),
    'name': fields.String(required=True,
                          description='The name of ShopCart'),
    'quantity': fields.Integer(required=True,
                            description='The quantity of an item in the ShopCart'),
    'price': fields.Float(required=True, 
                        description='The price of an item in the ShopCart')
    })

# query string arguments
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument('product_id', type=str, required=False, help='List ShopCarts by product id')
shopcart_args.add_argument('quantity', type=str, required=False, help='List ShopCarts by quantity')
shopcart_args.add_argument('price', type=inputs.boolean, required=False, help='List ShopCarts by price')

######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE

######################################################################
#  PATH: /shopcarts
######################################################################
@api.route('/shopcarts', strict_slashes=False)
class ShopCartCollection(Resource):
    """ Handles all interactions with collections of ShopCarts """
    #------------------------------------------------------------------
    # LIST ALL OR QUERY SHOPCARTS
    #------------------------------------------------------------------
    @api.doc('list_shopcarts')
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(create_model)
    def get(self):
        """Returns all of the products in ShopCarts"""
        app.logger.info("Request for product list")
        shopcarts = []
        price = request.args.get("price")
        quantity = request.args.get("quantity")
        product_id = request.args.get("product_id")
        if price:
            shopcarts = ShopCart.find_by_price(price)
        elif quantity:
            shopcarts = ShopCart.find_by_quantity(quantity)
        elif product_id:
            shopcarts = ShopCart.find_by_product_id(product_id)    
        else:
            shopcarts = ShopCart.all()

        results = [shopcart.serialize() for shopcart in shopcarts]
        app.logger.info("Returning %d shopcarts", len(results))
        return results, status.HTTP_200_OK
    
    ######################################################################
    # ADD A NEW SHOPCART
    ######################################################################
    @api.doc('create_shopcarts')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    def post(self):
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
        location_url = api.url_for(ShopCartResource, customer_id=shopcart.customer_id, _external=True)

        app.logger.info("Shopcart for customer [%s] created.", shopcart.customer_id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}

    # @api.doc('delete_all_shopcarts')
    # @api.response(204, 'All ShopCarts deleted')
    # def delete(self):

######################################################################
#  PATH: /shopcarts/{int:customer_id}
#  PATH: /shopcarts/{int:customer_id}/items
######################################################################
@api.route('/shopcarts/<int:customer_id>')
@api.route('/shopcarts/<int:customer_id>/items')
@api.param('customer_id', 'The ShopCart identifier')
class ShopCartResource(Resource):
    """
    ShopCartResource class
    Allows the manipulation of a single ShopCart
    GET /shopcart/{customer_id} - Returns a ShopCart with the customer_id
    # PUT /shopcart/{customer_id} - Update a ShopCart with the customer_id
    DELETE /shopcart{customer_id} -  Deletes a ShopCart with the customer_id
    """

    #------------------------------------------------------------------
    # RETRIEVE A SHOPCART
    #------------------------------------------------------------------
    @api.doc('get_shopcarts')
    @api.response(404, 'ShopCart not found')
    @api.marshal_with(create_model)
    def get(self, customer_id):
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
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A SHOPCART
    #------------------------------------------------------------------
    @api.doc('delete_shopcarts')
    @api.response(204, 'ShopCart deleted')
    def delete(self, customer_id):
        """
        Delete a Shopcart
        This endpoint will delete a Shopcart based the id specified in the path
        """
        app.logger.info("Request to delete shopcart with id: %s", customer_id)
        shopcarts = ShopCart.find_by_customer_id(customer_id)
        for shopcart in shopcarts:
            shopcart.delete()

        app.logger.info("Shopcart with ID [%s] delete complete.", customer_id)
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /shopcarts/{int:customer_id}/checkout
######################################################################
@api.route('/shopcarts/<int:customer_id>/checkout')
@api.param('customer_id', 'The ShopCart identifier')
class CheckoutResource(Resource):
    """ Purchase actions on a ShopCart """
    @api.doc('checkout_shopcarts')
    @api.response(404, 'ShopCart not found')
    @api.response(409, 'The ShopCart is not available for checkout ')
    def put(self, customer_id):
        """
        Checkout a Shopcart
        This endpoint will checkout a Shopcart based the id specified in the path. 
        The shopcart will be emptied as a result.
        """
        app.logger.info("Request to checkout shopcart with id: %s", customer_id)

        # Placeholder to call the orders api
        shopcarts = ShopCart.find_by_customer_id(customer_id)
        for shopcart in shopcarts:
            shopcart.delete()

        app.logger.info("Shopcart with ID [%s] checkout complete.", customer_id)
        return make_response("", status.HTTP_200_OK)

######################################################################
#  PATH: /shopcarts/<int:customer_id>/items
######################################################################
@api.route('/shopcarts/<int:customer_id>/items')
@api.param('customer_id', 'The ShopCart identifier')
class ItemCollection(Resource):
    """ Handles all interactions with collections of items in ShopCarts """
    #------------------------------------------------------------------
    # ADD A NEW ITEM WITH SHOPCART
    #------------------------------------------------------------------
    @api.doc('create_shopcarts_with_item')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    def post(self, customer_id):
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
        if ShopCart.find((shopcart.customer_id, shopcart.product_id)):
            abort(status.HTTP_400_BAD_REQUEST, 
                "ShopCart with customer id = {} and product id = {} already exists"
                .format(customer_id, shopcart.product_id)) 
        shopcart.create()
        message = shopcart.serialize()
        location_url = api.url_for(ItemResource, customer_id=shopcart.customer_id, 
                                                product_id=shopcart.product_id, _external=True)
        app.logger.info("Shopcart for customer [%s] for product [%s] created.", shopcart.customer_id, shopcart.product_id)
        return message, status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  PATH: /shopcarts/{int:customer_id}/items/{int:product_id}
######################################################################
@api.route('/shopcarts/<int:customer_id>/items/<int:product_id>')
@api.param('customer_id', 'The ShopCart identifier')
@api.param('product_id', 'The ShopCart item identifier')
class ItemResource(Resource):
    """
    ItemResource class
    Allows the manipulation of a single ShopCart
    GET /shopcart/{customer_id}/items/<product_id> - Returns a ShopCart with the customer_id and product_id
    PUT /shopcart/{customer_id}/items/<product_id> - Update a ShopCart with the customer_id and product_id
    DELETE /shopcart{customer_id}/items/<product_id> -  Deletes a ShopCart with the customer_id and product_id
    """

    #------------------------------------------------------------------
    # RETRIEVE A SHOPCART
    #------------------------------------------------------------------
    @api.doc('get_shopcarts_with_item_id')
    @api.response(404, 'ShopCart not found')
    @api.marshal_with(create_model)
    def get(self, customer_id, product_id):
        """
        Retrieve a single ShopCart
        This endpoint will return a ShopCart based on it's id
        """
        app.logger.info("Request for shopcart with id: %s", customer_id)
        shopcart = ShopCart.find((customer_id, product_id))
        if not shopcart:
            raise NotFound("ShopCart with id '{}' was not found.".format(customer_id))

        app.logger.info("Returning shopcart: %s", shopcart.name)
        return shopcart.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # UPDATE AN EXISTING SHOPCART
    #------------------------------------------------------------------
    @api.doc('update_shopcarts')
    @api.response(404, 'ShopCart not found')
    @api.response(400, 'The posted Pet data was not valid')
    @api.expect(create_model)
    def put(self, customer_id, product_id):
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
        return shopcart.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE A SHOPCART WITH AN ITEM
    #------------------------------------------------------------------
    @api.doc('delete_item_shopcarts')
    @api.response(204, 'All ShopCarts deleted')
    def delete(self, customer_id, product_id):
        """
        Delete a Shopcart
        This endpoint will delete a specific product item in Shopcart based the id specified in the path
        """
        app.logger.info("Request to delete product with id [%s] for shopcart [%s]", customer_id, product_id)
        shopcart = ShopCart.find((customer_id, product_id))
        if not shopcart:
            raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format(customer_id, product_id))
        shopcart.delete()

        app.logger.info("shopcart with ID [%s] for product [%s] deleted.", shopcart.customer_id, shopcart.product_id)
        return '', status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /shopcarts/{int:customer_id}/items/{int:product_id}/checkout
######################################################################
@api.route('/shopcarts/<int:customer_id>/items/<int:product_id>/checkout')
@api.param('customer_id', 'The ShopCart identifier')
@api.param('product_id', 'The ShopCart item identifier')
class CheckoutItemResource(Resource):
    """ Purchase actions on a ShopCart """
    @api.doc('checkout_item_shopcarts')
    @api.response(404, 'ShopCart not found')
    def put(self, customer_id, product_id):
        """
        Checkout an item in a Shopcart
        This endpoint will checkout a specific product item in Shopcart based the id specified in the path
        """
        app.logger.info("Request to checkout product with id [%s] for shopcart [%s]", customer_id, product_id)
        shopcart = ShopCart.find((customer_id, product_id))
        if not shopcart:
            raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format(customer_id, product_id))
        # Placeholder to call the orders api
        shopcart.delete()

        app.logger.info("shopcart with ID [%s] for product [%s] checked out.", shopcart.customer_id, shopcart.product_id)
        return make_response("", status.HTTP_200_OK)

# ######################################################################
# # ADD A NEW ITEM TO SHOPCART
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>/items", methods=["POST"])
# def create_shopcarts_with_item(customer_id):
#     """
#     Add an item to an existing ShopCart 
#     This endpoint will create a ShopCart based the data in the body that is posted
#     """
#     app.logger.info("Request to create a ShopCart")
#     check_content_type("application/json")
#     shopcart = ShopCart()
#     shopcart.deserialize(request.get_json())
#     if shopcart.customer_id != customer_id:
#         abort(status.HTTP_400_BAD_REQUEST, "Customer ID in data must be {} as requested in URI. ".format(customer_id)) 
#     if ShopCart.find((shopcart.customer_id, shopcart.product_id)):
#         abort(status.HTTP_400_BAD_REQUEST, 
#             "ShopCart with customer id = {} and product id = {} already exists"
#             .format(customer_id, shopcart.product_id)) 
#     shopcart.create()
#     message = shopcart.serialize()
#     location_url = url_for("get_shopcarts_with_item_id", customer_id=shopcart.customer_id, 
#                                             product_id=shopcart.product_id, _external=True)

#     app.logger.info("Shopcart for customer [%s] for product [%s] created.", shopcart.customer_id, shopcart.product_id)
#     return make_response(
#         jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
#     )

# ######################################################################
# # RETRIEVE A SHOPCART
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>", methods=["GET"])
# @api.route("/shopcarts/<int:customer_id>/items", methods=["GET"])
# def get_shopcarts(customer_id):
#     """
#     Retrieve a single ShopCart
#     This endpoint will return a ShopCart based on it's id
#     """
#     app.logger.info("Request for shopcart with id: %s", customer_id)
#     shopcart = ShopCart.find_by_customer_id(customer_id)
#     if shopcart.count() == 0:
#         raise NotFound("ShopCart with id '{}' was not found.".format(customer_id))

#     results = [product.serialize() for product in shopcart]
#     app.logger.info("Returning %d shopcarts", len(results))
#     return make_response(jsonify(results), status.HTTP_200_OK) 

# ######################################################################
# # RETRIEVE A SHOPCART
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["GET"])
# def get_shopcarts_with_item_id(customer_id, product_id):
#     """
#     Retrieve a single ShopCart
#     This endpoint will return a ShopCart based on it's id
#     """
#     app.logger.info("Request for shopcart with id: %s", customer_id)
#     shopcart = ShopCart.find((customer_id, product_id))
#     if not shopcart:
#         raise NotFound("ShopCart with id '{}' was not found.".format(customer_id))

#     app.logger.info("Returning shopcart: %s", shopcart.name)
#     return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK) 

# ######################################################################
# # UPDATE AN EXISTING SHOPCART
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["PUT"])
# def update_shopcarts(customer_id, product_id):
#     """
#     Update a shopcart
#     This endpoint will update a shopcart based the body that is posted
#     """
#     app.logger.info("Request to update shopcart with id [%s] for product [%s]", customer_id, product_id)
#     check_content_type("application/json")
#     shopcart = ShopCart.find((customer_id, product_id))
#     if not shopcart:
#         raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format((customer_id, product_id)))
#     shopcart.deserialize(request.get_json())
#     shopcart.customer_id = customer_id
#     shopcart.product_id= product_id
#     shopcart.update()

#     app.logger.info("shopcart with ID [%s] for product [%s] updated.", shopcart.customer_id, shopcart.product_id)
#     return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

# ######################################################################
# # DELETE A SHOPCART (INCLUDING ALL ITEMS IN IT)
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>", methods=["DELETE"])
# def delete_shopcarts(customer_id):
#     """
#     Delete a Shopcart
#     This endpoint will delete a Shopcart based the id specified in the path
#     """
#     app.logger.info("Request to delete shopcart with id: %s", customer_id)
#     shopcarts = ShopCart.find_by_customer_id(customer_id)
#     for shopcart in shopcarts:
#         shopcart.delete()

#     app.logger.info("Shopcart with ID [%s] delete complete.", customer_id)
#     return make_response("", status.HTTP_204_NO_CONTENT)


# ######################################################################
# # DELETE A SHOPCART (A SPECIFIC ITEM)
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["DELETE"])
# def delete_item_shopcarts(customer_id,product_id):
#     """
#     Delete a Shopcart
#     This endpoint will delete a specific product item in Shopcart based the id specified in the path
#     """
#     app.logger.info("Request to delete product with id [%s] for shopcart [%s]", customer_id, product_id)
#     shopcart = ShopCart.find((customer_id, product_id))
#     if not shopcart:
#         raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format((customer_id, product_id)))
#     shopcart.delete()

#     app.logger.info("shopcart with ID [%s] for product [%s] deleted.", shopcart.customer_id, shopcart.product_id)
#     return make_response("", status.HTTP_204_NO_CONTENT)

# ######################################################################
# # CHECKOUT A SHOPCART (INCLUDING ALL ITEMS IN IT)
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>/checkout", methods=["PUT"])
# def checkout_shopcarts(customer_id):
#     """
#     Checkout a Shopcart
#     This endpoint will checkout a Shopcart based the id specified in the path. 
#     The shopcart will be emptied as a result.
#     """
#     app.logger.info("Request to checkout shopcart with id: %s", customer_id)

#     # Placeholder to call the orders api
#     shopcarts = ShopCart.find_by_customer_id(customer_id)
#     for shopcart in shopcarts:
#         shopcart.delete()

#     app.logger.info("Shopcart with ID [%s] checkout complete.", customer_id)
#     return make_response("", status.HTTP_200_OK)


# ######################################################################
# # CHECKOUT A SHOPCART (A SPECIFIC ITEM)
# ######################################################################
# @api.route("/shopcarts/<int:customer_id>/items/<int:product_id>/checkout", methods=["PUT"])
# def checkout_item_shopcarts(customer_id,product_id):
#     """
#     Checkout an item in a Shopcart
#     This endpoint will checkout a specific product item in Shopcart based the id specified in the path
#     """
#     app.logger.info("Request to checkout product with id [%s] for shopcart [%s]", customer_id, product_id)
#     shopcart = ShopCart.find((customer_id, product_id))
#     if not shopcart:
#         raise NotFound("Shopcart with id '{}' for product '{}' was not found.".format((customer_id, product_id)))
#     # Placeholder to call the orders api
#     shopcart.delete()

#     app.logger.info("shopcart with ID [%s] for product [%s] checked out.", shopcart.customer_id, shopcart.product_id)
#     return make_response("", status.HTTP_200_OK)

# ######################################################################
# # LIST ALL SHOPCARTS AND QUERY PRICE, QUANTITY, PRODUCTID
# ######################################################################
# @api.route("/shopcarts", methods=["GET"])
# @api.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["GET"])
# def list_products():
#     """Returns all of the products in ShopCarts"""
#     app.logger.info("Request for product list")
#     shopcarts = []
#     price = request.args.get("price")
#     quantity = request.args.get("quantity")
#     product_id = request.args.get("product_id")
#     if price:
#         shopcarts = ShopCart.find_by_price(price)
#     elif quantity:
#         shopcarts = ShopCart.find_by_quantity(quantity)
#     elif product_id:
#         shopcarts = ShopCart.find_by_product_id(product_id)    
#     else:
#         shopcarts = ShopCart.all()

#     results = [shopcart.serialize() for shopcart in shopcarts]
#     app.logger.info("Returning %d shopcarts", len(results))
#     return make_response(jsonify(results), status.HTTP_200_OK)

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
