"""
TestYourResourceModel API Service Test Suite
Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import status  # HTTP Status Codes
from service.models import db
from service.routes import app, init_db
from .factories import ShopCartFactory
from config import DATABASE_URI

BASE_URL = "/shopcarts"
CONTENT_TYPE_JSON = "application/json"
######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopCart(TestCase):
    """ REST API Server Tests """
    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_shopcart(self):
        """Create a new shopcart"""
        test_shopcart = ShopCartFactory()
        logging.debug(test_shopcart)
        resp = self.app.post(
            BASE_URL, json=test_shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], test_shopcart.name, "Names do not match")
        self.assertEqual(
            new_shopcart["price"], test_shopcart.price, "Categories do not match"
        )
        self.assertEqual(
            new_shopcart["quantity"], test_shopcart.quantity, "Availability does not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], test_shopcart.name, "Names do not match")
        self.assertEqual(
            new_shopcart["price"], test_shopcart.price, "Categories do not match"
        )
        self.assertEqual(
            new_shopcart["quantity"], test_shopcart.quantity, "Availability does not match"
        )

    def test_update_shopcart(self):
        """Update an existing ShopCart"""
        # create a shopcart to update
        test_shopcart = ShopCartFactory()
        resp = self.app.post(
            BASE_URL, json=test_shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = resp.get_json()
        logging.debug(new_shopcart)
        new_shopcart["price"] = -1
        resp = self.app.put(
            "/shopcarts/{}/{}".format(new_shopcart["customer_id"], new_shopcart["product_id"]),
            json=new_shopcart,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["price"], -1)
