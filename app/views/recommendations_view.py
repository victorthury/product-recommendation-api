from fastapi import APIRouter
from app.controller.recommendation_controller import RecommendationController
from app.models.product import Product
from typing import List

router_recommendations = APIRouter()

@router_recommendations.get("/recommendations")
def get_recommendations() -> List[Product]:
  return RecommendationController().get()