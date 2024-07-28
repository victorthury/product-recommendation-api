from fastapi import APIRouter
from app.controller.recommendation_controller import RecommendationController

router_recommendations = APIRouter()

@router_recommendations.get("/recommendations")
def get_recommendations(user_id: int):
  return RecommendationController().get(user_id)