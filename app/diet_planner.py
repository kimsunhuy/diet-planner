from typing import List, Dict, Any
import json
from .models import FoodItem, MealPlan

class DietPlanner:
    def __init__(self):
        # 샘플 식품 데이터베이스 (실제로는 더 많은 데이터가 필요)
        self.food_database = {
            "korean": {
                "breakfast": [
                    {"name": "현미밥", "portion": 210, "calories": 300, "protein": 6, "carbs": 65, "fat": 2},
                    {"name": "계란말이", "portion": 100, "calories": 150, "protein": 12, "carbs": 2, "fat": 10},
                    {"name": "미역국", "portion": 250, "calories": 50, "protein": 3, "carbs": 5, "fat": 2},
                    {"name": "김치", "portion": 30, "calories": 15, "protein": 1, "carbs": 3, "fat": 0},
                ],
                "lunch": [
                    {"name": "닭가슴살", "portion": 150, "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
                    {"name": "잡곡밥", "portion": 210, "calories": 320, "protein": 7, "carbs": 68, "fat": 2},
                    {"name": "청국장찌개", "portion": 250, "calories": 140, "protein": 12, "carbs": 9, "fat": 7},
                    {"name": "숙주나물", "portion": 70, "calories": 25, "protein": 3, "carbs": 4, "fat": 0},
                ],
                "dinner": [
                    {"name": "연어구이", "portion": 130, "calories": 290, "protein": 25, "carbs": 0, "fat": 19},
                    {"name": "퀴노아밥", "portion": 150, "calories": 180, "protein": 6, "carbs": 34, "fat": 3},
                    {"name": "된장국", "portion": 250, "calories": 100, "protein": 8, "carbs": 7, "fat": 5},
                    {"name": "시금치나물", "portion": 70, "calories": 30, "protein": 3, "carbs": 4, "fat": 0},
                ]
            }
        }

    def create_meal_plan(self, target_calories: float, nutrition_goals: Dict[str, float],
                        allergies: List[str] = None) -> MealPlan:
        """
        목표 칼로리와 영양소 요구량에 맞는 식단 생성
        """
        if allergies is None:
            allergies = []

        # 끼니별 칼로리 배분 (아침 30%, 점심 40%, 저녁 30%)
        meal_calories = {
            "breakfast": target_calories * 0.3,
            "lunch": target_calories * 0.4,
            "dinner": target_calories * 0.3
        }

        meal_plan = {
            "breakfast": [],
            "lunch": [],
            "dinner": []
        }
        
        total_nutrients = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        # 각 끼니별 음식 선택
        for meal_type in ["breakfast", "lunch", "dinner"]:
            available_foods = self.food_database["korean"][meal_type]
            target_meal_calories = meal_calories[meal_type]
            
            # 알레르기 필터링
            filtered_foods = [
                food for food in available_foods
                if not any(allergy.lower() in food["name"].lower() for allergy in allergies)
            ]

            # 음식 선택
            selected_foods = self._select_foods_for_meal(
                filtered_foods,
                target_meal_calories,
                nutrition_goals
            )

            meal_plan[meal_type] = [FoodItem(**food) for food in selected_foods]
            
            # 영양소 합계 계산
            for food in selected_foods:
                total_nutrients["calories"] += food["calories"]
                total_nutrients["protein"] += food["protein"]
                total_nutrients["carbs"] += food["carbs"]
                total_nutrients["fat"] += food["fat"]

        return MealPlan(
            breakfast=meal_plan["breakfast"],
            lunch=meal_plan["lunch"],
            dinner=meal_plan["dinner"],
            total_calories=round(total_nutrients["calories"], 2),
            total_protein=round(total_nutrients["protein"], 2),
            total_carbs=round(total_nutrients["carbs"], 2),
            total_fat=round(total_nutrients["fat"], 2)
        )

    def _select_foods_for_meal(self, foods: List[Dict], target_calories: float,
                             nutrition_goals: Dict[str, float]) -> List[Dict]:
        """
        한 끼니에 대한 음식 선택
        """
        selected_foods = []
        current_calories = 0
        
        # 기본 음식 선택 (각 카테고리에서 하나씩)
        for food in foods:
            if current_calories + food["calories"] <= target_calories * 1.1:  # 10% 오차 허용
                selected_foods.append(food)
                current_calories += food["calories"]

        return selected_foods