"""
Test cases for ShopCart Model
"""
import logging
import unittest
import os
from service.models import ShopCart, DataValidationError, db
from service import app
from config import DATABASE_URI
from .factories import ShopCartFactory

######################################################################
#  S H O P C A R T   M O D E L   T E S T   C A S E S
######################################################################
class TestShopCart(unittest.TestCase):
    """ Test Cases for ShopCart Model """
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        ShopCart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """Create a shopcart and assert that it exists"""
        shopcart = ShopCart(name="MyCart1")
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.name, "MyCart1")

    def test_update_a_shopcart(self):
        """Update a shopcart"""
        shopcart = ShopCartFactory()
        logging.debug(shopcart)
        shopcart.create()
        logging.debug(shopcart)
        self.assertEqual(shopcart.customer_id, 1)
        self.assertEqual(shopcart.product_id, 1)
        # Change it an save it
        shopcart.price = 1
        shopcart.quantity = 1
        customer_id = shopcart.customer_id
        product_id = shopcart.product_id
        shopcart.update()
        self.assertEqual(shopcart.customer_id, customer_id)
        self.assertEqual(shopcart.product_id, product_id)
        self.assertEqual(shopcart.price, 1)
        self.assertEqual(shopcart.quantity, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        shopcarts = ShopCart.all()
        self.assertEqual(len(shopcarts), 1)
        self.assertEqual(shopcarts[0].customer_id, 1)
        self.assertEqual(shopcarts[0].product_id, 1)
        self.assertEqual(shopcarts[0].price, 1)
        self.assertEqual(shopcarts[0].quantity, 1)