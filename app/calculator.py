from .models import UserInput, ActivityLevel, Goal

class NutritionCalculator:
    def calculate_bmr(self, user_input: UserInput) -> float:
        """
        해리스-베네딕트 공식을 사용한 기초대사량(BMR) 계산
        """
        if user_input.gender.lower() == 'male':
            bmr = 88.362 + \
                  (13.397 * user_input.weight) + \
                  (4.799 * user_input.height) - \
                  (5.677 * user_input.age)
        else:
            bmr = 447.593 + \
                  (9.247 * user_input.weight) + \
                  (3.098 * user_input.height) - \
                  (4.330 * user_input.age)
        return round(bmr, 2)

    def calculate_tdee(self, bmr: float, activity_level: ActivityLevel) -> float:
        """
        총 일일 에너지 소비량(TDEE) 계산
        """
        activity_multipliers = {
            ActivityLevel.SEDENTARY: 1.2,      # 좌식 생활
            ActivityLevel.LIGHT: 1.375,        # 가벼운 운동
            ActivityLevel.MODERATE: 1.55,      # 중간 강도 운동
            ActivityLevel.ACTIVE: 1.725,       # 높은 강도 운동
            ActivityLevel.VERY_ACTIVE: 1.9     # 매우 높은 강도 운동
        }
        return round(bmr * activity_multipliers[activity_level], 2)

    def calculate_target_calories(self, tdee: float, goal: Goal) -> float:
        """
        목표에 따른 일일 목표 칼로리 계산
        """
        adjustments = {
            Goal.LOSS: -500,     # 감량: 일일 500칼로리 감소
            Goal.MAINTAIN: 0,    # 유지: 현재 칼로리 유지
            Goal.GAIN: 500      # 증가: 일일 500칼로리 증가
        }
        return round(tdee + adjustments[goal], 2)

    def get_full_calculation(self, user_input: UserInput) -> dict:
        """
        모든 계산을 수행하고 결과를 반환
        """
        bmr = self.calculate_bmr(user_input)
        tdee = self.calculate_tdee(bmr, user_input.activity_level)
        target_calories = self.calculate_target_calories(tdee, user_input.goal)
        
        return {
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_calories,
            "daily_protein": round(user_input.weight * 2, 2),  # 체중 1kg당 2g의 단백질
            "daily_fat": round(target_calories * 0.25 / 9, 2),  # 총 칼로리의 25%를 지방에서 섭취
            "daily_carbs": round(
                (target_calories - 
                 (user_input.weight * 2 * 4) -  # 단백질 칼로리
                 (target_calories * 0.25)       # 지방 칼로리
                ) / 4, 2)  # 나머지를 탄수화물로 계산
        }