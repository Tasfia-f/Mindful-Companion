from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from typing import Dict, List
import json

app = FastAPI(title="Local Mental Health AI")

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str
    source: str = "local_ai"

# Mental Health Response Database
RESPONSE_TEMPLATES = {
    "greeting": [
        "Hello! I'm here to listen. How are you feeling today?",
        "Hi there. I'm glad you're here. What's on your mind?",
        "Welcome. This is a safe space to talk. How can I support you?"
    ],
    "anxiety": [
        """I hear you're feeling anxious. That's completely normal. 
        Try this: **5-4-3-2-1 Grounding Technique**
        1. Look for 5 things you can see
        2. Notice 4 things you can touch
        3. Listen for 3 things you can hear
        4. Identify 2 things you can smell
        5. Name 1 thing you can taste""",
        """Anxiety can feel overwhelming. Let's try box breathing:
        1. Inhale for 4 seconds
        2. Hold for 4 seconds
        3. Exhale for 4 seconds
        4. Hold for 4 seconds
        5. Repeat 3-4 times"""
    ],
    "depression": [
        """I'm sorry you're feeling this way. Remember:
        • Your feelings are valid
        • You don't have to be productive
        • Small steps are still progress
        Would you like to share more?""",
        """When feeling down, sometimes it helps to:
        1. Connect with one person today
        2. Do one small thing you used to enjoy
        3. Be gentle with yourself"""
    ],
    "stress": [
        """Stress can build up. Try:
        • Take a 5-minute walk
        • Write down what's stressing you
        • Prioritize one task at a time""",
        """For stress relief:
        1. Progressive muscle relaxation
        2. 10-minute meditation
        3. Limit news/social media"""
    ],
    "loneliness": [
        """Feeling lonely is hard. You could:
        • Join an online community
        • Volunteer virtually
        • Reach out to an old friend""",
        """Remember:
        • Many people feel lonely sometimes
        • Quality connections matter more than quantity
        • It's okay to ask for company"""
    ],
    "sleep": [
        """For better sleep:
        • No screens 1 hour before bed
        • Keep a consistent sleep schedule
        • Try a warm caffeine-free drink""",
        """If you can't sleep:
        • Get out of bed for 20 minutes
        • Read a physical book
        • Try a sleep meditation"""
    ]
}

# Keyword to category mapping
KEYWORD_MAPPING = {
    "anxious": "anxiety",
    "anxiety": "anxiety",
    "panic": "anxiety",
    "worried": "anxiety",
    "nervous": "anxiety",
    
    "depressed": "depression",
    "depression": "depression",
    "sad": "depression",
    "down": "depression",
    "hopeless": "depression",
    
    "stress": "stress",
    "stressed": "stress",
    "overwhelmed": "stress",
    "pressure": "stress",
    
    "lonely": "loneliness",
    "alone": "loneliness",
    "isolated": "loneliness",
    
    "sleep": "sleep",
    "insomnia": "sleep",
    "tired": "sleep",
    "exhausted": "sleep",
    
    "hi": "greeting",
    "hello": "greeting",
    "hey": "greeting",
    "greetings": "greeting"
}

import random
def get_local_response(user_input: str) -> str:
    """Generate response from local templates"""
    user_lower = user_input.lower()
    
    # Check for keywords
    for keyword, category in KEYWORD_MAPPING.items():
        if keyword in user_lower:
            responses = RESPONSE_TEMPLATES.get(category, [])
            if responses:
                return random.choice(responses)
    
    # Default empathetic responses
    default_responses = [
        "Thank you for sharing that with me. Could you tell me more about how you're feeling?",
        "I hear you. That sounds really difficult. What's been most challenging about this?",
        "I'm here to listen. What would help most right now - to talk, or to explore coping strategies?",
        "Thank you for trusting me with this. How has this been affecting your daily life?"
    ]
    
    return random.choice(default_responses)

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for local AI"""
    response = get_local_response(request.message)
    return ChatResponse(response=response, source="local_ai")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_type": "local_rule_based"}

if __name__ == "__main__":
    # Run on localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)