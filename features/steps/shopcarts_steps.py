######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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
######################################################################

"""
Shopcarts Steps
Steps file for shopcarts.feature
For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect


@given('the following shopcarts')
def step_impl(context):
    """ Delete all ShopCarts and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the shopcarts and delete them one by one
    context.resp = requests.get(context.base_url + '/shopcarts', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for shopcart in context.resp.json():
        context.resp = requests.delete(context.base_url + '/shopcarts/' + str(shopcart["customer_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new shopcarts
    create_url = context.base_url + '/shopcarts'
    for row in context.table:
        data = {
            "customer_id": row['customer_id'],
            "product_id": row['product_id'],
            "name": row['name'],
            "quantity": row['quantity'],
            "price": row['price'],
        }
        payload = json.dumps(data)
        context.resp = requests.post("{}/{}/items".format(create_url, data['customer_id']), data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
