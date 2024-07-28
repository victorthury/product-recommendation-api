from app.models.product import get_products, get_products, Product
import pandas as pd
import os
import logging

class RecommendationController:
  def _get_total_sales_by_product(df):
    agg_sales = df.groupby(['product_id', 'product_title']).agg({
      'sales_per_day': 'sum'
    }).reset_index()

    agg_sales.rename(columns={'sales_per_day': 'total_sales'}, inplace=True)

    agg_sales = agg_sales.sort_values(by=['total_sales'], ascending=False).reset_index()
    return agg_sales
  
  def _get_last_prices_by_store(df):
    df_sorted = df.sort_values(by=['store_id', 'product_id', 'sale_date'], ascending=[True, True, False])
    last_prices = df_sorted.groupby(['store_id', 'product_id', 'product_title', 'store_name']).first().reset_index()
    last_prices = last_prices[['store_id', 'store_name', 'product_id', 'product_title', 'product_price', 'product_image_url']]
    return last_prices

  def _get_cheapest_product(df):
    return df.groupby(['product_id']).apply(lambda x: x.loc[x['product_price'].idxmin()]).reset_index(drop=True)
  
  def _merge_total_sales_and_cheapest_products(cheapest_products, total_sales,):
    return pd.merge(cheapest_products, total_sales[['product_id', 'total_sales']], on='product_id', how='left')
  
  def _normalize_column(column):
    return (column - column.min()) / (column.max() - column.min())
  
  def _get_top_recommendations(cls, df):
    weight_price = float(os.getenv("WEIGHT_PRICE"))
    weight_sales = float(os.getenv("WEIGHT_SALES"))
    
    df['normalized_sales'] = cls._normalize_column(df['total_sales'])
    df['normalized_prices'] = cls._normalize_column(df['product_price'])
    df['inverse_normalized_prices'] = 1 - df['normalized_prices']
    df['score'] = weight_price * df['inverse_normalized_prices'] + weight_sales * df['normalized_sales']
    df = df.sort_values(by=['score'], ascending=False).reset_index()
    return df.head().to_dict('records')
  
  def _format_recommendations(recommendations):
    formatted_recommendations = []
    for recommendation in recommendations:
      formatted_recommendations.append(Product(
        product_id=recommendation['product_id'],
        product_title=recommendation['product_title'],
        product_price=recommendation['product_price'],
        product_image_url=recommendation['product_image_url'],
        store_id=recommendation['store_id'],
        store_name=recommendation['store_name'],
      ))
    return formatted_recommendations
  
  @classmethod
  def get(cls, user_id):
    logging.info(f"Fetching recommendations for user_id: {user_id}")
    products = get_products()
    
    total_sales = cls._get_total_sales_by_product(products)

    last_prices = cls._get_last_prices_by_store(products)
    cheapest_products  = cls._get_cheapest_product(last_prices)

    merged_df = cls._merge_total_sales_and_cheapest_products(cheapest_products, total_sales)

    top_recommendations = cls._get_top_recommendations(cls, merged_df)
    formatted_recommendations = cls._format_recommendations(top_recommendations)
    return formatted_recommendations
