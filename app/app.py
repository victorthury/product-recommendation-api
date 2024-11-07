from fastapi import FastAPI
from dotenv import load_dotenv

from app.views.recommendations_view import router_recommendations

app = FastAPI(title="Product Recommendation API")

load_dotenv(".env.development")

app.router.include_router(
  router_recommendations,
  prefix="/api/v1",
  tags=["recommendation"]
)
