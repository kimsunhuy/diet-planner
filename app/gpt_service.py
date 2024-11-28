import openai
import os
from typing import Dict, Any
import json
from dotenv import load_dotenv

load_dotenv()

class GPTService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key not found")
    
    async def generate_diet_plan(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 한국어로 프롬프트 작성
            prompt = f"""
            다음 정보를 바탕으로 하루 식단을 추천해주세요:

            나이: {user_info['age']}세
            성별: {user_info['gender']}
            체중: {user_info['weight']}kg
            신장: {user_info['height']}cm
            활동량: {user_info['activity_level']}
            목표: {user_info['goal']}

            다음 형식으로 응답해주세요:
            {{
                "breakfast": [
                    {{"name": "음식명", "portion": 분량(g), "calories": 칼로리, "protein": 단백질(g), "carbs": 탄수화물(g), "fat": 지방(g)}}
                ],
                "lunch": [
                    {{"name": "음식명", "portion": 분량(g), "calories": 칼로리, "protein": 단백질(g), "carbs": 탄수화물(g), "fat": 지방(g)}}
                ],
                "dinner": [
                    {{"name": "음식명", "portion": 분량(g), "calories": 칼로리, "protein": 단백질(g), "carbs": 탄수화물(g), "fat": 지방(g)}}
                ]
            }}

            한국인의 식습관을 고려하여 현실적인 식단을 추천해주세요.
            각 끼니는 2-4개의 음식으로 구성해주세요.
            """

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 전문 영양사입니다. 한국인의 식습관을 잘 이해하고 있으며, 건강한 식단을 추천해줍니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # GPT 응답을 JSON으로 파싱
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                print("Error parsing GPT response as JSON")
                return None
            
        except Exception as e:
            print(f"Error in GPT service: {str(e)}")
            return None