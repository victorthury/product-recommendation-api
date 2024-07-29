from pydantic import BaseModel
import pandas as pd
import os

class Product(BaseModel):
  product_id: int
  product_title: str
  product_price: float
  product_image_url: str
  store_id: int
  store_name: str

def get_products() -> pd.DataFrame:
  path = os.getenv("DATASET_PATH")

  products = pd.read_csv(path)
  return products