import sys
import os
import pandas as pd
from unittest.mock import patch


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.controller.recommendation_controller import RecommendationController
from app.models.product import Product

def test_get_total_sales_by_product():
    data = {
        'sale_date': ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02'],
        'product_id': [1, 1, 2, 2],
        'product_title': ['Product A', 'Product A', 'Product B', 'Product B'],
        'product_price': [10.0, 10.0, 20.0, 20.0],
        'product_image_url': ['url_a', 'url_a', 'url_b', 'url_b'],
        'store_name': ['Store 1', 'Store 1', 'Store 2', 'Store 2'],
        'store_id': [1, 1, 2, 2],
        'sales_per_day': [5, 3, 2, 4]
    }
    df = pd.DataFrame(data)

    result = RecommendationController._get_total_sales_by_product(df)

    expected_data = {
        'product_id': [1, 2],
        'product_title': ['Product A', 'Product B'],
        'total_sales': [8, 6]
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df)

def test_get_last_prices_by_store():
    data = {
        'sale_date': ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-03'],
        'product_id': [1, 1, 2, 2],
        'product_title': ['Product A', 'Product A', 'Product B', 'Product B'],
        'product_price': [10.0, 12.0, 20.0, 18.0],
        'product_image_url': ['url_a', 'url_a', 'url_b', 'url_b'],
        'store_name': ['Store 1', 'Store 1', 'Store 2', 'Store 2'],
        'store_id': [1, 1, 2, 2],
        'sales_per_day': [5, 3, 2, 4]
    }
    df = pd.DataFrame(data)

    result = RecommendationController._get_last_prices_by_store(df)

    expected_data = {
        'store_id': [1, 2],
        'store_name': ['Store 1', 'Store 2'],
        'product_id': [1, 2],
        'product_title': ['Product A', 'Product B'],
        'product_price': [12.0, 18.0],
        'product_image_url': ['url_a', 'url_b']
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df)
    
def test_get_cheapest_product():
    data = {
        'sale_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
        'product_id': [1, 1, 2, 2],
        'product_title': ['Product A', 'Product A', 'Product B', 'Product B'],
        'product_price': [10.0, 8.0, 20.0, 15.0],
        'product_image_url': ['url_a', 'url_a', 'url_b', 'url_b'],
        'store_name': ['Store 1', 'Store 2', 'Store 1', 'Store 2'],
        'store_id': [1, 2, 1, 2],
        'sales_per_day': [5, 3, 2, 4]
    }
    df = pd.DataFrame(data)

    result = RecommendationController._get_cheapest_product(df)

    expected_data = {
        'sale_date': ['2023-01-02', '2023-01-04'],
        'product_id': [1, 2],
        'product_title': ['Product A', 'Product B'],
        'product_price': [8.0, 15.0],
        'product_image_url': ['url_a', 'url_b'],
        'store_name': ['Store 2', 'Store 2'],
        'store_id': [2, 2],
        'sales_per_day': [3, 4]
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df)

def test_merge_total_sales_and_cheapest_products():
    cheapest_products_data = {
        'product_id': [1, 2],
        'product_title': ['Product A', 'Product B'],
        'product_price': [8.0, 15.0],
        'product_image_url': ['url_a', 'url_b'],
        'store_name': ['Store 2', 'Store 2'],
        'store_id': [2, 2],
        'sales_per_day': [3, 4]
    }
    cheapest_products = pd.DataFrame(cheapest_products_data)

    total_sales_data = {
        'product_id': [1, 2],
        'total_sales': [100, 200]
    }
    total_sales = pd.DataFrame(total_sales_data)

    result = RecommendationController._merge_total_sales_and_cheapest_products(cheapest_products, total_sales)

    expected_data = {
        'product_id': [1, 2],
        'product_title': ['Product A', 'Product B'],
        'product_price': [8.0, 15.0],
        'product_image_url': ['url_a', 'url_b'],
        'store_name': ['Store 2', 'Store 2'],
        'store_id': [2, 2],
        'sales_per_day': [3, 4],
        'total_sales': [100, 200]
    }
    expected_df = pd.DataFrame(expected_data)

    pd.testing.assert_frame_equal(result, expected_df)

def test_get_top_recommendations():

    data = {
        'product_id': [1, 2, 3, 4, 5],
        'product_title': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'product_price': [10.0, 20.0, 15.0, 25.0, 5.0],
        'product_image_url': ['url_a', 'url_b', 'url_c', 'url_d', 'url_e'],
        'store_name': ['Store 1', 'Store 2', 'Store 3', 'Store 4', 'Store 5'],
        'store_id': [1, 2, 3, 4, 5],
        'sales_per_day': [5, 10, 15, 20, 25],
        'total_sales': [50, 100, 150, 200, 250]
    }
    df = pd.DataFrame(data)

    result = RecommendationController._get_top_recommendations(RecommendationController, df)

    expected_order = [5, 3, 1, 4, 2]
    result_order = [record['product_id'] for record in result]
    assert result_order == expected_order
    
    for record in result:
        assert 'score' in record
        
def test_format_recommendations():
    recommendations = [
        {
            'product_id': 1,
            'product_title': 'Product A',
            'product_price': 10.0,
            'product_image_url': 'url_a',
            'store_id': 1,
            'store_name': 'Store 1'
        },
        {
            'product_id': 2,
            'product_title': 'Product B',
            'product_price': 20.0,
            'product_image_url': 'url_b',
            'store_id': 2,
            'store_name': 'Store 2'
        }
    ]

    result = RecommendationController._format_recommendations(recommendations)

    expected_result = [
        Product(
            product_id=1,
            product_title='Product A',
            product_price=10.0,
            product_image_url='url_a',
            store_id=1,
            store_name='Store 1'
        ),
        Product(
            product_id=2,
            product_title='Product B',
            product_price=20.0,
            product_image_url='url_b',
            store_id=2,
            store_name='Store 2'
        )
    ]

    assert result == expected_result
    
@patch('app.models.product.get_products')
def test_get(mock_get_products):
    products_df = pd.DataFrame({
        'product_id': [1, 2, 3, 4, 5],
        'product_title': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'product_price': [10.0, 20.0, 15.0, 25.0, 5.0],
        'product_image_url': ['url_a', 'url_b', 'url_c', 'url_d', 'url_e'],
        'store_name': ['Store 1', 'Store 2', 'Store 3', 'Store 4', 'Store 5'],
        'store_id': [1, 2, 3, 4, 5],
        'sales_per_day': [5, 10, 15, 20, 25],
        'sale_date': ['2023-07-01', '2023-07-02', '2023-07-03', '2023-07-04', '2023-07-05']
    })

    mock_get_products.return_value = products_df

    user_id = 123
    result = RecommendationController.get(user_id)

    assert isinstance(result, list)
    assert all(isinstance(item, Product) for item in result)