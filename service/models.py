"""
Models for ShopCart

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""
    
class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class ShopCart(db.Model):
    """
    Class that represents a shop cart
    """

    app = None

    # Table Schema
    customer_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __repr__(self):
        return "<ShopCart %r customer_id=[%s] product_id=[%s]>" % (self.name, 
            self.customer_id, self.product_id)

    def create(self):
        """
        Creates a ShopCart to the database
        """
        logger.info("Creating %s", self.name)
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a ShopCart to the database
        """
        logger.info("Saving %s", self.name)
        if self.customer_id is None or self.product_id is None:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def save(self):
        """
        Updates a ShopCart to the database
        """
        logger.info("Saving %s", self.name)
        db.session.commit()

    def delete(self):
        """ Removes a ShopCart from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a ShopCart into a dictionary """
        return {
            "customer_id": self.customer_id, 
            "product_id": self.product_id, 
            "name": self.name, 
            "quantity": self.quantity, 
            "price": self.price
            }

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = int(data["customer_id"])
            self.product_id = int(data["product_id"])
            self.name = data["name"]
            self.quantity = int(data["quantity"])
            self.price = float(data["price"])
        except KeyError as error:
            raise DataValidationError(
                "Invalid ShopCart: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopCart: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the ShopCarts in the database """
        logger.info("Processing all ShopCarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a ShopCart by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a ShopCart by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """Returns all ShopCarts with the given name

        Args:
            name (string): the name of the ShopCarts you want to match
        """
        logger.info("Processing name query for %s ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id)
    
    @classmethod
    def find_by_price(cls, price: str) -> list:
        """Returns all Shopcarts with the given price

        :type name: float
        :return: a collection of Shopcarts equal to that price
        :rtype: list
        """
        logger.info("Processing price query for %s ...", price)
        return cls.query.filter(cls.price == price)
    
    @classmethod
    def find_by_quantity(cls, quantity: str) -> list:
        """Returns all Shopcarts with the given quantity

        :type name: float
        :return: a collection of Shopcarts equal to that quantity
        :rtype: list
        """
        logger.info("Processing quantity query for %s ...", quantity)
        return cls.query.filter(cls.quantity == quantity)

    @classmethod
    def find_by_product_id(cls, product_id: str) -> list:
        """Returns all Shopcarts with the given product_id

        :type name: float
        :return: a collection of Shopcarts equal to that product_id
        :rtype: list
        """
        logger.info("Processing product_id query for %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id)