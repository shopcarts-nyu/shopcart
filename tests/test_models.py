"""
Test cases for ShopCart Model
"""
import logging
import unittest
import os
from werkzeug.exceptions import NotFound
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
        ShopCartFactory.reset_sequence()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_shopcart(self):
        """Create a shopcart and assert that it exists"""
        shopcart = ShopCart(name="MyCart1", customer_id=12, product_id=3, price=100, quantity=1)
        self.assertTrue(shopcart is not None)
        self.assertEqual(shopcart.customer_id, 12)
        self.assertEqual(shopcart.product_id, 3)
        self.assertEqual(shopcart.name, "MyCart1")
        self.assertEqual(shopcart.price, 100)
        self.assertEqual(shopcart.quantity, 1)

    def test_read_a_shopcart(self):
        """Read a ShopCart"""
        shopcart = ShopCartFactory()
        logging.debug(shopcart)
        shopcart.create()
        self.assertEqual(shopcart.customer_id, 0)
        # Fetch it back 
        found_shopcart = shopcart.find_by_customer_id(shopcart.customer_id)
        items_in_found_shopcart = list(found_shopcart)
        self.assertEqual(len(items_in_found_shopcart), 1)
        self.assertEqual(items_in_found_shopcart[0].customer_id, shopcart.customer_id)
        self.assertEqual(items_in_found_shopcart[0].product_id, shopcart.product_id)
        self.assertEqual(items_in_found_shopcart[0].name, shopcart.name)
        self.assertEqual(items_in_found_shopcart[0].quantity, shopcart.quantity)
        self.assertEqual(items_in_found_shopcart[0].price, shopcart.price)

    def test_update_a_shopcart(self):
        """Update a shopcart"""
        shopcart = ShopCartFactory()
        logging.debug(shopcart)
        shopcart.create()
        logging.debug(shopcart)
        self.assertEqual(shopcart.customer_id, 0)
        self.assertEqual(shopcart.product_id, 0)
        logging.debug(shopcart.customer_id)
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
        self.assertEqual(shopcarts[0].customer_id, 0)
        self.assertEqual(shopcarts[0].product_id, 0)
        self.assertEqual(shopcarts[0].price, 1)
        self.assertEqual(shopcarts[0].quantity, 1)

    def test_delete_a_shopcart(self):
        """Delete a Shopcart"""
        shopcart = ShopCartFactory()
        logging.debug(shopcart)
        shopcart.create()
        self.assertEqual(len(shopcart.all()), 1)
        # delete the shopcart and make sure it isn't in the database
        shopcart.delete()
        self.assertEqual(len(shopcart.all()), 0)
    
    def test_list_all_shopcarts(self):
        """List ShopCarts in the database"""
        shopcarts = ShopCart.all()
        self.assertEqual(shopcarts, [])
        # Create 5 ShopCarts
        for i in range(5):
            shopcart = ShopCartFactory()
            shopcart.create()
        # See if we get back 5 shopcarts
        shopcarts = ShopCart.all()
        self.assertEqual(len(shopcarts), 5)

    def test_serialize_a_shopcart(self):
        """Test serialization of a ShopCart"""
        shopcart = ShopCartFactory()
        data = shopcart.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("customer_id", data)
        self.assertEqual(data["customer_id"], shopcart.customer_id)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], shopcart.product_id)
        self.assertIn("price", data)
        self.assertEqual(data["price"], shopcart.price)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], shopcart.quantity)

    def test_deserialize_a_shopcart(self):
        """Test deserialization of a ShopCart"""
        data = {
            "customer_id": 1,
            "product_id": 2,
            "name": "cart1",
            "price": 20.0,
            "quantity": 5,
        }
        shopcart = ShopCart()
        shopcart.deserialize(data)
        self.assertNotEqual(shopcart, None)
        self.assertEqual(shopcart.customer_id, 1)
        self.assertEqual(shopcart.product_id, 2)
        self.assertEqual(shopcart.name, "cart1")
        self.assertEqual(shopcart.price, 20.0)
        self.assertEqual(shopcart.quantity, 5)

    def test_deserialize_missing_data(self):
        """Test deserialization of a ShopCart with missing data"""
        data = {"customer_id": 1, "name": "test_cart", "price": 2}
        shopcart = ShopCart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        shopcart = ShopCart()
        self.assertRaises(DataValidationError, shopcart.deserialize, data)

    def test_find_shopcart(self):
        """Find a ShopCart by ID"""
        shopcarts = ShopCartFactory.create_batch(3)
        for shopcart in shopcarts:
            shopcart.create()
        logging.debug(shopcarts)
        # make sure they got saved
        self.assertEqual(len(ShopCart.all()), 3)
        # find the 2nd shopcart in the list
        shopcart = ShopCart.find((shopcarts[1].customer_id, shopcarts[1].product_id))
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.customer_id, shopcarts[1].customer_id)
        self.assertEqual(shopcart.product_id, shopcarts[1].product_id)
        self.assertEqual(shopcart.name, shopcarts[1].name)
        self.assertEqual(shopcart.price, shopcarts[1].price)

    def test_find_by_customer_id(self):
        """Find a ShopCart by customer id"""
        ShopCart(name="MyCart1", customer_id=12, product_id=3, price=100, quantity=1).create()
        ShopCart(name="MyCart2", customer_id=3, product_id=5, price=50, quantity=2).create()

        shopcarts = ShopCart.find_by_customer_id(3)
        self.assertEqual(shopcarts[0].price, 50)
        self.assertEqual(shopcarts[0].quantity, 2)
    
    def test_find_by_price(self):
        """Find a ShopCarts by price"""
        ShopCart(name="MyCart1", customer_id=12, product_id=3, price=100, quantity=1).create()
        ShopCart(name="MyCart2", customer_id=3, product_id=5, price=50, quantity=2).create()
        shopcarts = ShopCart.find_by_price(50)
        self.assertEqual(shopcarts[0].customer_id, 3)
        self.assertEqual(shopcarts[0].product_id, 5)
        self.assertEqual(shopcarts[0].quantity, 2)

    def test_find_by_quantity(self):
        """Find a ShopCarts by quantity"""
        ShopCart(name="MyCart1", customer_id=12, product_id=3, price=100, quantity=1).create()
        ShopCart(name="MyCart2", customer_id=3, product_id=5, price=50, quantity=2).create()
        shopcarts = ShopCart.find_by_quantity(2)
        self.assertEqual(shopcarts[0].customer_id, 3)
        self.assertEqual(shopcarts[0].product_id, 5)
        self.assertEqual(shopcarts[0].price, 50)


    def test_find_or_404_found(self):
        """Find or return 404 found"""
        shopcarts = ShopCartFactory.create_batch(3)
        for shopcart in shopcarts:
            shopcart.create()

        shopcart = ShopCart.find_or_404((shopcarts[1].product_id, shopcarts[1].product_id))
        self.assertIsNot(shopcart, None)
        self.assertEqual(shopcart.customer_id, shopcarts[1].customer_id)
        self.assertEqual(shopcart.name, shopcarts[1].name)
        self.assertEqual(shopcart.price, shopcarts[1].price)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, ShopCart.find_or_404, (0, 0))