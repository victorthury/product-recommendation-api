from pydantic import BaseModel
import pandas as pd

class Product(BaseModel):
  product_id: int
  product_title: str
  product_price: float
  product_image_url: str
  store_id: int
  store_name: str

def get_products() -> pd.DataFrame:
  path = 'xpto_sales_products_mar_may_2024.csv'

  products = pd.read_csv(path)
  return products