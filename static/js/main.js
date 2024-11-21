// 전역 변수로 마지막 결과 저장
let lastResults = null;

document.addEventListener('DOMContentLoaded', function() {
    const dietForm = document.getElementById('dietForm');
    dietForm.addEventListener('submit', handleFormSubmit);
});

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        weight: parseFloat(document.getElementById('weight').value),
        height: parseFloat(document.getElementById('height').value),
        activity_level: document.getElementById('activity_level').value,
        goal: document.getElementById('goal').value,
        allergies: []
    };
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        lastResults = data; // 결과 저장
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        alert('식단 생성 중 오류가 발생했습니다.');
    }
}

function displayResults(data) {
    document.getElementById('results').style.display = 'block';
    document.getElementById('bmr').textContent = Math.round(data.bmr);
    document.getElementById('targetCalories').textContent = Math.round(data.target_calories);
    
    displayMealPlan(data.meal_plan);
    createNutrientsChart(data.analysis);
    createMealDistributionChart(data.analysis.meal_distribution);
    displayRecommendations(data.analysis.recommendations);
}

function displayMealPlan(mealPlan) {
    ['breakfast', 'lunch', 'dinner'].forEach(mealTime => {
        const mealItems = document.querySelector(`#${mealTime} .meal-items`);
        mealItems.innerHTML = '';
        
        mealPlan[mealTime].forEach(food => {
            mealItems.innerHTML += `
                <div class="food-item">
                    <span class="food-name">${food.name}</span>
                    <span class="food-details">${food.portion}g - ${food.calories}kcal</span>
                </div>
            `;
        });
    });
}

// static/js/main.js의 createNutrientsChart 함수를 다음과 같이 수정

function createNutrientsChart(analysis) {
    const ctx = document.getElementById('nutrientsChart').getContext('2d');
    
    // 기존 차트 객체가 있으면 제거
    if (window.nutrientsChart instanceof Chart) {
        window.nutrientsChart.destroy();
    }
    
    window.nutrientsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['칼로리', '단백질', '탄수화물', '지방'],
            datasets: [{
                label: '목표 대비 섭취량 (%)',
                data: [
                    analysis.calories.achievement_rate,
                    analysis.protein.achievement_rate,
                    analysis.carbs.achievement_rate,
                    analysis.fat.achievement_rate
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function createMealDistributionChart(distribution) {
    const ctx = document.getElementById('mealDistributionChart').getContext('2d');
    
    // 기존 차트 객체가 있으면 제거
    if (window.distributionChart instanceof Chart) {
        window.distributionChart.destroy();
    }
    
    window.distributionChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['아침', '점심', '저녁'],
            datasets: [{
                data: [
                    distribution.breakfast,
                    distribution.lunch,
                    distribution.dinner
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true
        }
    });
}

function displayRecommendations(recommendations) {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = recommendations
        .map(rec => `<p>• ${rec}</p>`)
        .join('');
}

// 내보내기 함수들
async function exportPDF() {
    try {
        const response = await fetch('/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(lastResults)
        });
        
        const blob = await response.blob();
        downloadFile(blob, 'diet_plan.pdf');
    } catch (error) {
        console.error('Error:', error);
        alert('PDF 저장 중 오류가 발생했습니다.');
    }
}

async function exportExcel() {
    try {
        const response = await fetch('/export/excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(lastResults)
        });
        
        const blob = await response.blob();
        downloadFile(blob, 'diet_plan.xlsx');
    } catch (error) {
        console.error('Error:', error);
        alert('Excel 저장 중 오류가 발생했습니다.');
    }
}

async function exportImage() {
    try {
        const response = await fetch('/export/image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(lastResults)
        });
        
        const blob = await response.blob();
        downloadFile(blob, 'diet_plan.png');
    } catch (error) {
        console.error('Error:', error);
        alert('이미지 저장 중 오류가 발생했습니다.');
    }
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}