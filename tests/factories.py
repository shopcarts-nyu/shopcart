# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Test Factory to make fake objects for testing
"""
import factory
from service.models import ShopCart


class ShopCartFactory(factory.Factory):
    """Creates fake shopcarts that you don't have to buy"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = ShopCart

    customer_id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    quantity = factory.Faker('pyint', min_value=0, max_value=1000000000)
    price = factory.Faker('pyfloat', min_value=0, max_value=10000)

