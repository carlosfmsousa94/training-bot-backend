from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS so your frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class UserInput(BaseModel):
    age: int
    training_age: int
    goals: str
    availability: dict
    equipment: str
    max_pullup: int
    max_hspu: int
    week: int
    feedback: dict = {}

@app.post("/generate")
async def generate_plan(data: UserInput):
    prompt = f"""
You are a hybrid strength, gymnastics, and running coach blending Max El-Hag, Nick Dimarco, and elite running coaching.

Athlete Profile:
- Age: {data.age}
- Training Age: {data.training_age}
- Goals: {data.goals}
- Weekly Availability: {', '.join([day for day, status in data.availability.items() if status == 'available'])}
- Equipment: {data.equipment}
- Max Pull-Ups: {data.max_pullup}
- Max HSPU: {data.max_hspu}
- Current Week: {data.week}

Feedback (last week):
{data.feedback}

Create a detailed weekly training plan with exercises, sets, reps, intensities, and progression notes.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7,
        )
        return {"plan": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
