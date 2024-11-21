from typing import Dict, List
from .models import MealPlan, DietAnalysis, NutrientAnalysis

class DietAnalyzer:
    def __init__(self):
        self.acceptable_range = (0.9, 1.1)  # 목표의 90-110%를 적정 범위로 설정

    def analyze_diet(self, meal_plan: MealPlan, nutrition_goals: Dict[str, float]) -> DietAnalysis:
        """식단 분석 수행"""
        # 영양소 분석
        calories_analysis = self._analyze_nutrient(
            meal_plan.total_calories,
            nutrition_goals["calories"],
            "calories"
        )
        protein_analysis = self._analyze_nutrient(
            meal_plan.total_protein,
            nutrition_goals["protein"],
            "protein"
        )
        carbs_analysis = self._analyze_nutrient(
            meal_plan.total_carbs,
            nutrition_goals["carbs"],
            "carbs"
        )
        fat_analysis = self._analyze_nutrient(
            meal_plan.total_fat,
            nutrition_goals["fat"],
            "fat"
        )

        # 끼니별 칼로리 분포 계산
        meal_distribution = self._calculate_meal_distribution(meal_plan)

        # 개선 추천사항 생성
        recommendations = self._generate_recommendations(
            calories_analysis,
            protein_analysis,
            carbs_analysis,
            fat_analysis,
            meal_distribution
        )

        return DietAnalysis(
            calories=calories_analysis,
            protein=protein_analysis,
            carbs=carbs_analysis,
            fat=fat_analysis,
            meal_distribution=meal_distribution,
            recommendations=recommendations
        )

    def _analyze_nutrient(self, actual: float, target: float, nutrient_type: str) -> NutrientAnalysis:
        """개별 영양소 분석"""
        achievement_rate = (actual / target * 100) if target > 0 else 0
        return NutrientAnalysis(
            actual=round(actual, 2),
            target=round(target, 2),
            achievement_rate=round(achievement_rate, 2)
        )

    def _calculate_meal_distribution(self, meal_plan: MealPlan) -> Dict[str, float]:
        """끼니별 칼로리 분포 계산"""
        total_calories = meal_plan.total_calories if meal_plan.total_calories > 0 else 1

        breakfast_calories = sum(food.calories for food in meal_plan.breakfast)
        lunch_calories = sum(food.calories for food in meal_plan.lunch)
        dinner_calories = sum(food.calories for food in meal_plan.dinner)

        return {
            "breakfast": round((breakfast_calories / total_calories) * 100, 2),
            "lunch": round((lunch_calories / total_calories) * 100, 2),
            "dinner": round((dinner_calories / total_calories) * 100, 2)
        }

    def _generate_recommendations(self, calories: NutrientAnalysis,
                                protein: NutrientAnalysis,
                                carbs: NutrientAnalysis,
                                fat: NutrientAnalysis,
                                meal_distribution: Dict[str, float]) -> List[str]:
        """영양소 분석을 바탕으로 개선 추천사항 생성"""
        recommendations = []

        # 칼로리 관련 추천
        if calories.achievement_rate < 90:
            recommendations.append("총 칼로리가 목표보다 낮습니다. 간식을 추가하는 것을 고려해보세요.")
        elif calories.achievement_rate > 110:
            recommendations.append("총 칼로리가 목표보다 높습니다. portions을 줄이는 것을 고려해보세요.")

        # 단백질 관련 추천
        if protein.achievement_rate < 90:
            recommendations.append("단백질 섭취가 부족합니다. 계란, 닭가슴살, 생선 등을 추가해보세요.")
        elif protein.achievement_rate > 110:
            recommendations.append("단백질 섭취가 초과되었습니다. 단백질 위주의 음식을 줄여보세요.")

        # 탄수화물 관련 추천
        if carbs.achievement_rate < 90:
            recommendations.append("탄수화물 섭취가 부족합니다. 현미밥, 통곡물 등을 추가해보세요.")
        elif carbs.achievement_rate > 110:
            recommendations.append("탄수화물 섭취가 초과되었습니다. 밥의 양을 줄여보세요.")

        # 지방 관련 추천
        if fat.achievement_rate < 90:
            recommendations.append("지방 섭취가 부족합니다. 견과류, 올리브오일 등을 추가해보세요.")
        elif fat.achievement_rate > 110:
            recommendations.append("지방 섭취가 초과되었습니다. 기름진 음식을 줄여보세요.")

        # 끼니 분배 관련 추천
        ideal_breakfast = 30
        ideal_lunch = 40
        ideal_dinner = 30

        if abs(meal_distribution["breakfast"] - ideal_breakfast) > 10:
            recommendations.append("아침 식사의 칼로리 비중을 30% 근처로 조정하는 것이 좋습니다.")
        if abs(meal_distribution["lunch"] - ideal_lunch) > 10:
            recommendations.append("점심 식사의 칼로리 비중을 40% 근처로 조정하는 것이 좋습니다.")
        if abs(meal_distribution["dinner"] - ideal_dinner) > 10:
            recommendations.append("저녁 식사의 칼로리 비중을 30% 근처로 조정하는 것이 좋습니다.")

        return recommendations[:5]  # 상위 5개 추천사항만 반환