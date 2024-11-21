from fpdf import FPDF
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from typing import Dict
import os

class DietExporter:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

    def to_pdf(self, diet_data: Dict) -> str:
        """식단을 PDF로 내보내기"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        # 제목
        pdf.cell(190, 10, "맞춤 식단 플랜", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        
        # 기본 정보
        pdf.cell(190, 10, f"기초대사량(BMR): {diet_data['bmr']:.2f} kcal", ln=True)
        pdf.cell(190, 10, f"목표 칼로리: {diet_data['target_calories']:.2f} kcal", ln=True)
        
        # 식단 정보
        for meal_time, meals in diet_data['meal_plan'].items():
            if meal_time in ['breakfast', 'lunch', 'dinner']:
                pdf.set_font("Arial", "B", 14)
                pdf.cell(190, 10, f"{meal_time.capitalize()}", ln=True)
                pdf.set_font("Arial", size=12)
                
                for meal in meals:
                    pdf.cell(190, 10, 
                            f"- {meal['name']}: {meal['portion']}g "
                            f"({meal['calories']} kcal)", ln=True)
        
        # 영양소 분석
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, "영양소 분석", ln=True)
        pdf.set_font("Arial", size=12)
        
        for nutrient, data in diet_data['analysis'].items():
            if isinstance(data, dict) and 'actual' in data:
                pdf.cell(190, 10, 
                        f"{nutrient}: {data['actual']}/{data['target']} "
                        f"({data['achievement_rate']:.1f}%)", ln=True)

        # 파일 저장
        filename = f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.export_dir, filename)
        pdf.output(filepath)
        return filepath

    def to_excel(self, diet_data: Dict) -> str:
        """식단을 엑셀로 내보내기"""
        # 식단 데이터 준비
        meals_data = []
        for meal_time, meals in diet_data['meal_plan'].items():
            if meal_time in ['breakfast', 'lunch', 'dinner']:
                for meal in meals:
                    meals_data.append({
                        'Meal Time': meal_time,
                        'Food': meal['name'],
                        'Portion (g)': meal['portion'],
                        'Calories': meal['calories'],
                        'Protein (g)': meal['protein'],
                        'Carbs (g)': meal['carbs'],
                        'Fat (g)': meal['fat']
                    })
        
        # DataFrame 생성
        df = pd.DataFrame(meals_data)
        
        # 파일 저장
        filename = f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        # Excel 파일 생성
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Meal Plan', index=False)
            
            # 영양소 분석 시트 추가
            analysis_data = {
                'Nutrient': [],
                'Actual': [],
                'Target': [],
                'Achievement Rate (%)': []
            }
            
            for nutrient, data in diet_data['analysis'].items():
                if isinstance(data, dict) and 'actual' in data:
                    analysis_data['Nutrient'].append(nutrient)
                    analysis_data['Actual'].append(data['actual'])
                    analysis_data['Target'].append(data['target'])
                    analysis_data['Achievement Rate (%)'].append(data['achievement_rate'])
            
            pd.DataFrame(analysis_data).to_excel(
                writer, sheet_name='Analysis', index=False)
        
        return filepath

    def create_visualization(self, diet_data: Dict) -> str:
        """식단 시각화 이미지 생성"""
        # 이미지 크기 설정
        width = 800
        height = 1000
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()

        # 제목
        draw.text((width//2-100, 30), "일일 식단 계획", fill='black', font=font)
        
        # 기본 정보
        y = 100
        draw.text((50, y), f"목표 칼로리: {diet_data['target_calories']:.0f} kcal", 
                 fill='black', font=font)
        
        # 식단 정보
        y = 180
        for meal_time, meals in diet_data['meal_plan'].items():
            if meal_time in ['breakfast', 'lunch', 'dinner']:
                draw.text((50, y), meal_time.capitalize(), fill='black', font=font)
                y += 40
                
                for meal in meals:
                    draw.text((70, y), 
                             f"• {meal['name']} ({meal['portion']}g) - {meal['calories']} kcal",
                             fill='black', font=font)
                    y += 30
                y += 20

        # 파일 저장
        filename = f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.export_dir, filename)
        img.save(filepath)
        
        return filepath