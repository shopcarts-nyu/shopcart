Feature: The shopcart store service back-end
    As a E-commerce Manager
    I need a RESTful catalog service
    So that I can keep track of all my shopcarts

Background:
    Given the following shopcarts
        | customer_id | product_id |  name  | quantity | price | 
        | 1           |    1       |  item1 |     1    |  300  |
        | 1           |    2       |  item2 |     2    |  500  |
        | 2           |    1       |  item1 |     2    | 3000  |
        | 6           |   83       |  item6 |     3    |  99   |

Scenario: Search for product id
    When I visit the "Home Page"
    And I set the "Product ID" to "1"
    And I press the "Search" button
    Then I should see customer "1" with product "1" in the results
    And I should see customer "2" with product "1" in the results
    And I should not see customer "1" with product "2" in the results
    And I should not see customer "6" with product "83" in the results

Scenario: Search for quantity
    When I visit the "Home Page"
    And I set the "Quantity" to "2"
    And I press the "Search" button
    Then I should see customer "1" with product "2" in the results
    And I should see customer "1" with product "2" in the results
    And I should not see customer "6" with product "83" in the results
    And I should not see customer "1" with product "1" in the results

Scenario: Search for price
    When I visit the "Home Page"
    And I set the "Price" to "99"
    And I press the "Search" button
    Then I should see customer "6" with product "83" in the results
    And I should not see customer "1" with product "1" in the results
    And I should not see customer "1" with product "2" in the results
    And I should not see customer "2" with product "1" in the results
