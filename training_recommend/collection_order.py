# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Information collection order configuration for the training recommendation agent.

This file can be easily replaced to modify the information collection order
without changing the main prompts.py file.
"""

# Information collection order configuration
# Each item defines: field_name, question_template
INFORMATION_COLLECTION_ORDER = [
    {
        "field": "age",
        "question": "Please tell me your age, for example: 25"
    },
    {
        "field": "gender",
        "question": "Please tell me your gender (male/female)"
    },
    {
        "field": "weight",
        "question": "Please tell me your weight (in kg), for example: 70"
    },
    {
        "field": "height",
        "question": "Please tell me your height (in cm), for example: 175"
    },
    {
        "field": "injuries",
        "question": "Have you had any injuries in the past year, especially regarding your knees, ankles, or back?"
    },
    {
        "field": "fitness_level",
        "question": "What is your current fitness level? (beginner/intermediate/advanced)"
    },
    {
        "field": "running_times_per_week",
        "question": "How many times do you run per week?"
    },
    {
        "field": "total_mileage",
        "question": "What is the total mileage on average per week (in km)?"
    },
    {
        "field": "pb",
        "question": "What is your PB (personal best) for 5km or 10km run?"
    },
    {
        "field": "training_goal",
        "question": "What is your training goal? You can select multiple: weight loss, stay fit, train for a 10km race, train for a half-marathon, or train for a full marathon"
    },
    {
        "field": "training_days",
        "question": "Which days of the week can you train, and for how long each session?"
    },
    {
        "field": "training_location",
        "question": "Where do you usually train: road, track, treadmill, or trail?"
    },
    {
        "field": "arch_type",
        "question": "Do you have low (flat), neutral, or high arches? (This helps with shoe recommendation)"
    },
    {
        "field": "shoe_wear",
        "question": "Is the wear on your old shoes heavier on the inner edge or outer edge?"
    },
    {
        "field": "shoe_feel",
        "question": "Do you prefer a soft, plush feel or firm, responsive ride?"
    },
    {
        "field": "city",
        "question": "What city or area are you located in? For example: New York"
    }
]


def get_collection_order_text() -> str:
    """Generate the information collection order text for prompts.
    
    Returns:
        str: Formatted text describing the information collection order
    """
    lines = []
    for i, item in enumerate(INFORMATION_COLLECTION_ORDER, 1):
        field_name = item["field"].replace("_", " ").title()
        question = item["question"]
        lines.append(f"{i}. **{field_name}** - Ask: \"{question}\"")
    
    return "\n".join(lines)


def get_field_order() -> list:
    """Get the ordered list of field names.
    
    Returns:
        list: List of field names in collection order
    """
    return [item["field"] for item in INFORMATION_COLLECTION_ORDER]


def get_first_question() -> str:
    """Get the first question to ask.
    
    Returns:
        str: The first question text
    """
    if INFORMATION_COLLECTION_ORDER:
        return INFORMATION_COLLECTION_ORDER[0]["question"]
    return "Please tell me your age, for example: 25"


def get_first_field_name() -> str:
    """Get the name of the first field to collect.
    
    Returns:
        str: The first field name
    """
    if INFORMATION_COLLECTION_ORDER:
        return INFORMATION_COLLECTION_ORDER[0]["field"]
    return "age"


def get_question_sequence_text() -> str:
    """Get the question sequence text for prompts.
    
    Returns:
        str: Formatted text describing the question sequence
    """
    field_names = []
    for i, item in enumerate(INFORMATION_COLLECTION_ORDER, 1):
        field_name = item["field"].replace("_", " ").title()
        field_names.append(f"Question {i}: {field_name}")
    
    return " → ".join(field_names)


def get_example_conversation_questions() -> list:
    """Get list of questions for example conversation.
    
    Returns:
        list: List of question texts in order
    """
    return [item["question"] for item in INFORMATION_COLLECTION_ORDER]


def get_example_conversation_text() -> str:
    """Generate example conversation text for prompts.
    
    Returns:
        str: Formatted example conversation text
    """
    questions = get_example_conversation_questions()
    welcome_msg = "Hello! 👋 I'm your professional training plan generation assistant. I can create a personalized weekly training plan based on your personal information, sport preferences, weather conditions, and geographical location in your area. Let me learn about your situation so I can generate the most suitable training plan for you!"
    
    lines = [
        f'Agent: "{welcome_msg} {questions[0] if questions else ""}"'
    ]
    
    # Generate example responses and follow-up questions
    example_responses = [
        "25",
        "male",
        "70",
        "175",
        "No injuries",
        "intermediate",
        "3",
        "15",
        "5km: 25:00",
        "train for a 10km race",
        "Monday/Wednesday/Friday, 1 hour each",
        "road",
        "neutral",
        "outer edge",
        "firm, responsive ride",
        "New York"
    ]
    
    for i, question in enumerate(questions[1:], 1):
        if i < len(example_responses):
            lines.append(f'User: "{example_responses[i-1]}"')
            lines.append(f'Agent: "Got it, recorded. {question}"')
    
    # Add final response and completion
    if len(example_responses) >= len(questions):
        lines.append(f'User: "{example_responses[-1]}"')
    
    lines.append('Agent: "Great! I\'ve learned about your situation. Now let me generate a personalized training plan for you..."')
    lines.append('[Agent calls tools: get_weather_forecast, search_nearby_venues, get_recommended_gear]')
    lines.append('Agent: {"metadata":{...},"training_plan":[...],"summary":{...}}')
    lines.append('[Note: Agent directly outputs JSON, no other text]')
    
    return "\n".join(lines)
