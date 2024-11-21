from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging
import os
import sys

from .models import UserInput, FullDietResponse
from .calculator import NutritionCalculator
from .diet_planner import DietPlanner
from .analyzer import DietAnalyzer
from .exporters import DietExporter

# 정적 파일 디렉토리 설정
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Diet Planner API")

# 정적 파일과 템플릿 디렉토리 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 클래스 인스턴스 생성
calculator = NutritionCalculator()
diet_planner = DietPlanner()
analyzer = DietAnalyzer()
exporter = DietExporter()

@app.get("/")
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 나머지 엔드포인트들은 그대로 유지

@app.post("/calculate", response_model=FullDietResponse)
async def calculate_nutrition(user_input: UserInput):
    try:
        logger.debug(f"Received user input: {user_input}")
        
        # 영양소 계산
        nutrition_calc = calculator.get_full_calculation(user_input)
        logger.debug(f"Nutrition calculation: {nutrition_calc}")
        
        # 영양소 목표 설정
        nutrition_goals = {
            "calories": nutrition_calc["target_calories"],
            "protein": nutrition_calc["daily_protein"],
            "carbs": nutrition_calc["daily_carbs"],
            "fat": nutrition_calc["daily_fat"]
        }
        logger.debug(f"Nutrition goals: {nutrition_goals}")
        
        # 식단 생성
        meal_plan = diet_planner.create_meal_plan(
            target_calories=nutrition_calc["target_calories"],
            nutrition_goals=nutrition_goals,
            allergies=user_input.allergies
        )
        logger.debug(f"Generated meal plan: {meal_plan}")
        
        # 식단 분석
        analysis = analyzer.analyze_diet(meal_plan, nutrition_goals)
        logger.debug(f"Diet analysis: {analysis}")
        
        response = FullDietResponse(
            bmr=nutrition_calc["bmr"],
            tdee=nutrition_calc["tdee"],
            target_calories=nutrition_calc["target_calories"],
            meal_plan=meal_plan,
            analysis=analysis
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    

@app.post("/export/pdf")
async def export_pdf(diet_data: FullDietResponse):
    try:
        filepath = exporter.to_pdf(diet_data.dict())
        return FileResponse(filepath, filename=os.path.basename(filepath))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/excel")
async def export_excel(diet_data: FullDietResponse):
    try:
        filepath = exporter.to_excel(diet_data.dict())
        return FileResponse(filepath, filename=os.path.basename(filepath))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/image")
async def export_image(diet_data: FullDietResponse):
    try:
        filepath = exporter.create_visualization(diet_data.dict())
        return FileResponse(filepath, filename=os.path.basename(filepath))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# app/main.py
origins = [
    "https://diet-planner.onrender.com",  # Render에서 제공하는 도메인
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

