import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import hashlib
import json
import time
import random
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, timedelta
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import os

# Create database in current script directory (where app.py is)
db_path = "mood_data.db"  # This is in E:\ai chat bot\mood_data.db
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# Create moods table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        timestamp TEXT,
        mood TEXT,
        mood_value INTEGER,
        category TEXT,
        notes TEXT,
        color TEXT
    )
''')

# Create sleep tracking table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sleep_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        timestamp TEXT,
        sleep_hours REAL,
        sleep_quality INTEGER,
        wakeups INTEGER,
        notes TEXT,
        bedtime TEXT,
        waketime TEXT
    )
''')

# Create bedtime routines table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bedtime_routines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        activities TEXT,
        reminder_time TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT
    )
''')
conn.commit()


def toggle_theme():
    """Toggle between light and dark mode"""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    
    # Toggle the theme
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
        # Apply dark mode
        st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stSidebar {
                background-color: #262730;
            }
            .user-message {
                background-color: #2d3746;
            }
            .bot-message {
                background-color: #3a4a5f;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.session_state.theme = 'light'
        # Apply light mode (default Streamlit theme)
        st.markdown("""
        <style>
            .stApp {
                background-color: #ffffff;
                color: #31333F;
            }
            .stSidebar {
                background-color: #f0f2f6;
            }
        </style>
        """, unsafe_allow_html=True)


def show_resources_section():
    """Display resources as buttons that trigger pop-ups"""
    st.markdown("---")
    st.subheader("📚 Resources")
    
    # Initialize resource view state
    if 'resource_view' not in st.session_state:
        st.session_state.resource_view = None
    
    # Resource categories with icons
    resource_categories = [
        {"name": "🧠 Mental Health Education", "icon": "🧠"},
        {"name": "📱 Mobile Apps", "icon": "📱"},
        {"name": "📖 Books & Reading", "icon": "📖"},
        {"name": "🎧 Podcasts & Audio", "icon": "🎧"},
        {"name": "🆘 Immediate Help", "icon": "🆘"},
        {"name": "🧘‍♀️ Quick Exercises", "icon": "🧘‍♀️"},
        {"name": "📝 Journal Prompts", "icon": "📝"},
        {"name": "🏥 Local Services", "icon": "🏥"},
        {"name": "🎯 Self-Care Ideas", "icon": "🎯"},
        {"name": "💪 Crisis Coping Skills", "icon": "💪"}
    ]
    
    # Create 2 columns for buttons
    col1, col2 = st.columns(2)
    
    for i, category in enumerate(resource_categories):
        with col1 if i % 2 == 0 else col2:
            if st.button(
                f"{category['icon']} {category['name'].split()[0]}",
                key=f"resource_{i}",
                use_container_width=True,
                help=f"Click for {category['name']}"
            ):
                st.session_state.resource_view = category['name']
                st.rerun()
    
    # Add a clear button to close any open resource
    if st.session_state.resource_view:
        st.markdown("---")
        if st.button("✖ Close Resources", use_container_width=True, type="secondary"):
            st.session_state.resource_view = None
            st.rerun()
    
    # Display the selected resource
    if st.session_state.resource_view:
        show_resource_content(st.session_state.resource_view)

def show_resource_content(resource_name):
    """Display content for selected resource"""
    
    # Create a pop-up style container
    st.markdown("---")
    st.markdown(f"### {resource_name}")
    st.markdown("---")
    
    # Define resource content
    resource_content = {
        "🧠 Mental Health Education": """
        **Understanding Mental Health:**
        
        🌐 **Websites:**
        • [MentalHealth.gov](https://www.mentalhealth.gov) - US government mental health resources
        • [WHO Mental Health](https://www.who.int/mental_health) - Global mental health information
        • [NIMH](https://www.nimh.nih.gov) - National Institute of Mental Health research
        • [Mind.org.uk](https://www.mind.org.uk) - UK mental health charity
        
        🇧🇩 **Bangladesh Specific:**
        • [Kaan Pete Roi](https://kaanpeteroi.org) - Emotional support helpline & resources
        • [Moner Bondhu](https://www.monerbondhu.com) - Local mental health awareness platform
        • [BAP](http://www.bap-bd.org) - Bangladesh Association of Psychiatrists
        
        📚 **Learning Resources:**
        • **Psychoeducation materials** on anxiety, depression, stress
        • **Mental health first aid** training resources
        • **Understanding therapy** - Different types explained
        • **Medication education** - How antidepressants work
        
        🎓 **Free Courses:**
        • Coursera: "The Science of Well-Being" (Yale University)
        • edX: "Managing Mental Health in the Workplace"
        • FutureLearn: "Understanding Anxiety, Depression and CBT"
        """,
        
        "📱 Mobile Apps": """
        **Recommended Mental Health Apps:**
        
        🧘 **Mindfulness & Meditation:**
        • **Headspace** - Guided meditation for beginners & advanced
        • **Calm** - Sleep stories, meditation, music
        • **Insight Timer** - Largest free meditation library
        • **Smiling Mind** - Mindfulness for all ages (free)
        • **Breethe** - Meditation and sleep support
        
        📊 **Mood Tracking:**
        • **Daylio** - Simple mood diary with charts
        • **Moodnotes** - CBT-based mood journal
        • **Bearable** - Symptom & mood tracker
        • **eMoods** - Bipolar mood tracker
        • **How We Feel** - Emotion tracking & insights
        
        🆘 **Crisis Support:**
        • **My3** - Suicide prevention safety plan
        • **Crisis Text Line** - Text-based crisis support
        • **Stay Alive** - Suicide prevention resources
        • **Virtual Hope Box** - Coping skills for crisis
        
        🏃 **Wellness & Habit:**
        • **Fabulous** - Daily routine builder
        • **Habitica** - Gamified habit tracking
        • **Finch** - Self-care pet companion
        • **Sanvello** - CBT & meditation combined
        
        🇧🇩 **Bangladeshi Apps:**
        • **Tonic** - Doctor consultations including psychiatrists
        • **Praktan** - Mental health awareness platform
        • **Moner Bondhu App** - Local mental health resources
        """,
        
        "📖 Books & Reading": """
        **Recommended Reading:**
        
        🧠 **Self-Help Classics:**
        • **"Feeling Good"** by David Burns - CBT techniques for depression
        • **"The Happiness Trap"** by Russ Harris - ACT approach to thoughts
        • **"The Body Keeps the Score"** by Bessel van der Kolk - Trauma healing
        • **"Mind Over Mood"** by Dennis Greenberger - CBT workbook
        
        😰 **For Anxiety:**
        • **"The Anxiety and Phobia Workbook"** by Edmund Bourne
        • **"DARE"** by Barry McDonagh - New approach to anxiety
        • **"Hope and Help for Your Nerves"** by Claire Weekes
        • **"First, We Make the Beast Beautiful"** by Sarah Wilson
        
        🧘 **Mindfulness & Acceptance:**
        • **"Wherever You Go, There You Are"** by Jon Kabat-Zinn
        • **"The Miracle of Mindfulness"** by Thich Nhat Hanh
        • **"Radical Acceptance"** by Tara Brach
        • **"The Power of Now"** by Eckhart Tolle
        
        🤝 **Relationships & Communication:**
        • **"The Gifts of Imperfection"** by Brené Brown
        • **"Nonviolent Communication"** by Marshall Rosenberg
        • **"Attached"** by Amir Levine - Attachment theory
        
        🇧🇩 **Bangladeshi Authors:**
        • **"Moner Kotha"** by local psychologists
        • Mental health columns in **Prothom Alo, The Daily Star**
        • **"Chinta Biswasion"** - Anxiety management in Bangla
        """,
        
        "🎧 Podcasts & Audio": """
        **Mental Health Podcasts:**
        
        🎙️ **Therapy & Mental Health:**
        • **The Happiness Lab** - Dr. Laurie Santos (Yale)
        • **The Hilarious World of Depression** - Comedians discuss depression
        • **Terrible, Thanks for Asking** - Honest conversations
        • **Therapy for Black Girls** - Dr. Joy Harden Bradford
        
        🧠 **Psychology & Science:**
        • **Hidden Brain** - NPR's psychology podcast
        • **The Psychology Podcast** - Dr. Scott Barry Kaufman
        • **Speaking of Psychology** - APA's podcast
        
        🧘 **Mindfulness & Meditation:**
        • **10% Happier** - Dan Harris interviews meditation teachers
        • **The Daily Meditation Podcast** - Daily guided meditations
        • **Meditation Minis** - Short guided meditations
        
        🌏 **Bangladeshi Content:**
        • **Moner Kotha** - Mental health discussions in Bangla
        • **Cholo Boli** - Mental wellness conversations
        • **Shuni** - Storytelling with mental health themes
        
        📻 **Audio Resources:**
        • **Calm Radio** - Meditation music channels
        • **Sleep Stories** - Various apps and platforms
        • **LibriVox** - Free public domain audiobooks
        
        🎵 **Music for Mental Health:**
        • **Focus@Will** - Music for concentration
        • **Brain.fm** - Music for focus, relaxation, sleep
        • **YouTube channels** with calming music and nature sounds
        """,
        
        "🆘 Immediate Help": """
        **Crisis Support Contacts:**
        
        🇧🇩 **Bangladesh 24/7 Crisis Lines:**
        • **Kaan Pete Roi**: `09612-119911` or `+880 9612-119911`
        • **National Helpline (Women & Children)**: `109`
        • **Child Helpline**: `1098`
        • **Police/Fire/Ambulance**: `999`
        • **Health Call Centre**: `16263`
        
        🏥 **Hospital Psychiatry Departments:**
        • **BSMMU Hospital**: +880-2-8616641
        • **National Institute of Mental Health (NIMH)**: +880-2-9122560
        • **Dhaka Medical College**: +880-2-55165036
        
        🌍 **International Hotlines:**
        • **International Suicide Prevention**: Find local hotlines
        • **Crisis Text Line**: Text HOME to 741741 (US)
        • **Samaritans**: 116 123 (UK)
        • **Lifeline Australia**: 13 11 14
        
        💻 **Online Crisis Chat:**
        • **Crisis Text Line** website
        • **7 Cups** - Free listener support
        • **IMAlive** - Online crisis chat
        
        🚨 **What to Do in Crisis:**
        1. **Call a helpline** - You don't have to be suicidal to call
        2. **Go to emergency room** if you're unsafe
        3. **Contact a trusted person** immediately
        4. **Use grounding techniques** while waiting for help
        5. **Remove means** if having suicidal thoughts
        
        ⏰ **Remember:**
        • These services are **free** and **confidential**
        • You can call **even if you're not sure** you need help
        • **It's okay to call multiple times**
        • **You deserve support** no matter how small the problem seems
        """,
        
        "🧘‍♀️ Quick Exercises": """
        **Immediate Relief Exercises:**
        
        ⏱️ **5-Minute Stress Relief:**
        1. **Box Breathing**: Inhale 4s → Hold 4s → Exhale 4s → Hold 4s
        2. **Progressive Muscle Relaxation**: Tense and release each muscle group
        3. **Gratitude Practice**: Name 3 specific things you're thankful for
        4. **5-4-3-2-1 Grounding**: Notice 5 things you can see, 4 you can feel, 3 you can hear, 2 you can smell, 1 you can taste
        
        😰 **For Anxiety Attacks:**
        • **Temperature Shock**: Hold ice cube or splash cold water on face
        • **Square Breathing**: Visualize drawing a square with your breath
        • **Butterfly Hug**: Cross arms and alternately tap shoulders
        • **54321 Technique**: Engage all your senses
        
        😔 **For Depression:**
        • **Opposite Action**: Do the opposite of what depression suggests
        • **Behavioral Activation**: Schedule one pleasant activity
        • **Sunlight Exposure**: 10 minutes of morning sun
        • **Micro-movement**: Just move one body part
        
        😤 **For Anger/Frustration:**
        • **STOP Technique**: Stop → Take breath → Observe → Proceed
        • **Counting Backwards**: From 100 by 7s
        • **Physical Release**: Punch pillow or squeeze stress ball
        • **Cool Down**: Splash cold water or use cold compress
        
        🧠 **For Overthinking:**
        • **Thought Stopping**: Say "STOP" aloud and visualize stop sign
        • **Worry Time**: Schedule 15 minutes to worry, then move on
        • **Mindful Observation**: Observe thoughts like clouds passing
        • **Distraction Technique**: Engage in absorbing activity
        
        💤 **For Sleep Issues:**
        • **4-7-8 Breathing**: Inhale 4s → Hold 7s → Exhale 8s
        • **Body Scan**: Mentally scan body from toes to head
        • **Gratitude Reflection**: List things you're grateful for
        • **Progressive Relaxation**: Release tension systematically
        """,
        
        "📝 Journal Prompts": """
        **Therapeutic Writing Prompts:**
        
        📅 **Daily Check-in:**
        1. What emotion am I feeling most strongly today? (Name it, rate 1-10)
        2. What's one small act of self-care I can do today?
        3. What am I grateful for today? (Be specific)
        4. What's one challenge I faced and how did I handle it?
        
        🌀 **When Feeling Overwhelmed:**
        1. What's actually within my control right now?
        2. What's one tiny step I can take right now?
        3. What would I tell a friend in this situation?
        4. What resources or support do I need?
        
        🔍 **Self-Reflection:**
        1. What are my personal warning signs of stress/anxiety?
        2. What activities make me lose track of time (flow state)?
        3. When do I feel most like "myself"?
        4. What are my core values? Am I living in alignment with them?
        
        💭 **Thought Examination (CBT Style):**
        1. What's the automatic thought I'm having?
        2. What evidence supports this thought?
        3. What evidence contradicts this thought?
        4. What's a more balanced perspective?
        
        🌈 **Positive Exploration:**
        1. What are my strengths and how have I used them recently?
        2. What's something I've overcome that I'm proud of?
        3. What brings me joy? (Make a list)
        4. Who supports me and how can I connect with them?
        
        🎯 **Goal-Oriented:**
        1. What's one small step toward my wellbeing goals?
        2. What boundaries do I need to set or reinforce?
        3. What am I learning about myself through challenges?
        4. How do I want to feel, and what actions support that?
        
        ✨ **Weekly Reflection:**
        1. What went well this week?
        2. What did I learn about myself?
        3. What do I want to carry into next week?
        4. What do I need to let go of?
        """,
        
        "🏥 Local Services": """
        **Bangladesh Mental Health Services:**
        
        🏛️ **Government Hospitals with Psychiatry:**
        • **Bangabandhu Sheikh Mujib Medical University (BSMMU)**
          - Address: Shahbag, Dhaka
          - Contact: +880-2-8616641
        
        • **National Institute of Mental Health (NIMH)**
          - Address: Sher-e-Bangla Nagar, Dhaka
          - Contact: +880-2-9122560
          - Specialized mental health institute
        
        • **Dhaka Medical College Hospital**
          - Address: Bakshi Bazar, Dhaka
          - Psychiatry OPD available
        
        • **Sir Salimullah Medical College Hospital**
          - Address: Mitford Road, Dhaka
        
        🏥 **Private Hospitals:**
        • **Labaid Specialized Hospital**
          - Psychiatry Department: +880-2-9676350
          - Appointment needed
        
        • **United Hospital Limited**
          - Mental Health Services: +880-2-8836000
          - Psychiatrists available
        
        • **Apollo Hospitals Dhaka**
          - Behavioral Medicine: +880-2-8431661
          - Counseling available
        
        • **Square Hospitals Ltd**
          - Psychiatry: +880-2-8144400
        
        💻 **Online/Telemedicine:**
        • **Tonic** - Video consultations with psychiatrists
        • **Cholo Doctor** - Doctor appointments including mental health
        • **DocTime** - Online doctor consultations
        
        👥 **Support Groups:**
        • **Anxiety & Depression Support Group Bangladesh** (Facebook)
        • **Mental Health Bangladesh** community groups
        • **Recovery International** meetings (if available)
        
        🎓 **Training & Workshops:**
        • **Mental Health First Aid** training occasionally available
        • **Mindfulness workshops** through various organizations
        • **Yoga & meditation classes** with mental health focus
        
        💰 **Cost Considerations:**
        • Government hospitals: More affordable, longer waits
        • Private hospitals: Higher cost, shorter waits
        • Some NGOs offer free/subsidized services
        • Check if insurance covers mental health
        
        📋 **Before Your Appointment:**
        1. Write down your symptoms and concerns
        2. Note any medications you're taking
        3. Prepare questions for the doctor
        4. Bring a trusted person if needed
        5. Know your rights as a patient
        """,
        
        "🎯 Self-Care Ideas": """
        **Practical Self-Care Activities:**
        
        ⏱️ **Quick Self-Care (Under 5 minutes):**
        • Drink a glass of water mindfully
        • Step outside for 10 deep breaths
        • Listen to one favorite song fully
        • Do 5 stretches at your desk/chair
        • Write down 3 positive things from today
        • Apply scented lotion or essential oil
        • Look out window and name things you see
        
        ☕ **Medium Self-Care (15-30 minutes):**
        • Make a proper cup of tea/coffee
        • Take a mindful shower or bath
        • Read a chapter of a book
        • Do a short guided meditation
        • Journal for 10 minutes
        • Cook a simple, nourishing meal
        • Call a friend just to chat
        
        🏃 **Movement-Based Self-Care:**
        • 10-minute dance party to favorite music
        • Gentle yoga or stretching
        • Walk around the block
        • Swimming or water exercise
        • Gardening or plant care
        • Cleaning/organizing one small area
        
        🎨 **Creative Self-Care:**
        • Doodle or color in a coloring book
        • Write a poem or short story
        • Play a musical instrument
        • Take photos of things that bring joy
        • Cook or bake something new
        • Craft or DIY project
        
        🌿 **Nature-Based Self-Care:**
        • Sit in sunlight for 10 minutes
        • Walk barefoot on grass
        • Visit a park or garden
        • Watch clouds or stars
        • Care for houseplants
        • Open windows for fresh air
        
        📵 **Digital Detox Self-Care:**
        • Turn off notifications for 1 hour
        • Delete unused apps
        • Unfollow negative accounts
        • Read a physical book
        • Write letters instead of texting
        • Have a device-free meal
        
        🛌 **Rest & Sleep Self-Care:**
        • Create bedtime routine
        • Use calming scents (lavender)
        • Try white noise or calming sounds
        • Use comfortable bedding
        • Keep sleep environment cool/dark
        • Nap if needed (20-30 minutes)
        
        🤝 **Social Self-Care:**
        • Schedule regular check-ins with friends
        • Join a club or group with shared interests
        • Volunteer for a cause you care about
        • Attend community events
        • Practice saying "no" to protect energy
        • Ask for help when needed
        """,
        
        "💪 Crisis Coping Skills": """
        **Immediate Coping Strategies for Crisis Moments:**
        
        🚨 **When Overwhelmed:**
        1. **STOP Skill** (DBT):
           - Stop what you're doing
           - Take a step back
           - Observe what's happening
           - Proceed mindfully
        
        2. **TIPP Skill** (DBT):
           - Temperature: Cold water on face or hold ice
           - Intense exercise: 5-10 minutes of vigorous movement
           - Paced breathing: Slow, deep breaths
           - Paired muscle relaxation: Tense and release
        
        🧊 **Grounding Techniques:**
        • **Physical Grounding:**
          - Press feet firmly into floor
          - Touch different textures around you
          - Hold a cold object
          - Notice body sensations
        
        • **Mental Grounding:**
          - Name all colors you see
          - Count backwards from 100 by 7s
          - List categories (animals, countries, etc.)
          - Describe your environment in detail
        
        • **Soothing Grounding:**
          - Say kind things to yourself
          - Picture a safe place
          - Hold a comforting object
          - Listen to calming sounds
        
        🌊 **Ride the Wave Technique:**
        1. Acknowledge the emotion is temporary
        2. Don't try to fight it
        3. Breathe through it
        4. Notice it peaks and subsides
        5. Remind yourself "This will pass"
        
        📞 **Safety Planning:**
        1. **Emergency contacts** (keep list handy)
        2. **Safe places** to go
        3. **Distraction activities** prepared
        4. **Reasons for living** list
        5. **Professional contacts** saved
        
        🎯 **Distress Tolerance ACCEPTS** (DBT):
        • **Activities** - Do something engaging
        • **Contributing** - Help someone else
        • **Comparisons** - Put situation in perspective
        • **Emotions** - Create opposite emotion
        • **Pushing away** - Temporarily set aside
        • **Thoughts** - Distract with mental activities
        • **Sensations** - Use strong sensations
        
        🔄 **When Suicidal Thoughts Occur:**
        1. **Reach out immediately** - Call helpline or trusted person
        2. **Go to safe place** - Remove yourself from danger
        3. **Delay decision** - Wait 24 hours before acting
        4. **Remember past coping** - What has helped before?
        5. **Professional help** - Go to emergency room if needed
        
        💭 **Cognitive Strategies:**
        • **Thought Defusion**: See thoughts as just thoughts, not facts
        • **Wise Mind**: Balance emotional mind with reasonable mind
        • **Radical Acceptance**: Accept reality as it is in this moment
        • **One-Moment Mindfulness**: Focus completely on present moment
        
        ⚠️ **When to Seek Immediate Help:**
        • Thoughts of harming self or others
        • Feeling completely out of control
        • Severe dissociation or psychosis
        • Inability to care for basic needs
        • Acute substance abuse risk
        """
    }
    
    # Display the content
    if resource_name in resource_content:
        st.markdown(resource_content[resource_name])
        
        # REMOVED THE 3 BUTTONS:
        # 1. 📋 Copy to Notes
        # 2. 💾 Save Resource  
        # 3. 🔄 New Random Tip
        
    else:
        st.info("Resource content coming soon!")
    
    # Show saved resources count (removed but keeping the saved_resources logic if needed elsewhere)
    if 'saved_resources' in st.session_state and st.session_state.saved_resources:
        st.caption(f"📌 You have {len(st.session_state.saved_resources)} saved resources")

def add_resources_to_sidebar():
    """Add resources section to sidebar"""
    show_resources_section()
    
    # Add saved resources view if any are saved (keeping this but the save button is removed)
    if 'saved_resources' in st.session_state and st.session_state.saved_resources:
        st.markdown("---")
        with st.expander("📌 Your Saved Resources", expanded=False):
            for i, resource in enumerate(st.session_state.saved_resources):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"{i+1}. {resource}")
                with col2:
                    if st.button("🗑️", key=f"remove_{i}"):
                        st.session_state.saved_resources.pop(i)
                        st.rerun()
            
            if st.button("Clear All Saved Resources", type="secondary"):
                st.session_state.saved_resources = []
                st.rerun()
        
def get_ollama_response_simple(user_input, history):
    """Simple Ollama integration with better error handling"""
    try:
        # Quick check if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code != 200:
            return None
        
        # Get available models
        models = response.json().get('models', [])
        if not models:
            return None
        
        # Use first available model
        model_name = models[0]['name']
        
        # Prepare messages
        messages = [
            {"role": "system", "content": "You are a supportive mental health listener. Be empathetic and helpful."}
        ]
        
        # Add conversation context
        for msg in history[-3:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"][:200]  # Limit length
            })
        
        messages.append({"role": "user", "content": user_input})
        
        # Call Ollama
        ollama_response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=15
        )
        
        if ollama_response.status_code == 200:
            result = ollama_response.json()
            return f"[Ollama] {result['message']['content']}"
        
    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None
    
    return None


def get_local_ai_response(user_input: str) -> str:
    """Advanced local AI response system - runs in same app, no FastAPI needed"""
    
    user_lower = user_input.lower()
    
    # Enhanced mental health responses
    response_groups = {
        'greeting': {
            'keywords': ['hi', 'hello', 'hey', 'greetings'],
            'responses': [
                "Hello! I'm here to listen. How are you feeling today?",
                "Hi there. This is a safe space. What's on your mind?"
            ]
        },
        'anxiety': {
            'keywords': ['anxious', 'anxiety', 'panic', 'worried', 'nervous'],
            'responses': [
                """I hear you're feeling anxious. Try this grounding exercise:
1. Name 5 things you can see
2. Notice 4 things you can touch
3. Listen for 3 sounds
4. Identify 2 things you can smell
5. Name 1 thing you can taste""",
                """For anxiety, try box breathing:
1. Inhale for 4 seconds
2. Hold for 4 seconds
3. Exhale for 4 seconds
4. Hold for 4 seconds
5. Repeat 3-4 times"""
            ]
        },
        'depression': {
            'keywords': ['depressed', 'depression', 'sad', 'down', 'hopeless'],
            'responses': [
                """I'm sorry you're feeling this way. Remember your feelings are valid.
Would you like to share more about what's on your mind?""",
                """When feeling down:
• Connect with one person today
• Do one small thing you used to enjoy
• Be gentle with yourself"""
            ]
        },
        'stress': {
            'keywords': ['stress', 'stressed', 'pressure', 'overwhelmed'],
            'responses': [
                """Stress can build up. Try:
• Take a 5-minute walk
• Write down what's stressing you
• Prioritize one task at a time""",
                """For stress relief:
1. Progressive muscle relaxation
2. 10-minute meditation
3. Limit news/social media"""
            ]
        }
    }
    
    # Check for keywords and return appropriate response
    for category, data in response_groups.items():
        for keyword in data['keywords']:
            if keyword in user_lower:
                return random.choice(data['responses'])
    
    # General empathetic responses
    general_responses = [
        "Thank you for sharing that with me. Could you tell me more?",
        "I hear you. That sounds really difficult. What's been most challenging?",
        "I'm here to listen. What would be most helpful right now?",
        "Thank you for trusting me with this. How has this been affecting you?"
    ]
    
    return random.choice(general_responses)


# Add to session state
if 'response_cache' not in st.session_state:
    st.session_state.response_cache = {}
if 'cache_hits' not in st.session_state:
    st.session_state.cache_hits = 0

def get_cached_response(user_input):
    """Check cache for similar queries"""
    cache_key = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
    
    # Check cache
    if cache_key in st.session_state.response_cache:
        cached = st.session_state.response_cache[cache_key]
        # If cached less than 1 hour ago
        if time.time() - cached['timestamp'] < 3600:
            st.session_state.cache_hits += 1
            return cached['response']
    return None

def cache_response(user_input, response):
    """Store response in cache"""
    cache_key = hashlib.md5(user_input.lower().strip().encode()).hexdigest()
    st.session_state.response_cache[cache_key] = {
        'response': response,
        'timestamp': time.time()
    }
    
def calculate_weekly_pattern():
    """Calculate mood patterns by day of week"""
    if not st.session_state.mood_history:
        return {}
    
    weekly_data = defaultdict(list)
    for entry in st.session_state.mood_history:
        day_name = entry["timestamp"].strftime("%A")
        weekly_data[day_name].append(entry["mood_value"])
    
    weekly_pattern = {}
    for day, values in weekly_data.items():
        weekly_pattern[day] = sum(values) / len(values)
    
    return weekly_pattern

def update_mood_insights():
    """Calculate mood insights from history"""
    if not st.session_state.mood_history:
        return
    
    # Count by category
    positive_count = len([m for m in st.session_state.mood_history if m["category"] == "positive"])
    neutral_count = len([m for m in st.session_state.mood_history if m["category"] == "neutral"])
    negative_count = len([m for m in st.session_state.mood_history if m["category"] == "negative"])
    
    # Find most common moods
    mood_counts = defaultdict(int)
    for entry in st.session_state.mood_history[-30:]:  # Last 30 days
        mood_counts[entry["mood"]] += 1
    
    common_moods = sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Calculate weekly pattern
    weekly_pattern = calculate_weekly_pattern()
    
    st.session_state.mood_insights = {
        'positive_days': positive_count,
        'neutral_days': neutral_count,
        'negative_days': negative_count,
        'common_moods': common_moods,
        'mood_patterns': weekly_pattern,
        'total_entries': len(st.session_state.mood_history),
        'avg_mood': sum(m["mood_value"] for m in st.session_state.mood_history) / len(st.session_state.mood_history) if st.session_state.mood_history else 0
    }


# ========== MOOD TRACKING ==========
# Initialize mood tracking in session state
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []
    # Load from database
    cursor.execute("SELECT * FROM moods ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    for row in rows:
        mood_entry = {
            "date": row[1],
            "timestamp": datetime.fromisoformat(row[2]),
            "mood": row[3],
            "mood_value": row[4],
            "category": row[5],
            "notes": row[6],
            "color": row[7]
        }
        st.session_state.mood_history.append(mood_entry)

if 'daily_moods' not in st.session_state:
    st.session_state.daily_moods = {}
    # Populate daily_moods from loaded history
    for entry in st.session_state.mood_history:
        st.session_state.daily_moods[entry["date"]] = entry

if 'mood_insights' not in st.session_state:
    update_mood_insights()

# Mood options with emojis and colors
MOOD_OPTIONS = {
    "😊 Happy": {"value": 5, "color": "#4CAF50", "category": "positive"},
    "🙂 Content": {"value": 4, "color": "#8BC34A", "category": "positive"},
    "😐 Neutral": {"value": 3, "color": "#FFC107", "category": "neutral"},
    "😔 Sad": {"value": 2, "color": "#FF9800", "category": "negative"},
    "😢 Depressed": {"value": 1, "color": "#F44336", "category": "negative"},
    "😰 Anxious": {"value": 2, "color": "#9C27B0", "category": "negative"},
    "😤 Stressed": {"value": 2, "color": "#E91E63", "category": "negative"},
    "😴 Tired": {"value": 2, "color": "#607D8B", "category": "negative"},
    "😌 Relaxed": {"value": 4, "color": "#2196F3", "category": "positive"},
    "🎉 Excited": {"value": 5, "color": "#00BCD4", "category": "positive"}
}


def record_mood(mood, notes=""):
    """Record a mood entry"""
    today = date.today().isoformat()
    timestamp = datetime.now()
    
    mood_entry = {
        "date": today,
        "timestamp": timestamp,
        "mood": mood,
        "mood_value": MOOD_OPTIONS[mood]["value"],
        "category": MOOD_OPTIONS[mood]["category"],
        "notes": notes,
        "color": MOOD_OPTIONS[mood]["color"]
    }
    
    # Save to database with proper encoding
    try:
        cursor.execute('''
            INSERT INTO moods (date, timestamp, mood, mood_value, category, notes, color)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            today,
            timestamp.isoformat(),
            mood,  # This should store the actual emoji text
            MOOD_OPTIONS[mood]["value"],
            MOOD_OPTIONS[mood]["category"],
            notes,
            MOOD_OPTIONS[mood]["color"]
        ))
        conn.commit()
        print(f"✅ Saved mood to database: {mood}")
    except Exception as e:
        print(f"❌ Database error: {e}")
        # Try alternative encoding
        try:
            mood_clean = mood.encode('utf-8', 'ignore').decode('utf-8')
            cursor.execute('''
                INSERT INTO moods (date, timestamp, mood, mood_value, category, notes, color)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                today,
                timestamp.isoformat(),
                mood_clean,
                MOOD_OPTIONS[mood]["value"],
                MOOD_OPTIONS[mood]["category"],
                notes,
                MOOD_OPTIONS[mood]["color"]
            ))
            conn.commit()
            print(f"✅ Saved mood (alternative encoding): {mood_clean}")
        except Exception as e2:
            print(f"❌ Alternative encoding also failed: {e2}")
    
    # Also add to session state for current session
    st.session_state.mood_history.append(mood_entry)
    st.session_state.daily_moods[today] = mood_entry
    update_mood_insights()
    
    return mood_entry

# With automatic sentiment detection:
#detect sentiment
def detect_sentiment(text):
    """Simple sentiment detection"""
    text_lower = text.lower()
    positive_words = ['good', 'great', 'happy', 'better', 'improving', 'thanks', 'thank you', 'helpful']
    negative_words = ['bad', 'worse', 'sad', 'depressed', 'anxious', 'stress', 'hopeless', 'lonely']
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"



def create_mood_chart(days=7):
    """Create a mood chart for the last N days"""
    if not st.session_state.daily_moods:
        return None
    
    # Get last N days
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    dates = []
    mood_values = []
    colors = []
    labels = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        if date_str in st.session_state.daily_moods:
            entry = st.session_state.daily_moods[date_str]
            dates.append(current_date)
            mood_values.append(entry["mood_value"])
            colors.append(entry["color"])
            labels.append(entry["mood"])
        else:
            dates.append(current_date)
            mood_values.append(None)
            colors.append("#CCCCCC")
            labels.append("No data")
        
        current_date += timedelta(days=1)
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add line
    fig.add_trace(go.Scatter(
        x=dates,
        y=mood_values,
        mode='lines+markers',
        name='Mood',
        line=dict(color='#4A90E2', width=3),
        marker=dict(size=10, color=colors),
        text=labels,
        hoverinfo='text+y'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Mood Trend - Last {days} Days",
        xaxis_title="Date",
        yaxis_title="Mood Level (1-5)",
        yaxis=dict(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5]),
        height=300,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

def create_mood_distribution_chart():
    """Create a pie chart of mood distribution"""
    if not st.session_state.mood_insights['total_entries']:
        return None
    
    categories = ['Positive', 'Neutral', 'Negative']
    values = [
        st.session_state.mood_insights['positive_days'],
        st.session_state.mood_insights['neutral_days'],
        st.session_state.mood_insights['negative_days']
    ]
    colors = ['#4CAF50', '#FFC107', '#F44336']
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hoverinfo='label+value+percent'
    )])
    
    fig.update_layout(
        title="Mood Distribution",
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    return fig

def get_mood_analysis():
    """Generate mood analysis text"""
    insights = st.session_state.mood_insights
    
    if insights['total_entries'] == 0:
        return "Track your mood to see insights here!"
    
    analysis = []
    
    # Overall mood
    avg_mood = insights['avg_mood']
    if avg_mood >= 4:
        overall = "mostly positive"
    elif avg_mood >= 3:
        overall = "generally neutral"
    else:
        overall = "tending towards negative"
    
    analysis.append(f"**Overall**: Your mood has been {overall} (average: {avg_mood:.1f}/5).")
    
    # Most common moods
    if insights['common_moods']:
        common = ", ".join([f"{mood} ({count}x)" for mood, count in insights['common_moods'][:2]])
        analysis.append(f"**Common moods**: {common}")
    
    # Weekly patterns
    if insights['mood_patterns']:
        best_day = max(insights['mood_patterns'].items(), key=lambda x: x[1])[0]
        worst_day = min(insights['mood_patterns'].items(), key=lambda x: x[1])[0]
        analysis.append(f"**Pattern**: You feel best on {best_day}s and worst on {worst_day}s.")
    
    # Encouragement based on trends
    if insights['positive_days'] > insights['negative_days'] * 2:
        analysis.append("💚 **Great job!** You're maintaining mostly positive moods.")
    elif insights['negative_days'] > insights['positive_days']:
        analysis.append("💛 **Notice**: You've had more difficult days lately. Remember to practice self-care.")
    
    return "\n\n".join(analysis)

# Temporary bypass - remove when quota resets
USE_MOCK_RESPONSES = True  # Set to False when quota resets

def get_mock_response(user_input):
    """Return mock responses without API calls"""
    responses = {
        "hello": "Hi there! How are you feeling today?",
        "anxious": "I understand you're feeling anxious. Try the 5-4-3-2-1 grounding exercise in the sidebar.",
        "sad": "I'm sorry you're feeling sad. Remember it's okay to feel this way. Would you like to talk about it?",
        "stress": "Stress can be overwhelming. Have you tried the deep breathing exercise? It might help calm your nervous system.",
    }
    
    # Find closest match
    user_lower = user_input.lower()
    for key in responses:
        if key in user_lower:
            return responses[key]
    
    return "I'm here to listen. Could you tell me more about what you're experiencing?"

# Load environment variables
load_dotenv()

# ========== PAGE SETUP ==========
st.set_page_config(
    page_title="Mindful Companion",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ========== CUSTOM STYLING ==========
st.markdown("""
<style>
    /* Existing styles... */
    .stChatInput {
        bottom: 20px;
    }
    .user-message {
        background-color: #1e3a5f;
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 4px 18px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #2b3e50;
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 4px;
        margin: 5px 0;
        max-width: 80%;
        margin-right: auto;
    }
    .emergency-box {
        background-color: #ffebee;
        border: 2px solid #f44336;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    /* Dark/Light mode toggle positioning */
    .mode-toggle {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 999;
    }
    
    /* Custom toggle switch */
    .switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }
    
    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 34px;
    }
    
    .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    
    input:checked + .slider {
        background-color: #2196F3;
    }
    
    input:checked + .slider:before {
        transform: translateX(26px);
    }
    
    .slider:after {
        content: "🌙";
        position: absolute;
        left: 8px;
        top: 5px;
        font-size: 18px;
        opacity: 0;
        transition: .4s;
    }
    
    input:checked + .slider:after {
        content: "☀️";
        left: 8px;
        opacity: 1;
    }
    
    input:not(:checked) + .slider:after {
        content: "🌙";
        left: 36px;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    .stChatInput {
        bottom: 20px;
    }
    .user-message {
        background-color: #1e3a5f;
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 4px 18px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #2b3e50;
        color: white;
        padding: 10px 15px;
        border-radius: 18px 18px 18px 4px;
        margin: 5px 0;
        max-width: 80%;
        margin-right: auto;
    }
    .emergency-box {
        background-color: #ffebee;
        border: 2px solid #f44336;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== INITIALIZE SESSION STATE ==========
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
if 'emergency_triggered' not in st.session_state:
    st.session_state.emergency_triggered = False

# ========== EMERGENCY DETECTION ==========
EMERGENCY_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die',
    'self-harm', 'cutting', 'overdose', 'emergency'
]

# ========== PROFESSIONAL HELP DETECTION ==========
PROFESSIONAL_HELP_KEYWORDS = [
    'psychiatrist', 'therapist', 'doctor', 'counselor',
    'therapy', 'appointment', 'clinic', 'hospital',
    'professional help', 'mental hospital', 'treatment',
    'psychologist', 'clinical', 'medication', 'prescription'
]

HOSPITAL_SWITCHBOARDS = {
    "Apollo Hospitals Dhaka": "+880-2-8431661",
    "United Hospital Limited": "+880-2-8836000", 
    "Square Hospitals Ltd": "+880-2-8144400",
    "Labaid Specialized Hospital": "+880-2-9676350",
    "Popular Medical College Hospital": "+880-2-9353690"
}

EMERGENCY_RESPONSE = """🚨 **Please seek immediate help. You are not alone:**

**In Bangladesh:**
• **Kaan Pete Roi (Emotional Support):** `09612-119911` or `+880 9612-119911`
• **Child Helpline:** `1098`
• **National Helpline (Women & Children):** `109`

**Main Emergency Numbers:**
• **999**: The primary, free, 24/7 national emergency service for Police, Fire, and Ambulance.
• **English Service**: Dial 999 and press '2' for English-speaking operators.
• **16263**: The Health Call Centre for health advice and government/private ambulance lists.

**Private Ambulance Services (Examples):**
• **24 Ambulance**: `01911-125156`

**International Resources:**
• **International Association for Suicide Prevention**: Find a crisis centre near you.

Help is available right now."""

def check_emergency(text):
    """Check if message contains emergency keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

def log_mood_interaction(user_input, professional_response, sentiment="neutral"):
    """Analyze and log mood from interactions"""
    # Simple sentiment analysis
    user_lower = user_input.lower()
    
    # Detect mood from keywords
    mood_keywords = {
        'happy': '😊 Happy',
        'good': '😊 Happy',
        'great': '😊 Happy',
        'excited': '🎉 Excited',
        'content': '🙂 Content',
        'relaxed': '😌 Relaxed',
        'okay': '😐 Neutral',
        'fine': '😐 Neutral',
        'neutral': '😐 Neutral',
        'sad': '😔 Sad',
        'down': '😔 Sad',
        'depressed': '😢 Depressed',
        'anxious': '😰 Anxious',
        'worried': '😰 Anxious',
        'stressed': '😤 Stressed',
        'tired': '😴 Tired',
        'exhausted': '😴 Tired'
    }
    
    detected_mood = None
    for keyword, mood in mood_keywords.items():
        if keyword in user_lower:
            detected_mood = mood
            break
    
    # If no specific mood detected, use the provided sentiment
    if not detected_mood:
        if sentiment == "positive":
            detected_mood = "🙂 Content"
        elif sentiment == "negative":
            detected_mood = "😔 Sad"
        else:
            detected_mood = "😐 Neutral"
    
    # Record the mood
    mood_entry = record_mood(detected_mood, user_input[:100])  # Store first 100 chars as notes
    
    return mood_entry


def get_professional_help_guide():
    """Provide safe guidance for finding psychiatric help"""
    
    # Use the correct hospital switchboards dictionary
    hospital_list = "\n".join([
        f"• **{name}**: `{number}`" 
        for name, number in HOSPITAL_SWITCHBOARDS.items()
    ])
    
    guide = f"""**🔍 How to Find Professional Psychiatric Help:**

🏥 **Hospital Contacts (Main Switchboards):**
{hospital_list}

⚠️ **Important Note:**
These are **general hospital numbers**. When you call, ask for the **"Psychiatry Department"** or **"Mental Health OPD"**.

📋 **How to Use These Numbers:**
1. Call during office hours (9 AM - 5 PM, Sunday-Thursday)
2. Clearly state you need the Psychiatry Department
3. Inquire about:
   - Appointment procedures and availability
   - Consultation fees
   - Required documents or referrals

⚕️ **Verification Checklist:**
✅ Ensure the psychiatrist is registered with **Bangladesh Medical & Dental Council (BMDC)**
✅ Check their specialization area
✅ Ask about follow-up procedures
✅ Verify credentials during your first visit

💡 **Additional Options:**
• **Government Hospitals**: More affordable, may have longer wait times
• **Telemedicine Platforms**: Tonic, Cholo Doctor, DocTime (offer vetted doctors)
• **Bangladesh Association of Psychiatrists (BAP)**: Can provide professional referrals

🚨 **For emergencies**, use the emergency helplines immediately."""
    
    return guide

# ========== INITIALIZE GEMINI AI ==========
def setup_gemini():
    """Configure Gemini API with available models"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key or api_key == "your_NEW_key_goes_here":
        st.error("""
        🔑 **API Key Missing**
        
        1. Edit the `.env` file
        2. Replace `your_NEW_key_goes_here` with your actual key
        """)
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        
        # Safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Use available model (from your list)
        model = genai.GenerativeModel(
            model_name="models/gemini-flash-latest",
            safety_settings=safety_settings
        )
        return model
        
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        st.stop()

def setup_gemini_with_fallback():
    """Try multiple models until one works"""
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    # Models to try in order (each has separate 20/day quota)
    model_attempts = [
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite", 
        "models/gemini-2.5-flash",
        "models/gemini-flash-latest"
    ]
    
    for model_name in model_attempts:
        try:
            # Quick test to see if model has quota
            test_model = genai.GenerativeModel(model_name=model_name)
            response = test_model.generate_content("Test")
            if response.text:
                print(f"✅ Using model: {model_name}")
                return test_model
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                print(f"⚠️ Model {model_name} quota exceeded, trying next...")
                continue
            else:
                print(f"⚠️ Model {model_name} error: {str(e)[:50]}...")
                continue
    
    # If all models exhausted
    st.error("""
    ❌ **Daily Free Quota Exhausted**
    
    You've used all 20 free requests across available models.
    
    **Solutions:**
    1. **Wait until tomorrow** (resets at 00:00 PT)
    2. **Upgrade to paid tier** at: https://ai.google.dev/pricing
    3. **Use OpenAI/Claude** as alternative (if you have their API keys)
    4. **Implement local caching** to reduce API calls
    """)
    st.stop()

def summarize_user_input(text, max_length=100):
    """Summarize user input for therapeutic responses"""
    if len(text) <= max_length:
        return text
    # Simple summary - take first part
    words = text.split()
    if len(words) > 20:
        return " ".join(words[:20]) + "..."
    return text

def detect_themes(text):
    """Detect themes in text"""
    themes = []
    text_lower = text.lower()
    
    theme_keywords = {
        'relationships': ['relationship', 'partner', 'friend', 'family', 'love', 'breakup'],
        'work': ['work', 'job', 'career', 'boss', 'colleague', 'office'],
        'health': ['health', 'sick', 'pain', 'illness', 'medical'],
        'future': ['future', 'goal', 'plan', 'dream', 'ambition'],
        'past': ['past', 'memory', 'childhood', 'previous', 'before']
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    return themes

def paraphrase_user_input(text):
    """Create a therapeutic paraphrase of user input"""
    # Simple paraphrasing - just return a cleaned version
    return text[:150] + "..." if len(text) > 150 else text

def create_system_prompt():
    """Create the AI's personality with psychological knowledge"""
    return """You are Mindful Companion, an AI mental health therapist with expertise in:

**THERAPEUTIC APPROACHES YOU USE:**
1. **Cognitive Behavioral Therapy (CBT)** - Help identify and reframe negative thought patterns
2. **Mindfulness-Based Stress Reduction (MBSR)** - Guide present-moment awareness
3. **Acceptance and Commitment Therapy (ACT)** - Foster psychological flexibility
4. **Positive Psychology** - Build strengths and cultivate gratitude
5. **Dialectical Behavior Therapy (DBT)** skills - Emotional regulation, distress tolerance

**PSYCHOLOGICAL KNOWLEDGE BASE:**
• **Maslow's Hierarchy of Needs** - Understand human motivation
• **Attachment Theory** - Relationship patterns and emotional bonds
• **Transtheoretical Model of Change** - Stages: Precontemplation → Action → Maintenance
• **Cognitive Distortions** - All-or-nothing thinking, catastrophizing, personalization
• **Emotional Regulation** - Window of tolerance, grounding techniques

**THERAPEUTIC TECHNIQUES:**
- Socratic questioning to explore thoughts
- Reflective listening and validation
- Psychoeducation about mental health
- Behavioral activation for depression
- Exposure hierarchy for anxiety
- Thought records for cognitive restructuring

**CLINICAL GUIDELINES:**
1. **Assessment Phase**: Understand presenting concerns, history, current functioning
2. **Psychoeducation**: Explain psychological concepts in simple terms
3. **Skill Building**: Teach practical coping strategies
4. **Generalization**: Help apply skills to real-life situations
5. **Relapse Prevention**: Plan for maintaining progress

**RESPONSE GUIDELINES:**
- Start with empathy and validation
- Ask open-ended questions to explore deeper
- Provide evidence-based interventions
- Use metaphors and examples for clarity
- Suggest specific exercises or journal prompts
- Always maintain therapeutic boundaries
- Never diagnose but suggest when professional evaluation might help
- End with a reflective question to continue conversation

**CRISIS RESPONSE:**
If suicide/self-harm mentioned:
1. Express immediate concern and validation
2. Provide crisis resources (national hotlines)
3. Encourage contacting professional help
4. Suggest immediate safety planning

Begin by asking about their current emotional state and what brings them here today."""

# Add psychology knowledge base
PSYCHOLOGY_KNOWLEDGE = {
    "cbt_techniques": [
        "**Cognitive Restructuring**: Identify and challenge automatic negative thoughts",
        "**Behavioral Activation**: Schedule pleasant activities to combat depression",
        "**Exposure Therapy**: Gradual facing of feared situations for anxiety",
        "**Thought Records**: Writing down thoughts, emotions, and evidence",
        "**Activity Scheduling**: Planning rewarding activities to improve mood"
    ],
    "mindfulness_exercises": [
        "**Body Scan**: Systematically bring attention to each body part",
        "**Mindful Breathing**: Focus on breath without judgment",
        "**RAIN Technique**: Recognize, Allow, Investigate, Nurture difficult emotions",
        "**Loving-Kindness Meditation**: Cultivate compassion for self and others",
        "**3-Minute Breathing Space**: Brief mindfulness practice for stress"
    ],
    "psychology_concepts": {
        "Window of Tolerance": "Optimal zone of emotional arousal where we can function effectively",
        "Fight-Flight-Freeze": "Automatic survival responses to perceived threat",
        "Emotional Regulation": "Ability to manage and respond to emotional experiences",
        "Core Beliefs": "Deeply held beliefs about self, others, and the world",
        "Psychological Flexibility": "Ability to adapt to changing circumstances while staying true to values"
    },
    "therapy_books": [
        "**'The Happiness Trap' by Russ Harris** - ACT approach to managing difficult thoughts",
        "**'Feeling Good' by David Burns** - CBT techniques for depression",
        "**'The Body Keeps the Score' by Bessel van der Kolk** - Trauma and healing",
        "**'Mind Over Mood' by Dennis Greenberger** - CBT workbook for various issues",
        "**'The Dialectical Behavior Therapy Skills Workbook' by McKay** - DBT skills"
    ]
}

def enhance_response_with_psychology(user_input, base_response):
    """Enhance AI response with psychological concepts"""
    user_lower = user_input.lower()
    
    # Check for specific topics and add relevant psychology
    enhancements = []
    
    if any(word in user_lower for word in ['anxious', 'worry', 'panic', 'fear']):
        enhancements.append(
            "**From an anxiety perspective**: This might relate to the **amygdala's threat detection system**. "
            "When we perceive threat (real or imagined), our body prepares for fight-or-flight. "
            "Grounding techniques help bring you back to the present moment where you're actually safe."
        )
    
    if any(word in user_lower for word in ['sad', 'depressed', 'hopeless', 'empty']):
        enhancements.append(
            "**Considering depression**: Research shows depression often involves **reduced behavioral activation**. "
            "The 'opposite action' technique from DBT suggests doing the opposite of what depression urges "
            "(like staying in bed) can help break the cycle. Even small activities matter."
        )
    
    if any(word in user_lower for word in ['stress', 'overwhelmed', 'pressure']):
        enhancements.append(
            "**Stress response insight**: Chronic stress activates the **HPA axis** (hypothalamic-pituitary-adrenal), "
            "releasing cortisol. Mindfulness practices have been shown to reduce cortisol levels and "
            "increase prefrontal cortex activity for better decision-making."
        )
    
    if any(word in user_lower for word in ['angry', 'frustrated', 'irritated']):
        enhancements.append(
            "**Anger perspective**: Anger often masks underlying emotions like hurt, fear, or vulnerability. "
            "The **STOP technique** can help: Stop, Take a breath, Observe, Proceed mindfully."
        )
    
    # Add random psychology insight if no specific match
    if not enhancements:
        random_concept = random.choice(list(PSYCHOLOGY_KNOWLEDGE['psychology_concepts'].keys()))
        random_definition = PSYCHOLOGY_KNOWLEDGE['psychology_concepts'][random_concept]
        enhancements.append(f"**Psychology Insight**: {random_concept} - {random_definition}")
    
    # Combine base response with psychology enhancements
    enhanced_response = base_response + "\n\n" + "\n\n".join(enhancements[:2])  # Limit to 2 enhancements
    
    # Occasionally suggest a therapy book
    if random.random() < 0.3:  # 30% chance
        suggested_book = random.choice(PSYCHOLOGY_KNOWLEDGE['therapy_books'])
        enhanced_response += f"\n\n**Book Suggestion**: You might find {suggested_book} helpful for deeper understanding."
    
    return enhanced_response

# psychology database
PSYCHOEDUCATION_DB = {
    "anxiety": {
        "concept": "the amygdala's threat detection system",
        "explanation": "Your brain has a primitive alarm system designed to protect you. Sometimes it gets overly sensitive and reacts to non-threatening situations.",
        "technique": "grounding exercises",
        "book": "'The Anxiety and Phobia Workbook' by Edmund Bourne"
    },
    "depression": {
        "concept": "the behavioral activation system",
        "explanation": "Depression often involves reduced engagement with rewarding activities, creating a cycle of low mood and inactivity.",
        "technique": "activity scheduling",
        "book": "'Feeling Good' by David Burns"
    },
    "stress": {
        "concept": "the HPA axis",
        "explanation": "Chronic stress keeps your cortisol levels elevated, which can affect sleep, digestion, and immune function.",
        "technique": "mindfulness meditation",
        "book": "'The Relaxation and Stress Reduction Workbook' by Davis, Eshelman & McKay"
    },
    "trauma": {
        "concept": "the window of tolerance",
        "explanation": "Trauma can narrow your ability to manage emotions effectively. The goal is to widen this window through regulation skills.",
        "technique": "grounding and resourcing",
        "book": "'The Body Keeps the Score' by Bessel van der Kolk"
    }
}

TECHNIQUES_DB = [
    {
        "name": "Cognitive Reframing",
        "brief_instructions": "Identify the automatic thought, examine evidence for and against it, then create a more balanced thought.",
        "exercise": "Write down the thought that's bothering you, rate how much you believe it (0-100%), then challenge it with evidence.",
        "suggestion": "keeping a thought record this week",
        "steps": ["Identify the thought", "Rate belief in it", "Find evidence for/against", "Create balanced thought"]
    },
    {
        "name": "Grounding (5-4-3-2-1)",
        "brief_instructions": "Name 5 things you see, 4 things you feel, 3 things you hear, 2 things you smell, 1 thing you taste.",
        "exercise": "Right now, look around and name 5 things you can see in detail.",
        "suggestion": "practicing the 5-4-3-2-1 technique when feeling overwhelmed",
        "steps": ["Pause", "Notice 5 things you see", "Notice 4 things you feel", "Notice 3 things you hear", "Notice 2 things you smell", "Notice 1 thing you taste"]
    }
]

def generate_therapist_response(user_input, conversation_history):
    """Generate therapist-style responses with psychological depth"""
    
    # Therapeutic response templates
    THERAPEUTIC_RESPONSES = {
        'exploration': [
            "I hear you saying {summary}. Could you tell me more about how this has been affecting you?",
            "It sounds like {emotion} has been quite present for you. When did you first notice this feeling?",
            "Thank you for sharing that. What's it like for you to talk about this?",
            "I'm wondering if {issue} connects to any patterns you've noticed in your life?"
        ],
        'validation': [
            "That sounds really difficult. Anyone in your situation might feel {emotion}.",
            "Your feelings make complete sense given what you're experiencing.",
            "It takes courage to acknowledge {issue}. Thank you for trusting me with this.",
            "I can see how {situation} would lead to feeling {emotion}."
        ],
        'psychoeducation': [
            "From a psychological perspective, {issue} often relates to {concept}. {explanation}",
            "Research shows that {technique} can be particularly helpful for {issue}.",
            "The brain has a natural tendency to {pattern}, which might explain why {observation}.",
            "Many people find that understanding {concept} helps them make sense of {experience}."
        ],
        'intervention': [
            "Would you be willing to try a brief exercise? {exercise}",
            "I'd like to suggest a technique called {technique}. {instructions}",
            "This week, you might experiment with {suggestion} and notice what happens.",
            "Let's practice {skill} together. First, {step_one}..."
        ],
        'reflection': [
            "So what I'm hearing is {summary}. Is that accurate?",
            "It seems like the core issue might be {core_issue}. Does that resonate?",
            "I notice you mentioned {theme} several times. I wonder what that means to you?",
            "Let me reflect back what I'm understanding: {paraphrase}"
        ]
    }
    
    # Extract key information from user input
    emotions = detect_emotions(user_input)
    issues = detect_issues(user_input)
    
    # Build therapeutic response
    response_parts = []
    
    # Start with validation (if emotions detected)
    if emotions:
        emotion_word = random.choice(emotions)
        response_parts.append(random.choice(THERAPEUTIC_RESPONSES['validation']).format(
            emotion=emotion_word, issue=issues[0] if issues else "this"
        ))
    
    # Add exploration
    response_parts.append(random.choice(THERAPEUTIC_RESPONSES['exploration']).format(
        summary=summarize_user_input(user_input),
        emotion=emotions[0] if emotions else "that",
        issue=issues[0] if issues else "what you're experiencing"
    ))
    
    # Add psychoeducation (if relevant issue detected)
    if issues and random.random() < 0.6:  # 60% chance
        issue = issues[0]
        if issue in PSYCHOEDUCATION_DB:
            psychoeducation = PSYCHOEDUCATION_DB[issue]
            response_parts.append(random.choice(THERAPEUTIC_RESPONSES['psychoeducation']).format(
                issue=issue,
                concept=psychoeducation['concept'],
                explanation=psychoeducation['explanation'],
                technique=psychoeducation['technique'],
                observation="you're experiencing this"
            ))
    
    # Add intervention suggestion (40% chance)
    if random.random() < 0.4:
        technique = random.choice(TECHNIQUES_DB)
        response_parts.append(random.choice(THERAPEUTIC_RESPONSES['intervention']).format(
            technique=technique['name'],
            instructions=technique['brief_instructions'],
            exercise=technique['exercise'],
            suggestion=technique['suggestion'],
            step_one=technique['steps'][0] if technique['steps'] else "take a deep breath"
        ))
    
    # End with reflective question
    response_parts.append(random.choice(THERAPEUTIC_RESPONSES['reflection']).format(
        summary=summarize_user_input(user_input)[:100],
        core_issue=issues[0] if issues else "what's most important to address",
        theme=detect_themes(user_input)[0] if detect_themes(user_input) else "this",
        paraphrase=paraphrase_user_input(user_input)
    ))
    
    return "\n\n".join(response_parts)

def detect_emotions(text):
    """Detect emotions in text"""
    emotion_keywords = {
        'sad': ['sad', 'depressed', 'hopeless', 'empty', 'down', 'blue'],
        'anxious': ['anxious', 'worried', 'nervous', 'panic', 'fear', 'scared'],
        'angry': ['angry', 'mad', 'furious', 'irritated', 'frustrated'],
        'stressed': ['stressed', 'overwhelmed', 'pressure', 'burned out'],
        'lonely': ['lonely', 'isolated', 'alone', 'disconnected']
    }
    
    emotions_found = []
    text_lower = text.lower()
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            emotions_found.append(emotion)
    
    return emotions_found if emotions_found else ['upset', 'concerned']

def detect_issues(text):
    """Detect psychological issues in text"""
    issue_keywords = {
        'relationships': ['relationship', 'partner', 'friend', 'family', 'social'],
        'work': ['work', 'job', 'career', 'boss', 'colleague'],
        'self-esteem': ['worth', 'confidence', 'self-esteem', 'inadequate'],
        'trauma': ['trauma', 'abuse', 'past', 'memory', 'flashback'],
        'grief': ['loss', 'grief', 'death', 'passed away', 'mourning']
    }
    
    issues_found = []
    text_lower = text.lower()
    
    for issue, keywords in issue_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            issues_found.append(issue)
    
    return issues_found

# ========== SLEEP MANAGEMENT FUNCTIONS ==========

def record_sleep_entry(sleep_hours, sleep_quality, wakeups, notes="", bedtime="", waketime=""):
    """Record a sleep entry in the database"""
    today = date.today().isoformat()
    timestamp = datetime.now()
    
    try:
        cursor.execute('''
            INSERT INTO sleep_data (date, timestamp, sleep_hours, sleep_quality, wakeups, notes, bedtime, waketime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            today,
            timestamp.isoformat(),
            sleep_hours,
            sleep_quality,
            wakeups,
            notes,
            bedtime,
            waketime
        ))
        conn.commit()
        
        # Update session state
        sleep_entry = {
            "date": today,
            "timestamp": timestamp,
            "sleep_hours": sleep_hours,
            "sleep_quality": sleep_quality,
            "wakeups": wakeups,
            "notes": notes,
            "bedtime": bedtime,
            "waketime": waketime
        }
        
        if 'sleep_history' not in st.session_state:
            st.session_state.sleep_history = []
        st.session_state.sleep_history.append(sleep_entry)
        
        if 'daily_sleep' not in st.session_state:
            st.session_state.daily_sleep = {}
        st.session_state.daily_sleep[today] = sleep_entry
        
        print(f"✅ Saved sleep data: {sleep_hours} hours, quality: {sleep_quality}")
        return sleep_entry
        
    except Exception as e:
        print(f"❌ Database error saving sleep: {e}")
        return None

