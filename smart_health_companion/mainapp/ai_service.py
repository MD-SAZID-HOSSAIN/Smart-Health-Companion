import openai
from django.conf import settings
from typing import Dict, Any, Optional


class AIPlan:
    """
    AI Agent for generating personalized weight loss plans using OpenAI API
    """
    
    def __init__(self):
        """Initialize the AI service with OpenAI API key and base URL"""
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def generate_plan(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate a personalized plan based on user profile data and target goal
        
        Args:
            profile_data: Dictionary containing user profile information
            
        Returns:
            HTML formatted plan
        """
        try:
            # Prepare the prompt with user data
            prompt = self._create_prompt(profile_data)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional nutritionist and fitness expert. Create detailed, personalized weight loss plans based on user data. Always format your response as HTML with proper styling for better presentation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=16000,
                temperature=0.7
            )

            # print(f"OpenAI Response: {response}")
            
            return response.choices[0].message.content.replace("```html", "").replace("```", "")
            
        except Exception as e:
            return f"""
            <div style="padding: 20px; background-color: #fee; border: 1px solid #fcc; border-radius: 8px; color: #c33;">
                <h3>Error Generating Plan</h3>
                <p>Unable to generate plan at this time. Please check your local OpenAI server configuration.</p>
                <p><strong>Server URL:</strong> {settings.OPENAI_BASE_URL}</p>
                <p><strong>Model:</strong> {settings.OPENAI_MODEL}</p>
                <p><strong>Error:</strong> {str(e)}</p>
                <p><em>Make sure your local OpenAI server is running at {settings.OPENAI_BASE_URL}</em></p>
            </div>
            """
    
    def _create_prompt(self, profile_data: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for the AI based on user profile data
        
        Args:
            profile_data: User profile information
            
        Returns:
            Formatted prompt string
        """
        # Extract profile information
        age = profile_data.get('age', 'Not specified')
        height = profile_data.get('height', 'Not specified')
        weight = profile_data.get('weight', 'Not specified')
        gender = profile_data.get('gender', 'Not specified')
        goal = profile_data.get('goal', 'Not specified')
        food_allergies = profile_data.get('food_allergies', 'None')
        health_problems = profile_data.get('health_problems', [])
        other_health_problems = profile_data.get('other_health_problems', 'None')
        bmi = profile_data.get('bmi', 'Not calculated')
        
        # Format gender display
        gender_display = {
            'M': 'Male',
            'F': 'Female', 
            'O': 'Other'
        }.get(gender, gender)
        
        # Format goal display
        goal_display = {
            'lose_weight': 'Lose Weight',
            'maintain_weight': 'Maintain Weight',
            'build_muscle': 'Gain Muscle',
            'both': 'Gain Muscle & Lose Fat',
            'improve_fitness': 'Improve Fitness'
        }.get(goal, goal)
        
        prompt = f"""
        Create a comprehensive, personalized weight loss plan for the following user profile:

        **Personal Information:**
        - Age: {age} years
        - Height: {height} cm
        - Weight: {weight} kg
        - Gender: {gender_display}
        - BMI: {bmi if bmi != 'Not calculated' else 'Not calculated'}

        **Health Goals:**
        - Primary Goal: {goal_display}

        **Health Considerations:**
        - Food Allergies: {food_allergies}
        - Health Problems: {', '.join(health_problems) if health_problems else 'None'}
        - Other Health Issues: {other_health_problems}

        **Requirements:**
        1. Create a detailed 3 to 4 month weight loss plan
        2. Include specific meal recommendations (breakfast, lunch, dinner, snacks)
        3. Provide exercise plan for 3 or 4 days a week suitable for their profile
        4. Include hydration and sleep guidelines
        5. Add progress tracking suggestions
        6. Consider their food allergies and health conditions
        7. Make it realistic and sustainable
        8. Format everything as HTML with proper styling, headings, and structure
        9. Use a professional, encouraging tone
        10. No need for an Introduction.

        Please format the response as HTML with CSS styling for better presentation. Use appropriate headings, lists, and styling to make it visually appealing and easy to read.
        Make sure all the styles are inline, so that they don't interfere with the styling of the page this will be embedded in.
        NOTE: ALL STYLES SHOULD BE INLINE.
        """
        
        return prompt
    
