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

    def _create_shopcarts(self, count):
        """Factory method to create shopcarts in bulk"""
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopCartFactory()
            resp = self.app.post(
                f'{BASE_URL}/{test_shopcart.customer_id}/items', 
                json=test_shopcart.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test shopcart"
            )
            new_shopcart = resp.get_json()
            test_shopcart.customer_id = new_shopcart["customer_id"]
            test_shopcart.product_id = new_shopcart["product_id"]
            shopcarts.append(test_shopcart)
        return shopcarts

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_empty_shopcart(self):
        """Create an empty shopcart"""
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
        self.assertEqual(new_shopcart["customer_id"], test_shopcart.customer_id, 
                        "Customer id do not match")
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_shopcart_with_item(self):
        """Create a ShopCart with item in it"""
        # get the id of a shopcart
        shopcart = self._create_shopcarts(1)[0]
        test_shopcart = ShopCartFactory()
        test_shopcart.customer_id = shopcart.customer_id
        logging.debug(test_shopcart)
        resp = self.app.post(
            "/shopcarts/{}/items".format(test_shopcart.customer_id), 
            json=test_shopcart.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], test_shopcart.name, "Names do not match")
        self.assertEqual(
            new_shopcart["price"], test_shopcart.price, "Prices do not match"
        )
        self.assertEqual(
            new_shopcart["quantity"], test_shopcart.quantity, "Quantities does not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_shopcart = resp.get_json()
        self.assertEqual(new_shopcart["name"], test_shopcart.name, "Names do not match")
        self.assertEqual(
            new_shopcart["price"], test_shopcart.price, "Prices do not match"
        )
        self.assertEqual(
            new_shopcart["quantity"], test_shopcart.quantity, "Quantities does not match"
        )

    def test_create_dup_shopcarts(self):
        """Create a ShopCart with item in it"""
        # get the id of a shopcart
        shopcart = self._create_shopcarts(1)[0]
        test_shopcart = ShopCartFactory()
        test_shopcart.customer_id = shopcart.customer_id
        logging.debug(test_shopcart)
        resp = self.app.post(
            "/shopcarts/{}/items".format(test_shopcart.customer_id), 
            json=test_shopcart.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        resp = self.app.post(
            "/shopcarts/{}/items".format(test_shopcart.customer_id), 
            json=test_shopcart.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_shopcart(self):
        """Get a single ShopCart"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.get(
            "/shopcarts/{}".format(test_shopcart.customer_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], test_shopcart.name)
    
    def test_get_shopcart_alt_route(self):
        """Get a single ShopCart"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.get(
            "/shopcarts/{}/items".format(test_shopcart.customer_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], test_shopcart.name)
    
    def test_get_shopcart_item(self):
        """Get a single ShopCart"""
        # get the id of a shopcart
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.get(
            "/shopcarts/{}/items/{}".format(test_shopcart.customer_id, 
                test_shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_shopcart.name)

    def test_update_shopcart(self):
        """Update an existing ShopCart"""
        # create a shopcart to update
        test_shopcart = ShopCartFactory()
        resp = self.app.post(
            f'{BASE_URL}/{test_shopcart.customer_id}/items', 
            json=test_shopcart.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the shopcart
        new_shopcart = resp.get_json()
        logging.debug(new_shopcart)
        new_shopcart["price"] = -1
        resp = self.app.put(
            "/shopcarts/{}/items/{}".format(new_shopcart["customer_id"], new_shopcart["product_id"]),
            json=new_shopcart,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_shopcart = resp.get_json()
        self.assertEqual(updated_shopcart["price"], -1)

    def test_delete_shopcart(self):
        """Delete a ShopCart"""
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_shopcart.customer_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_shopcart.customer_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_item(self):
        """Delete a product from a ShopCart"""
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.delete(
            "{0}/{1}/items/{2}".format(BASE_URL, test_shopcart.customer_id, test_shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}/items/{2}".format(BASE_URL, test_shopcart.customer_id, test_shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkout_shopcart(self):
        """Checkout a ShopCart"""
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.put(
            "{0}/{1}/checkout".format(BASE_URL, test_shopcart.customer_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_shopcart.customer_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkout_product_item(self):
        """Check out a product from a ShopCart"""
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.put(
            "{0}/{1}/items/{2}/checkout".format(BASE_URL, test_shopcart.customer_id, test_shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 0)
        # make sure they are checked out
        resp = self.app.get(
            "{0}/{1}/items/{2}".format(BASE_URL, test_shopcart.customer_id, test_shopcart.product_id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_shopcart_list(self):
        """Get a list of ShopCarts"""
        self._create_shopcarts(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_shopcart_not_found(self):
        """Get a ShopCart thats not found"""
        resp = self.app.get("/shopcarts/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_shopcart_no_data(self):
        """Create a ShopCart with missing data"""
        resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_shopcart_no_content_type(self):
        """Create a ShopCart with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """ Make an illegal method call """
        resp = self.app.put(
            BASE_URL, 
            json={"not": "today"}, 
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_shopcart_list_by_price(self):
        """Query Shopcarts by price"""
        shopcarts = self._create_shopcarts(10)
        test_price = shopcarts[0].price
        price_shopcarts = [shopcart for shopcart in shopcarts if shopcart.price == test_price]
        resp = self.app.get(
            BASE_URL, query_string="price={}".format(test_price)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(price_shopcarts))
        # check the data just to be sure
        for shopcart in data:
            self.assertEqual(shopcart["price"], test_price)

    def test_query_shopcart_list_by_quantity(self):
        """Query Shopcarts by quantity"""
        shopcarts = self._create_shopcarts(10)
        test_quantity = shopcarts[0].quantity
        quantity_shopcarts = [shopcart for shopcart in shopcarts if shopcart.quantity == test_quantity]
        resp = self.app.get(
            BASE_URL, query_string="quantity={}".format(test_quantity)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(quantity_shopcarts))
        # check the data just to be sure
        for shopcart in data:
            self.assertEqual(shopcart["quantity"], test_quantity)

    def test_query_shopcart_list_by_product_id(self):
        """Query Shopcarts by product_id"""
        shopcarts = self._create_shopcarts(10)
        test_product_id = shopcarts[0].product_id
        product_id_shopcarts = [shopcart for shopcart in shopcarts if shopcart.product_id == test_product_id]
        resp = self.app.get(
            BASE_URL, query_string="product_id={}".format(test_product_id)
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(product_id_shopcarts))
        # check the data just to be sure
        for shopcart in data:
            self.assertEqual(shopcart["product_id"], test_product_id)