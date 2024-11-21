from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class Goal(str, Enum):
    LOSS = "loss"
    MAINTAIN = "maintain"
    GAIN = "gain"

# app/models.py의 UserInput 클래스에 validator 추가
class UserInput(BaseModel):
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(male|female)$")
    weight: float = Field(..., ge=20, le=300)
    height: float = Field(..., ge=100, le=250)
    activity_level: ActivityLevel
    goal: Goal
    allergies: Optional[List[str]] = Field(default=[])

    @validator('gender')
    def gender_must_be_valid(cls, v):
        if v.lower() not in ['male', 'female']:
            raise ValueError('gender must be either male or female')
        return v.lower()

    @validator('activity_level')
    def activity_level_must_be_valid(cls, v):
        if not isinstance(v, ActivityLevel):
            raise ValueError('invalid activity level')
        return v

    @validator('goal')
    def goal_must_be_valid(cls, v):
        if not isinstance(v, Goal):
            raise ValueError('invalid goal')
        return v

    class Config:
        schema_extra = {
            "example": {
                "age": 30,
                "gender": "male",
                "weight": 70,
                "height": 175,
                "activity_level": "moderate",
                "goal": "loss",
                "allergies": []
            }
        }

class FoodItem(BaseModel):
    name: str
    portion: float
    calories: float
    protein: float
    carbs: float
    fat: float

class MealPlan(BaseModel):
    breakfast: List[FoodItem]
    lunch: List[FoodItem]
    dinner: List[FoodItem]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

class NutrientAnalysis(BaseModel):
    actual: float
    target: float
    achievement_rate: float

class DietAnalysis(BaseModel):
    calories: NutrientAnalysis
    protein: NutrientAnalysis
    carbs: NutrientAnalysis
    fat: NutrientAnalysis
    meal_distribution: Dict[str, float]
    recommendations: List[str]

class FullDietResponse(BaseModel):
    bmr: float
    tdee: float
    target_calories: float
    meal_plan: MealPlan
    analysis: DietAnalysis