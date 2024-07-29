from fastapi import APIRouter
from app.controller.recommendation_controller import RecommendationController
from app.models.product import Product
from typing import List

router_recommendations = APIRouter()

@router_recommendations.get("/recommendations")
def get_recommendations(user_id: int) -> List[Product]:
  return RecommendationController().get(user_id)