import openai
from django.conf import settings
from typing import Dict, Any, Optional


class WeightLossPlanAI:
    """
    AI Agent for generating personalized weight loss plans using OpenAI API
    """
    
    def __init__(self):
        """Initialize the AI service with OpenAI API key and base URL"""
        self.client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    def generate_weight_loss_plan(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate a personalized weight loss plan based on user profile data
        
        Args:
            profile_data: Dictionary containing user profile information
            
        Returns:
            HTML formatted weight loss plan
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
                <p>Unable to generate weight loss plan at this time. Please check your local OpenAI server configuration.</p>
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
    
    def get_demo_plan(self) -> str:
        """
        Return a demo weight loss plan when API is not available
        """
        return """
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">🎯 Personalized Weight Loss Plan</h2>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                <h3 style="margin: 0;">📋 Your 4-Week Weight Loss Journey</h3>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">A comprehensive plan tailored to your profile and goals</p>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745;">
                    <h4 style="color: #28a745; margin-top: 0;">🥗 Nutrition Guidelines</h4>
                    <ul style="color: #495057;">
                        <li>Calorie deficit: 500-750 calories per day</li>
                        <li>Protein: 1.2-1.6g per kg body weight</li>
                        <li>Hydration: 8-10 glasses of water daily</li>
                        <li>Limit processed foods and added sugars</li>
                    </ul>
                </div>

                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #007bff;">
                    <h4 style="color: #007bff; margin-top: 0;">🏃‍♀️ Exercise Plan</h4>
                    <ul style="color: #495057;">
                        <li>Cardio: 150 minutes moderate intensity weekly</li>
                        <li>Strength training: 2-3 sessions per week</li>
                        <li>Daily walking: 10,000 steps minimum</li>
                        <li>Include flexibility and mobility work</li>
                    </ul>
                </div>
            </div>

            <div style="background: #fff3cd; padding: 20px; border-radius: 10px; border: 1px solid #ffeaa7; margin-bottom: 30px;">
                <h4 style="color: #856404; margin-top: 0;">⚠️ Important Disclaimer</h4>
                <p style="color: #856404; margin: 0;">This is a demo plan. For personalized recommendations, please configure your OpenAI API key and consult with healthcare professionals before starting any weight loss program.</p>
            </div>

            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #6c757d; font-style: italic;">Start your local OpenAI server at http://127.0.0.1:1234 to get personalized AI-generated plans!</p>
            </div>
        </div>
        """