def get_sleep_history():
    """Load sleep history from database"""
    cursor.execute("SELECT * FROM sleep_data ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    sleep_history = []
    
    for row in rows:
        sleep_entry = {
            "date": row[1],
            "timestamp": datetime.fromisoformat(row[2]),
            "sleep_hours": row[3],
            "sleep_quality": row[4],
            "wakeups": row[5],
            "notes": row[6],
            "bedtime": row[7],
            "waketime": row[8]
        }
        sleep_history.append(sleep_entry)
    
    return sleep_history

def get_bedtime_routines():
    """Load bedtime routines from database"""
    cursor.execute("SELECT * FROM bedtime_routines ORDER BY created_at DESC")
    rows = cursor.fetchall()
    routines = []
    
    for row in rows:
        routine = {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "activities": row[3],
            "reminder_time": row[4],
            "enabled": row[5],
            "created_at": row[6]
        }
        routines.append(routine)
    
    return routines

def save_bedtime_routine(name, description, activities, reminder_time):
    """Save a new bedtime routine"""
    created_at = datetime.now().isoformat()
    
    try:
        cursor.execute('''
            INSERT INTO bedtime_routines (name, description, activities, reminder_time, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            description,
            activities,
            reminder_time,
            1,  # Enabled by default
            created_at
        ))
        conn.commit()
        print(f"✅ Saved bedtime routine: {name}")
        return True
    except Exception as e:
        print(f"❌ Database error saving routine: {e}")
        return False

def create_sleep_chart(days=7):
    """Create a sleep chart for the last N days"""
    if 'daily_sleep' not in st.session_state or not st.session_state.daily_sleep:
        return None
    
    # Get last N days
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    dates = []
    sleep_hours = []
    sleep_quality = []
    colors = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        if date_str in st.session_state.daily_sleep:
            entry = st.session_state.daily_sleep[date_str]
            dates.append(current_date)
            sleep_hours.append(entry["sleep_hours"])
            sleep_quality.append(entry["sleep_quality"])
            # Color based on quality (1-5 scale)
            if entry["sleep_quality"] >= 4:
                colors.append("#4CAF50")  # Green for good quality
            elif entry["sleep_quality"] >= 3:
                colors.append("#FFC107")  # Yellow for medium quality
            else:
                colors.append("#F44336")  # Red for poor quality
        else:
            dates.append(current_date)
            sleep_hours.append(None)
            sleep_quality.append(None)
            colors.append("#CCCCCC")
        
        current_date += timedelta(days=1)
    
    # Create Plotly figure for sleep hours
    fig = go.Figure()
    
    # Add sleep hours bars
    fig.add_trace(go.Bar(
        x=dates,
        y=sleep_hours,
        name='Sleep Hours',
        marker_color=colors,
        text=[f"{h:.1f} hrs" if h else "No data" for h in sleep_hours],
        textposition='auto',
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Sleep Hours - Last {days} Days",
        xaxis_title="Date",
        yaxis_title="Sleep Hours",
        yaxis=dict(range=[0, 12]),
        height=300,
        hovermode='x unified',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

def create_mood_sleep_correlation_chart(days=30):
    """Create a chart showing correlation between mood and sleep"""
    if not st.session_state.daily_moods or not st.session_state.daily_sleep:
        return None
    
    dates = []
    mood_values = []
    sleep_hours = []
    sleep_quality = []
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        if date_str in st.session_state.daily_moods and date_str in st.session_state.daily_sleep:
            mood_entry = st.session_state.daily_moods[date_str]
            sleep_entry = st.session_state.daily_sleep[date_str]
            dates.append(current_date)
            mood_values.append(mood_entry["mood_value"])
            sleep_hours.append(sleep_entry["sleep_hours"])
            sleep_quality.append(sleep_entry["sleep_quality"])
        
        current_date += timedelta(days=1)
    
    if not dates:
        return None
    
    # Create correlation chart
    fig = go.Figure()
    
    # Add scatter plot
    fig.add_trace(go.Scatter(
        x=sleep_hours,
        y=mood_values,
        mode='markers',
        name='Mood vs Sleep Hours',
        marker=dict(
            size=10,
            color=sleep_quality,
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Sleep Quality")
        ),
        text=[f"Date: {d.strftime('%Y-%m-%d')}<br>Sleep: {h:.1f} hrs<br>Mood: {m}/5" 
              for d, h, m in zip(dates, sleep_hours, mood_values)],
        hoverinfo='text'
    ))
    
    # Add trend line
    if len(sleep_hours) > 1:
        import numpy as np
        z = np.polyfit(sleep_hours, mood_values, 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=sleep_hours,
            y=p(sleep_hours),
            mode='lines',
            name='Trend',
            line=dict(color='#4A90E2', width=2, dash='dash')
        ))
    
    # Update layout
    fig.update_layout(
        title="Mood vs Sleep Correlation",
        xaxis_title="Sleep Hours",
        yaxis_title="Mood Level (1-5)",
        yaxis=dict(range=[0.5, 5.5]),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

def get_sleep_analysis():
    """Generate sleep analysis text"""
    if 'sleep_history' not in st.session_state or not st.session_state.sleep_history:
        return "Track your sleep to see insights here!"
    
    sleep_data = st.session_state.sleep_history
    last_7_days = sleep_data[:7]  # Most recent 7 entries
    
    if not last_7_days:
        return "Not enough sleep data yet!"
    
    # Calculate averages
    avg_hours = sum(entry["sleep_hours"] for entry in last_7_days) / len(last_7_days)
    avg_quality = sum(entry["sleep_quality"] for entry in last_7_days) / len(last_7_days)
    avg_wakeups = sum(entry["wakeups"] for entry in last_7_days) / len(last_7_days)
    
    analysis = []
    
    # Overall assessment
    if avg_hours >= 7:
        sleep_duration = "adequate"
    elif avg_hours >= 6:
        sleep_duration = "moderate"
    else:
        sleep_duration = "insufficient"
    
    analysis.append(f"**Sleep Duration**: You're getting {avg_hours:.1f} hours on average ({sleep_duration}).")
    
    # Quality assessment
    if avg_quality >= 4:
        quality_desc = "good quality"
    elif avg_quality >= 3:
        quality_desc = "moderate quality"
    else:
        quality_desc = "poor quality"
    
    analysis.append(f"**Sleep Quality**: Average quality is {avg_quality:.1f}/5 ({quality_desc}).")
    
    # Wakeups assessment
    if avg_wakeups == 0:
        wakeup_desc = "rarely wake up"
    elif avg_wakeups <= 1:
        wakeup_desc = "wake up occasionally"
    else:
        wakeup_desc = "frequently wake up"
    
    analysis.append(f"**Sleep Continuity**: You {wakeup_desc} during the night.")
    
    # Compare with recommended
    if avg_hours < 7:
        analysis.append("💡 **Tip**: Adults typically need 7-9 hours of sleep for optimal health.")
    
    # Check correlation with mood if available
    if st.session_state.mood_history:
        # Find days with both sleep and mood data
        combined_data = []
        for sleep_entry in sleep_data[:14]:  # Last 14 days
            date_str = sleep_entry["date"]
            if date_str in st.session_state.daily_moods:
                mood_entry = st.session_state.daily_moods[date_str]
                combined_data.append({
                    "sleep_hours": sleep_entry["sleep_hours"],
                    "sleep_quality": sleep_entry["sleep_quality"],
                    "mood": mood_entry["mood_value"]
                })
        
        if len(combined_data) >= 5:
            # Simple correlation calculation
            sleep_hours_list = [d["sleep_hours"] for d in combined_data]
            mood_list = [d["mood"] for d in combined_data]
            
            if len(set(sleep_hours_list)) > 1:  # Check if there's variation
                import numpy as np
                correlation = np.corrcoef(sleep_hours_list, mood_list)[0, 1]
                
                if correlation > 0.3:
                    analysis.append("📈 **Pattern**: Better sleep appears to correlate with better mood!")
                elif correlation < -0.3:
                    analysis.append("📉 **Pattern**: Less sleep appears to correlate with lower mood.")
    
    return "\n\n".join(analysis)

def show_sleep_tracker():
    """Display sleep tracking interface"""
    st.title("💤 Sleep Tracker")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Track Sleep", "📈 Sleep Analytics", "🌙 Bedtime Routines", "📤 Export Data"])
    
    with tab1:
        st.subheader("Log Today's Sleep")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sleep_hours = st.slider("Sleep Hours", 0.0, 12.0, 7.0, 0.5, 
                                   help="How many hours did you sleep?")
        
        with col2:
            sleep_quality = st.slider("Sleep Quality", 1, 5, 3,
                                     help="1 = Very poor, 5 = Excellent")
        
        with col3:
            wakeups = st.number_input("Number of Wakeups", 0, 10, 0,
                                     help="How many times did you wake up during the night?")
        
        col4, col5 = st.columns(2)
        with col4:
            bedtime = st.time_input("Bedtime", value=datetime.strptime("22:30", "%H:%M").time())
        with col5:
            waketime = st.time_input("Wake Time", value=datetime.strptime("06:30", "%H:%M").time())
        
        notes = st.text_area("Sleep Notes (optional)", 
                           placeholder="How did you feel when you woke up? Any dreams?")
        
        if st.button("💾 Save Sleep Entry", type="primary", use_container_width=True):
            sleep_entry = record_sleep_entry(
                sleep_hours=sleep_hours,
                sleep_quality=sleep_quality,
                wakeups=wakeups,
                notes=notes,
                bedtime=bedtime.strftime("%H:%M"),
                waketime=waketime.strftime("%H:%M")
            )
            
            if sleep_entry:
                st.success(f"✅ Sleep recorded: {sleep_hours} hours, Quality: {sleep_quality}/5")
                st.rerun()
    
    with tab2:
        st.subheader("Sleep Analytics")
        
        # Time range selector
        time_range = st.select_slider(
            "Time range:",
            options=["7 days", "14 days", "30 days", "All time"],
            value="7 days"
        )
        
        days_map = {"7 days": 7, "14 days": 14, "30 days": 30, "All time": 90}
        days = days_map[time_range]
        
        # Sleep chart
        sleep_chart = create_sleep_chart(min(days, len(st.session_state.daily_sleep) if 'daily_sleep' in st.session_state else 0))
        if sleep_chart:
            st.plotly_chart(sleep_chart, use_container_width=True)
        else:
            st.info("No sleep data to show. Start tracking your sleep!")
        
        # Mood-sleep correlation
        if st.session_state.daily_moods and 'daily_sleep' in st.session_state and st.session_state.daily_sleep:
            st.subheader("Mood-Sleep Correlation")
            correlation_chart = create_mood_sleep_correlation_chart(min(30, days))
            if correlation_chart:
                st.plotly_chart(correlation_chart, use_container_width=True)
                
                # Show correlation analysis
                st.markdown("### 📊 Correlation Insights")
                st.markdown("""
                **What this chart shows:**
                • Each point represents a day with both sleep and mood data
                • Color indicates sleep quality (green = good, red = poor)
                • Trend line shows overall relationship
                
                **What to look for:**
                ↗️ **Upward trend** = More sleep → Better mood
                ↘️ **Downward trend** = More sleep → Worse mood
                ➡️ **Flat trend** = No clear relationship
                """)
            else:
                st.info("Need more data to show correlation (at least 5 days with both sleep and mood)")
        
        # Sleep analysis text
        sleep_analysis = get_sleep_analysis()
        st.markdown("### 📋 Sleep Insights")
        st.markdown(sleep_analysis)
    
    with tab3:
        st.subheader("Bedtime Routines")
        
        # Load existing routines
        routines = get_bedtime_routines()
        
        # Create new routine
        with st.expander("➕ Create New Routine", expanded=not routines):
            st.write("Build a personalized bedtime routine to improve sleep quality.")
            
            routine_name = st.text_input("Routine Name", placeholder="e.g., Relaxing Wind-Down")
            routine_desc = st.text_area("Description", placeholder="Describe your routine")
            
            st.write("**Select Activities:**")
            col1, col2 = st.columns(2)
            
            activities = []
            with col1:
                if st.checkbox("Meditation (10 min)"):
                    activities.append("🧘 10-minute meditation")
                if st.checkbox("Reading (20 min)"):
                    activities.append("📚 Read a book for 20 minutes")
                if st.checkbox("Warm shower"):
                    activities.append("🚿 Take a warm shower")
                if st.checkbox("Herbal tea"):
                    activities.append("☕ Drink herbal tea")
            
            with col2:
                if st.checkbox("Light stretching"):
                    activities.append("💪 Gentle stretching")
                if st.checkbox("Journaling"):
                    activities.append("📝 Journal thoughts")
                if st.checkbox("Gratitude practice"):
                    activities.append("🙏 List 3 things you're grateful for")
                if st.checkbox("Device-free time"):
                    activities.append("📵 No screens 1 hour before bed")
            
            reminder_time = st.time_input("Reminder Time", 
                                         value=datetime.strptime("21:00", "%H:%M").time(),
                                         help="When should we remind you to start your routine?")
            
            if st.button("Save Routine", type="primary"):
                if routine_name and activities:
                    activities_text = "\n".join(activities)
                    success = save_bedtime_routine(
                        name=routine_name,
                        description=routine_desc,
                        activities=activities_text,
                        reminder_time=reminder_time.strftime("%H:%M")
                    )
                    
                    if success:
                        st.success(f"✅ Routine '{routine_name}' saved!")
                        st.rerun()
                else:
                    st.warning("Please provide a routine name and select at least one activity.")
        
        # Display existing routines
        if routines:
            st.markdown("---")
            st.subheader("Your Routines")
            
            for i, routine in enumerate(routines):
                with st.expander(f"{routine['name']} ⏰ {routine['reminder_time']}", expanded=i==0):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if routine['description']:
                            st.write(routine['description'])
                        
                        st.markdown("**Activities:**")
                        activities_list = routine['activities'].split('\n')
                        for activity in activities_list:
                            st.write(f"• {activity}")
                    
                    with col2:
                        status = "🟢 Enabled" if routine['enabled'] else "🔴 Disabled"
                        st.write(status)
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("🔔", key=f"remind_{i}", help="Set reminder"):
                                st.info(f"Reminder set for {routine['reminder_time']}")
                        with col_btn2:
                            if st.button("🗑️", key=f"delete_{i}", help="Delete routine"):
                                cursor.execute("DELETE FROM bedtime_routines WHERE id = ?", (routine['id'],))
                                conn.commit()
                                st.success("Routine deleted!")
                                st.rerun()
        
        # Quick routine templates
        st.markdown("---")
        st.subheader("Quick Routine Templates")
        
        template_col1, template_col2 = st.columns(2)
        
        with template_col1:
            if st.button("🌙 Relaxation Focus", use_container_width=True):
                st.session_state.routine_template = {
                    "name": "Relaxation Focus",
                    "desc": "Calm your mind and body before sleep",
                    "activities": [
                        "🧘 10-minute meditation",
                        "🚿 Warm shower",
                        "☕ Herbal tea",
                        "📝 Journal thoughts"
                    ],
                    "time": "21:00"
                }
                st.rerun()
        
        with template_col2:
            if st.button("📱 Digital Detox", use_container_width=True):
                st.session_state.routine_template = {
                    "name": "Digital Detox",
                    "desc": "Reduce screen time for better sleep",
                    "activities": [
                        "📵 No screens 1 hour before bed",
                        "📚 Read a physical book",
                        "🙏 Gratitude practice",
                        "💪 Light stretching"
                    ],
                    "time": "21:30"
                }
                st.rerun()
        
        # Apply template if selected
        if 'routine_template' in st.session_state:
            template = st.session_state.routine_template
            st.info(f"Template loaded: {template['name']}")
            
            if st.button(f"Use {template['name']} Template"):
                activities_text = "\n".join(template['activities'])
                success = save_bedtime_routine(
                    name=template['name'],
                    description=template['desc'],
                    activities=activities_text,
                    reminder_time=template['time']
                )
                
                if success:
                    st.success(f"✅ Routine '{template['name']}' created from template!")
                    del st.session_state.routine_template
                    st.rerun()
    
    with tab4:
        st.subheader("Export Your Data")
        st.write("Download your mood and sleep data for personal analysis or to share with healthcare professionals.")
        
        # Export mood data
        st.markdown("### 📊 Mood Data")
        mood_csv = export_mood_data()
        if mood_csv:
            st.download_button(
                label="⬇️ Download Mood Data (CSV)",
                data=mood_csv,
                file_name=f"mindful_companion_mood_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("Includes: Date, Mood, Mood Value, Category, Notes")
        else:
            st.info("No mood data available to export")
        
        # Export sleep data
        st.markdown("### 💤 Sleep Data")
        sleep_csv = export_sleep_data()
        if sleep_csv:
            st.download_button(
                label="⬇️ Download Sleep Data (CSV)",
                data=sleep_csv,
                file_name=f"mindful_companion_sleep_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("Includes: Date, Sleep Hours, Quality, Wakeups, Bedtime, Waketime, Notes")
        else:
            st.info("No sleep data available to export")
        
        # Export combined data
        st.markdown("### 📈 Combined Data")
        combined_csv = export_combined_data()
        if combined_csv:
            st.download_button(
                label="⬇️ Download Combined Data (CSV)",
                data=combined_csv,
                file_name=f"mindful_companion_mood_sleep_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.caption("Includes: Date, Mood Data, Sleep Data (combined for each day)")
        else:
            st.info("No data available to export")
        
        # Data format information
        st.markdown("---")
        with st.expander("📋 Data Format Information", expanded=False):
            st.markdown("""
            **CSV File Format:**
            
            **Mood Data Columns:**
            - `Date`: Date of entry (YYYY-MM-DD)
            - `Timestamp`: Full timestamp
            - `Mood`: Mood emoji and name (e.g., 😊 Happy)
            - `Mood_Value`: Numerical value (1-5)
            - `Category`: positive/neutral/negative
            - `Notes`: Additional notes
            - `Color`: Color code for visualization
            
            **Sleep Data Columns:**
            - `Date`: Date of entry (YYYY-MM-DD)
            - `Timestamp`: Full timestamp
            - `Sleep_Hours`: Hours slept (0.0-12.0)
            - `Sleep_Quality`: Quality rating (1-5)
            - `Wakeups`: Number of times woke up
            - `Bedtime`: When you went to bed (HH:MM)
            - `Waketime`: When you woke up (HH:MM)
            - `Notes`: Additional sleep notes
            
            **Combined Data Columns:**
            - All mood and sleep columns combined
            - Empty cells where data is missing
            - Perfect for correlation analysis
            """)
    
    # Back button
    st.markdown("---")
    if st.button("Back to Chat", type="primary"):
        st.session_state.show_sleep_tracker = False
        st.rerun()      
        
def show_mood_history():
    """Display mood history and analytics"""
    st.title("📊 Mood Tracker")
    
    if not st.session_state.mood_history:
        st.info("No mood data yet. Start by recording your mood!")
        if st.button("Back to Chat"):
            st.session_state.show_mood_history = False
            st.rerun()
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "📊 Analytics", "📝 History"])
    
    with tab1:
        # Time range selector
        time_range = st.select_slider(
            "Time range:",
            options=["7 days", "14 days", "30 days", "All time"],
            value="7 days"
        )
        
        days_map = {"7 days": 7, "14 days": 14, "30 days": 30, "All time": 90}
        days = days_map[time_range]
        
        # Create mood chart
        fig = create_mood_chart(min(days, len(st.session_state.daily_moods)))
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data to show trends yet.")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Mood distribution
            dist_fig = create_mood_distribution_chart()
            if dist_fig:
                st.plotly_chart(dist_fig, use_container_width=True)
            else:
                st.info("No data for distribution chart.")
        
        with col2:
            # Mood insights
            st.subheader("📋 Insights")
            analysis = get_mood_analysis()
            st.markdown(analysis)
            
            # Weekly pattern if available
            if st.session_state.mood_insights['mood_patterns']:
                st.markdown("---")
                st.write("**Weekly Mood Pattern:**")
                for day, avg in sorted(st.session_state.mood_insights['mood_patterns'].items()):
                    st.write(f"{day}: {'⭐' * int(avg)} ({avg:.1f}/5)")
    
    with tab3:
        # Recent mood entries
        st.subheader("Recent Mood Entries")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_mood = st.selectbox(
                "Filter by mood:",
                ["All"] + list(MOOD_OPTIONS.keys())
            )
        with col2:
            sort_order = st.radio("Sort by:", ["Newest first", "Oldest first"])
        
        # Display mood entries
        filtered_history = st.session_state.mood_history.copy()
        
        if filter_mood != "All":
            filtered_history = [m for m in filtered_history if m["mood"] == filter_mood]
        
        if sort_order == "Oldest first":
            filtered_history = filtered_history[::-1]
        
        if not filtered_history:
            st.info("No entries match your filter.")
        else:
            for entry in filtered_history[:20]:  # Show last 20 entries
                with st.expander(f"{entry['timestamp'].strftime('%Y-%m-%d %H:%M')} - {entry['mood']}"):
                    col_a, col_b = st.columns([1, 3])
                    with col_a:
                        st.markdown(f"**Mood:** {entry['mood']}")
                        st.markdown(f"<div style='background-color:{entry['color']}; padding:5px; border-radius:5px; width:50px; height:20px;'></div>", 
                                   unsafe_allow_html=True)
                    with col_b:
                        if entry['notes']:
                            st.write(f"**Note:** {entry['notes']}")
                        else:
                            st.caption("No note added")
        # Add export section
    st.markdown("---")
    st.subheader("📤 Export Mood Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = export_mood_data()
        if csv:
            st.download_button(
                label="⬇️ Download Mood CSV",
                data=csv,
                file_name=f"mood_data_{date.today().isoformat()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No mood data to export")
    
    with col2:
        if st.button("Export All Data", use_container_width=True):
            st.session_state.show_sleep_tracker = True
            st.rerun()
    
    # Back button
    st.markdown("---")
    if st.button("Back to Chat", type="primary"):
        st.session_state.show_mood_history = False
        st.rerun()
   

def export_mood_data():
    """Export mood data as CSV"""
    if not st.session_state.mood_history:
        return None
    
    df = pd.DataFrame(st.session_state.mood_history)
    # Convert timestamp to string for CSV
    df['timestamp'] = df['timestamp'].apply(lambda x: x.isoformat())
    return df.to_csv(index=False)

# ========== MAIN APPLICATION ==========
def main():
    """Main chatbot interface"""
   
    # Initialize theme if not set
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
        
    # Initialize mood history view
    if 'show_mood_history' not in st.session_state:
        st.session_state.show_mood_history = False
    
    # Initialize sleep tracker view
    if 'show_sleep_tracker' not in st.session_state:
        st.session_state.show_sleep_tracker = False
    
    # Load sleep data
    if 'sleep_history' not in st.session_state:
        st.session_state.sleep_history = get_sleep_history()
        st.session_state.daily_sleep = {}
        for entry in st.session_state.sleep_history:
            st.session_state.daily_sleep[entry["date"]] = entry
    
    # Check if we should show sleep tracker
    if st.session_state.show_sleep_tracker:
        show_sleep_tracker()
        return
    
    # Check if we should show mood history
    if st.session_state.show_mood_history:
        show_mood_history()
        return
    
    # Create a container for the toggle in top right
    toggle_container = st.container()
    
    with toggle_container:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            # Header
            st.title("🧠 Mindful Companion")
            st.markdown("<h3 style='text-align: center; font-weight: bold;'>A safe space to talk. I'm here to listen.</h3>", unsafe_allow_html=True)
        
        with col2:
            # Dark/Light mode toggle
            st.markdown("<div class='mode-toggle'>", unsafe_allow_html=True)
            
            # Create the toggle switch
            if st.button("🌙" if st.session_state.theme == 'light' else "☀️", 
                        key="theme_toggle", 
                        help="Toggle dark/light mode"):
                toggle_theme()
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Apply current theme
    if st.session_state.theme == 'dark':
        st.markdown("""
        <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            .stSidebar {
                background-color: #262730;
            }
            .user-message {
                background-color: #2d3746;
            }
            .bot-message {
                background-color: #3a4a5f;
            }
            .stChatInput textarea {
                background-color: #262730;
                color: #fafafa;
            }
            .stChatInput button {
                background-color: #4a5568;
                color: white;
            }
            .stButton button {
                background-color: #4a5568;
                color: white;
            }
            .stSelectbox div[data-baseweb="select"] {
                background-color: #262730;
                color: #fafafa;
            }
            .stTextInput input {
                background-color: #262730;
                color: #fafafa;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Footnote at the bottom
    st.markdown("---")
    st.markdown("<p style='text-align: center; font-size: 14px; color: #666; font-style: italic;'>💡 <b>Tip:</b> Start by sharing how you're feeling today.</p>", unsafe_allow_html=True)
    
    # Sidebar with quick exercises
    with st.sidebar:
        st.header("🌤 WELCOME")
        
        # Add model selector
        st.markdown("---")
        st.subheader("🤖 AI Model Selector")
        
        # Initialize selected model in session state
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = "Gemini (20 free/day)"
        
        # Model options
        model_options = {
            "Gemini (20 free/day)": "gemini",
            "Ollama (Local, Unlimited)": "ollama",
            "Enhanced Local AI": "local"
        }
        
        # Create dropdown
        selected_option = st.selectbox(
            "Choose AI Model:",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(st.session_state.selected_model)
        )
        
        # Update session state if changed
        if selected_option != st.session_state.selected_model:
            st.session_state.selected_model = selected_option
            st.rerun()
        
        # Show current model info
        st.caption(f"Current: {selected_option}")
        
        # Model status
        st.markdown("---")
        st.subheader("📊 Model Status")
        
        # Gemini status
        try:
            if selected_option == "Gemini (20 free/day)":
                st.success("✅ Gemini: Active")
            else:
                st.info("🔵 Gemini: Available")
        except:
            st.warning("⚠️ Gemini: Needs API key")
        
        # Ollama status
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    st.success(f"✅ Ollama: Ready")
                else:
                    st.warning("⚠️ Ollama: No models")
            else:
                st.warning("⚠️ Ollama: Not running")
        except:
            st.warning("⚠️ Ollama: Not detected")
        
        # Local AI status
        st.success("✅ Local AI: Always available")
        
        # Exercises
        st.markdown("---")
        st.subheader("🩺 Quick Exercises")
        
        if st.button("5-4-3-2-1 Grounding"):
            st.info("""
            **Notice:**
            5 things you can see
            4 things you can touch
            3 things you can hear
            2 things you can smell
            1 thing you can taste
            """)
        
        if st.button("Deep Breathing"):
            st.info("""
            **4-7-8 Breathing:**
            1. Inhale for 4 seconds
            2. Hold for 7 seconds
            3. Exhale for 8 seconds
            4. Repeat 4 times
            """)
        
        st.markdown("---")
        st.write(f"**Session started:** {st.session_state.session_start.strftime('%I:%M %p')}")
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        
        # ADD RESOURCES SECTION HERE
        add_resources_to_sidebar()
        
        # Mood Tracking Section
        st.markdown("---")
        st.subheader("📊 Mood & Sleep Tracker")
        
        # Quick mood check-in
        st.write("**How are you feeling right now?**")
        
        # Initialize selected mood in session state
        if 'selected_mood' not in st.session_state:
            st.session_state.selected_mood = None
        
        # Display mood buttons
        cols = st.columns(5)
        mood_list = list(MOOD_OPTIONS.keys())
        
        for i, mood in enumerate(mood_list):
            with cols[i % 5]:
                if st.button(mood, key=f"mood_btn_{i}", use_container_width=True):
                    st.session_state.selected_mood = mood
                    st.session_state.show_mood_input = True
        
        # Show note input if a mood was selected
        if st.session_state.get('selected_mood'):
            notes = st.text_input(f"Add a note for {st.session_state.selected_mood} (optional):", 
                                 key="mood_notes")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Mood", type="primary", use_container_width=True):
                    record_mood(st.session_state.selected_mood, notes)
                    st.success(f"✅ Recorded: {st.session_state.selected_mood}")
                    # Reset
                    st.session_state.selected_mood = None
                    st.session_state.show_mood_input = False
                    st.rerun()
            with col2:
                if st.button("Cancel", type="secondary", use_container_width=True):
                    st.session_state.selected_mood = None
                    st.session_state.show_mood_input = False
                    st.rerun()
        
        # Quick sleep check-in
        st.markdown("---")
        st.write("**💤 Quick Sleep Log**")
        
        if 'daily_sleep' in st.session_state and date.today().isoformat() in st.session_state.daily_sleep:
            today_sleep = st.session_state.daily_sleep[date.today().isoformat()]
            st.info(f"**Today's sleep:** {today_sleep['sleep_hours']:.1f} hours, Quality: {today_sleep['sleep_quality']}/5")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Log Sleep", use_container_width=True):
                    st.session_state.show_sleep_tracker = True
                    st.rerun()
            with col2:
                if st.button("View Sleep", use_container_width=True):
                    st.session_state.show_sleep_tracker = True
                    st.rerun()
        
        # View buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 View Mood History", use_container_width=True):
                st.session_state.show_mood_history = True
                st.rerun()
        with col2:
            if st.button("💤 Sleep Tracker", use_container_width=True):
                st.session_state.show_sleep_tracker = True
                st.rerun()
        
        # Mood stats
        if st.session_state.mood_history:
            today_mood = None
            today_str = date.today().isoformat()
            if today_str in st.session_state.daily_moods:
                today_mood = st.session_state.daily_moods[today_str]["mood"]
            
            if today_mood:
                st.info(f"**Today's mood**: {today_mood}")
            else:
                st.caption("No mood recorded today")
            
            st.caption(f"**Total entries**: {len(st.session_state.mood_history)}")     
            
            # Quick insight
            if st.session_state.mood_insights['total_entries'] > 0:
                avg_mood = st.session_state.mood_insights['avg_mood']
                if avg_mood >= 4:
                    st.caption("🎯 **Insight**: Mostly positive")
                elif avg_mood >= 3:
                    st.caption("🎯 **Insight**: Generally neutral")
                else:
                    st.caption("🎯 **Insight**: Tending negative")
        
        # Sleep stats
        if 'sleep_history' in st.session_state and st.session_state.sleep_history:
            st.caption(f"**Sleep entries**: {len(st.session_state.sleep_history)}")
            
            # Quick sleep insight
            last_7_sleep = st.session_state.sleep_history[:7]
            if last_7_sleep:
                avg_sleep = sum(entry["sleep_hours"] for entry in last_7_sleep) / len(last_7_sleep)
                if avg_sleep >= 7:
                    st.caption("💤 **Sleep**: Good duration")
                elif avg_sleep >= 6:
                    st.caption("💤 **Sleep**: Moderate duration")
                else:
                    st.caption("💤 **Sleep**: Could use more")
                      
        # Cache statistics
        st.markdown("---")
        st.subheader("💾 Cache Stats")
        st.write(f"**Cache hits:** {st.session_state.cache_hits}")
        st.write(f"**Cached responses:** {len(st.session_state.response_cache)}")
        
        # Clear cache button
        if st.button("Clear Cache", type="secondary"):
            st.session_state.response_cache = {}
            st.session_state.cache_hits = 0
            st.success("Cache cleared!")
            st.rerun()
            
            
        # Export section
        st.markdown("---")
        st.subheader("📤 Export Data")
        
        if st.button("Export All Data", use_container_width=True):
            st.session_state.show_sleep_tracker = True
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message"><b>You:</b> {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message"><b>Companion:</b> {message["content"]}</div>', 
                       unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("How are you feeling today?", key="chat_input")
    
    # Check if there's new input to process
    if user_input:
        # Use a session state flag to track if we're processing this input
        processing_key = f"processing_{user_input[:20]}"
        
        if processing_key not in st.session_state:
            st.session_state[processing_key] = True
            
            # FIRST: Check cache
            cached_response = get_cached_response(user_input)
            if cached_response:
                # user message to history
                st.session_state.messages.append({"role": "user", "content": user_input})
                # cached response
                st.session_state.messages.append({"role": "assistant", "content": cached_response})
                # Remove processing flag and rerun
                del st.session_state[processing_key]
                st.rerun()
            
            # 1. Check for professional help requests
            elif any(keyword in user_input.lower() for keyword in PROFESSIONAL_HELP_KEYWORDS):
                professional_response = get_professional_help_guide()
                
                # chat history
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": professional_response})
                
                # Cache the response
                cache_response(user_input, professional_response)
                
                # Log interaction
                sentiment = detect_sentiment(user_input)
                log_mood_interaction(user_input, professional_response, sentiment)
                
                # Remove processing flag and rerun
                del st.session_state[processing_key]
                st.rerun()
            
            # 2. Check for emergency
            elif check_emergency(user_input):
                # Display emergency box
                st.markdown(f'<div class="emergency-box">{EMERGENCY_RESPONSE}</div>', 
                           unsafe_allow_html=True)
                
                # Add to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": EMERGENCY_RESPONSE})
                
                # Cache the response
                cache_response(user_input, EMERGENCY_RESPONSE)
                
                # Add mood logging
                sentiment = detect_sentiment(user_input)
                log_mood_interaction(user_input, EMERGENCY_RESPONSE, sentiment)
                
                # Remove processing flag and rerun
                del st.session_state[processing_key]
                st.rerun()
            
            # 3. Normal conversation
            else:
                # Add user message to history
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Generate AI response
                with st.spinner("Thinking..."):
                    try:
                        # Get selected model type
                        model_type = model_options[st.session_state.selected_model]
                        
                        if model_type == "gemini":
                            # ========== GEMINI MODE ==========
                            try:
                                # Initialize Gemini model if not already done
                                if 'ai_model' not in st.session_state:
                                    st.session_state.ai_model = setup_gemini_with_fallback()
                                
                                # Prepare conversation history for prompt
                                history = ""
                                for msg in st.session_state.messages[-6:]:  # Last 6 messages
                                    role = "User" if msg["role"] == "user" else "Assistant"
                                    history += f"{role}: {msg['content']}\n"
                                
                                full_prompt = f"""{create_system_prompt()}

Recent conversation:
{history}

User: {user_input}
Assistant:"""
                                
                                # Generate response
                                response = st.session_state.ai_model.generate_content(full_prompt)
                                base_response = response.text
                                
                                # ENHANCE WITH PSYCHOLOGY KNOWLEDGE
                                professional_response = enhance_response_with_psychology(user_input, base_response)
                                
                                # Cache successful response
                                cache_response(user_input, professional_response)
                                
                            except Exception as e:
                                error_msg = str(e)
                                if "quota" in error_msg.lower() or "429" in error_msg:
                                    # Quota exceeded, fallback to therapist-style local AI
                                    professional_response = generate_therapist_response(user_input, st.session_state.messages)
                                    st.warning("⚠️ Gemini quota exceeded. Using therapist AI.")
                                    cache_response(user_input, professional_response)
                                else:
                                    # Other error, switch to therapist AI
                                    professional_response = generate_therapist_response(user_input, st.session_state.messages)
                                    st.session_state.selected_model = "Enhanced Local AI"
                                    cache_response(user_input, professional_response)
                        
                        elif model_type == "ollama":
                            # ========== OLLAMA MODE ==========
                            ollama_response = get_ollama_response_simple(user_input, st.session_state.messages)
                            if ollama_response:
                                # Enhance Ollama response with psychology
                                enhanced_response = enhance_response_with_psychology(user_input, ollama_response)
                                professional_response = enhanced_response
                                cache_response(user_input, professional_response)
                            else:
                                # Ollama not available, fallback to therapist AI
                                professional_response = generate_therapist_response(user_input, st.session_state.messages)
                                st.info("Ollama not available. Using therapist AI.")
                                cache_response(user_input, professional_response)
                        
                        else:  # model_type == "local"
                            # ========== ENHANCED LOCAL AI MODE ==========
                            # Use therapist-style responses
                            professional_response = generate_therapist_response(user_input, st.session_state.messages)
                            cache_response(user_input, professional_response)
                        
                        # Add mood logging
                        sentiment = detect_sentiment(user_input)
                        mood_entry = log_mood_interaction(user_input, professional_response, sentiment)
                        
                        # Add AI response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": professional_response})
                        
                        # Remove processing flag
                        del st.session_state[processing_key]
                        
                    except Exception as e:
                        # General error handling
                        professional_response = f"[Error] {str(e)[:100]}..."
                        cache_response(user_input, professional_response)
                        
                        # Add error response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": professional_response})
                        
                        # Remove processing flag
                        if processing_key in st.session_state:
                            del st.session_state[processing_key]
                
                # Rerun to display new messages
                st.rerun()
    
    # Clear chat button
    if st.session_state.messages:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🧹 Clear Conversation", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.session_state.session_start = datetime.now()
                st.session_state.emergency_triggered = False
                st.rerun()
        with col2:
            if st.button("📊 View Stats", type="secondary", use_container_width=True):
                st.info(f"""
                **Session Statistics:**
                - Messages exchanged: {len(st.session_state.messages)}
                - Session duration: {(datetime.now() - st.session_state.session_start).seconds // 60} minutes
                - Cache hits: {st.session_state.cache_hits}
                - Cached responses: {len(st.session_state.response_cache)}
                - Mood entries: {len(st.session_state.mood_history)}
                - Sleep entries: {len(st.session_state.sleep_history) if 'sleep_history' in st.session_state else 0}
                """)
                
                
def export_mood_data():
    """Export mood data as CSV"""
    if not st.session_state.mood_history:
        return None
    
    # Create DataFrame from mood history
    mood_data = []
    for entry in st.session_state.mood_history:
        mood_data.append({
            "Date": entry["date"],
            "Timestamp": entry["timestamp"].isoformat(),
            "Mood": entry["mood"],
            "Mood_Value": entry["mood_value"],
            "Category": entry["category"],
            "Notes": entry["notes"],
            "Color": entry["color"]
        })
    
    df = pd.DataFrame(mood_data)
    return df.to_csv(index=False)

def export_sleep_data():
    """Export sleep data as CSV"""
    if 'sleep_history' not in st.session_state or not st.session_state.sleep_history:
        return None
    
    # Create DataFrame from sleep history
    sleep_data = []
    for entry in st.session_state.sleep_history:
        sleep_data.append({
            "Date": entry["date"],
            "Timestamp": entry["timestamp"].isoformat(),
            "Sleep_Hours": entry["sleep_hours"],
            "Sleep_Quality": entry["sleep_quality"],
            "Wakeups": entry["wakeups"],
            "Bedtime": entry["bedtime"],
            "Waketime": entry["waketime"],
            "Notes": entry["notes"]
        })
    
    df = pd.DataFrame(sleep_data)
    return df.to_csv(index=False)

def export_combined_data():
    """Export combined mood and sleep data as CSV"""
    combined_data = []
    
    # Get all unique dates
    all_dates = set()
    
    if st.session_state.mood_history:
        all_dates.update([entry["date"] for entry in st.session_state.mood_history])
    
    if 'sleep_history' in st.session_state and st.session_state.sleep_history:
        all_dates.update([entry["date"] for entry in st.session_state.sleep_history])
    
    if not all_dates:
        return None
    
    # Sort dates
    sorted_dates = sorted(list(all_dates))
    
    # Create combined data
    for date_str in sorted_dates:
        entry = {"Date": date_str}
        
        # Add mood data if exists
        if date_str in st.session_state.daily_moods:
            mood_entry = st.session_state.daily_moods[date_str]
            entry.update({
                "Mood": mood_entry["mood"],
                "Mood_Value": mood_entry["mood_value"],
                "Mood_Category": mood_entry["category"],
                "Mood_Notes": mood_entry["notes"]
            })
        else:
            entry.update({
                "Mood": "",
                "Mood_Value": "",
                "Mood_Category": "",
                "Mood_Notes": ""
            })
        
        # Add sleep data if exists
        if 'daily_sleep' in st.session_state and date_str in st.session_state.daily_sleep:
            sleep_entry = st.session_state.daily_sleep[date_str]
            entry.update({
                "Sleep_Hours": sleep_entry["sleep_hours"],
                "Sleep_Quality": sleep_entry["sleep_quality"],
                "Wakeups": sleep_entry["wakeups"],
                "Bedtime": sleep_entry["bedtime"],
                "Waketime": sleep_entry["waketime"],
                "Sleep_Notes": sleep_entry["notes"]
            })
        else:
            entry.update({
                "Sleep_Hours": "",
                "Sleep_Quality": "",
                "Wakeups": "",
                "Bedtime": "",
                "Waketime": "",
                "Sleep_Notes": ""
            })
        
        combined_data.append(entry)
    
    df = pd.DataFrame(combined_data)
    return df.to_csv(index=False)

def show_export_section():
    """Display export section in sleep tracker"""
    st.markdown("---")
    st.subheader("📤 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Mood Data", use_container_width=True):
            csv = export_mood_data()
            if csv:
                st.download_button(
                    label="⬇️ Download Mood CSV",
                    data=csv,
                    file_name=f"mood_data_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    key="download_mood_csv"
                )
            else:
                st.warning("No mood data to export")
    
    with col2:
        if st.button("💤 Export Sleep Data", use_container_width=True):
            csv = export_sleep_data()
            if csv:
                st.download_button(
                    label="⬇️ Download Sleep CSV",
                    data=csv,
                    file_name=f"sleep_data_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    key="download_sleep_csv"
                )
            else:
                st.warning("No sleep data to export")
    
    with col3:
        if st.button("📈 Export Combined Data", use_container_width=True):
            csv = export_combined_data()
            if csv:
                st.download_button(
                    label="⬇️ Download Combined CSV",
                    data=csv,
                    file_name=f"mood_sleep_data_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    key="download_combined_csv"
                )
            else:
                st.warning("No data to export")
                
                
# ========== RUN APP ==========
if __name__ == "__main__":
    main()