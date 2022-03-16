"""
Test cases for ShopCart Model
"""
import logging
import unittest
import os
from service.models import ShopCart, DataValidationError, db
from service import app
from config import DATABASE_URI

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
        shopcart = ShopCart(name="MyCart1", price=100, quantity=1)
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.customer_id, None)
        self.assertEqual(shopcart.product_id, None)
        self.assertEqual(shopcart.name, "MyCart1")
        self.assertEqual(shopcart.price, 100)
        self.assertEqual(shopcart.quantity, 1)