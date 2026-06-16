# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from random import randrange, choice as randchoice
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read a product from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        prod_lst = []
        n_prod = 3
        for _ in range(n_prod):
            prod_lst.append(ProductFactory())
            prod_lst[-1].id = None
            prod_lst[-1].create()
            self.assertIsNotNone(prod_lst[-1].id)
        # choose random product to read from db
        i = randrange(n_prod)
        # Read product by id, check that it matches the original in the list
        app.logger.info(
            f'Retrieving product {prod_lst[i].name} with id {prod_lst[i].id}')
        prod_read = Product.find(prod_lst[i].id)
        self.assertEqual(prod_read.name, prod_lst[i].name)
        self.assertEqual(prod_read.description, prod_lst[i].description)
        self.assertEqual(Decimal(prod_read.price), prod_lst[i].price)
        self.assertEqual(prod_read.available, prod_lst[i].available)
        self.assertEqual(prod_read.category, prod_lst[i].category)

    def test_update_a_product(self):
        """It should Update a product in the database"""
        # Generate Product in the database
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        app.logger.info(f'Creating product {product.name}')
        product.create()
        # Read product from the database before updating
        product_db_orig = Product.find(product.id)
        self.assertEqual(product_db_orig.description, product.description)
        # Update product text
        new_desc = 'I''m a litte teapot, short and stout, ' \
            + 'here''s my handle, here''s my spout.'
        self.assertNotEqual(new_desc, product.description)
        product.description = new_desc
        app.logger.info(f'Updating description of {product.name}')
        product.update()
        # Read updated product from the database and check description
        self.assertEqual(len(Product.all()), 1)
        product_db_altrd = Product.find(product.id)
        self.assertEqual(product_db_altrd.description, new_desc)
        # Set invalid id and check for DataValidationError
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a product in the database"""
        # Generate Product in the database
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        app.logger.info(f'Creating product {product.name}')
        product.create()
        self.assertEqual(len(Product.all()), 1)
        app.logger.info(f'Deleting product {product.name}')
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List All products from the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Generate five products
        prod_lst = []
        n_prod = 5
        app.logger.info(f'Creating {n_prod} products')
        for _ in range(n_prod):
            prod_lst.append(ProductFactory())
            prod_lst[-1].id = None
            prod_lst[-1].create()
            self.assertIsNotNone(prod_lst[-1].id)
        # Read all products from the database
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """It should Find a product by Name"""
        products = Product.all()
        self.assertEqual(products, [])
        # Generate five products
        prod_lst = []
        n_prod = 5
        app.logger.info(f'Creating {n_prod} products')
        for _ in range(n_prod):
            prod_lst.append(ProductFactory())
            prod_lst[-1].id = None
            prod_lst[-1].create()
            self.assertIsNotNone(prod_lst[-1].id)
        # Calculate number of occurences
        name_srch = prod_lst[0].name
        n_occurence = 0
        for prod in prod_lst:
            if prod.name == name_srch:
                n_occurence += 1
        # Find products by name and check for correct number and name
        products_fnd = Product.find_by_name(name_srch)
        self.assertEqual(products_fnd.count(), n_occurence)
        for prod_fnd in products_fnd:
            self.assertEqual(prod_fnd.name, name_srch)

    def test_find_product_by_availability(self):
        """It should Find a product by Availability"""
        products = Product.all()
        self.assertEqual(products, [])
        # Generate ten products
        prod_lst = []
        n_prod = 10
        app.logger.info(f'Creating {n_prod} products')
        for _ in range(n_prod):
            prod_lst.append(ProductFactory())
            prod_lst[-1].id = None
            prod_lst[-1].create()
            self.assertIsNotNone(prod_lst[-1].id)
        # Calculate number of occurences
        avail_srch = prod_lst[0].available
        n_occurence = 0
        for prod in prod_lst:
            if prod.available == avail_srch:
                n_occurence += 1
        # Find products by availability
        # and check for correct number and availability
        products_fnd = Product.find_by_availability(avail_srch)
        self.assertEqual(products_fnd.count(), n_occurence)
        for prod_fnd in products_fnd:
            self.assertEqual(prod_fnd.available, avail_srch)

    def test_find_product_by_category(self):
        """It should Find a product by Category"""
        products = Product.all()
        self.assertEqual(products, [])
        # Generate ten products
        prod_lst = []
        n_prod = 10
        app.logger.info(f'Creating {n_prod} products')
        for _ in range(n_prod):
            prod_lst.append(ProductFactory())
            prod_lst[-1].id = None
            prod_lst[-1].create()
            self.assertIsNotNone(prod_lst[-1].id)
        # Calculate number of occurences
        ctgry_srch = prod_lst[0].category
        n_occurence = 0
        for prod in prod_lst:
            if prod.category == ctgry_srch:
                n_occurence += 1
        # Find products by category
        # and check for correct number and category
        products_fnd = Product.find_by_category(ctgry_srch)
        self.assertEqual(products_fnd.count(), n_occurence)
        for prod_fnd in products_fnd:
            self.assertEqual(prod_fnd.category, ctgry_srch)

    def test_find_product_by_price(self):
        """It should Find a product by Price"""
        products = Product.all()
        self.assertEqual(products, [])
        # Generate ten products
        prod_lst = []
        n_prod = 10
        app.logger.info(f'Creating {n_prod} products')
        for _ in range(n_prod):
            prod_lst.append(ProductFactory())
            prod_lst[-1].id = None
            prod_lst[-1].create()
            self.assertIsNotNone(prod_lst[-1].id)
        # Calculate number of occurences
        price_srch = prod_lst[0].price
        n_occurence = 0
        for prod in prod_lst:
            if prod.price == price_srch:
                n_occurence += 1
        # Find products by price
        # and check for correct number and price
        products_fnd = Product.find_by_price(price_srch)
        self.assertEqual(products_fnd.count(), n_occurence)
        for prod_fnd in products_fnd:
            self.assertEqual(prod_fnd.price, price_srch)
        # check correct processing when price provided as string
        products_fnd = Product.find_by_price(str(price_srch))
        self.assertEqual(products_fnd.count(), n_occurence)

    def test_deserialize_a_product(self):
        """It should Deserialize a dict to a product"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        prod_dict = product.serialize()
        prod_tst = ProductFactory()
        prod_tst.id = None
        prod_tst.deserialize(prod_dict)
        self.assertEqual(prod_tst.id, product.id)
        self.assertEqual(prod_tst.name, product.name)
        self.assertEqual(prod_tst.description, product.description)
        self.assertEqual(prod_tst.available, product.available)
        self.assertEqual(prod_tst.price, product.price)
        self.assertEqual(prod_tst.category, product.category)
        # test for DataValiationError on wrong available and category types
        tests = {'available': 42, 'category': 'fish'}
        for k, v in tests.items():
            self.assertRaises(
                DataValidationError,
                lambda: prod_tst.deserialize(prod_dict | {k: v}))
        self.assertRaises(
            DataValidationError,
            lambda: prod_tst.deserialize(prod_dict | {'category': {'a': 'b', 'c': 42}}))
