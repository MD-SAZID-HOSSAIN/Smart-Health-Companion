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
            error_message = str(e)
            if "401" in error_message or "User not found" in error_message:
                return f"""
                <div style="padding: 20px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; color: #856404;">
                    <h3>⚠️ API Configuration Issue</h3>
                    <p><strong>OpenRouter API Key Issue:</strong> The API key is invalid or expired.</p>
                    <p><strong>To fix this:</strong></p>
                    <ol>
                        <li>Go to <a href="https://openrouter.ai/" target="_blank">OpenRouter.ai</a></li>
                        <li>Sign up or log in to your account</li>
                        <li>Generate a new API key</li>
                        <li>Update the OPENAI_API_KEY in your settings.py file</li>
                    </ol>
                    <p><strong>Current Configuration:</strong></p>
                    <ul>
                        <li>Server URL: {settings.OPENAI_BASE_URL}</li>
                        <li>Model: {settings.OPENAI_MODEL}</li>
                        <li>Error: {error_message}</li>
                    </ul>
                    <p><em>Alternatively, you can set the OPENAI_API_KEY environment variable with your valid API key.</em></p>
                </div>
                """
            else:
                return f"""
                <div style="padding: 20px; background-color: #fee; border: 1px solid #fcc; border-radius: 8px; color: #c33;">
                    <h3>Error Generating Plan</h3>
                    <p>Unable to generate plan at this time. Please check your OpenAI configuration.</p>
                    <p><strong>Server URL:</strong> {settings.OPENAI_BASE_URL}</p>
                    <p><strong>Model:</strong> {settings.OPENAI_MODEL}</p>
                    <p><strong>Error:</strong> {error_message}</p>
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
        current_weight = profile_data.get('current_weight', 'Not specified')
        target_weight = profile_data.get('target_weight', 'Not specified')
        gender = profile_data.get('gender', 'Not specified')
        goal = profile_data.get('goal', 'Not specified')
        exercise_place = profile_data.get('exercise_place', 'Not specified')
        activity_level = profile_data.get('activity_level', 'Not specified')
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

        # Format exercise place display
        exercise_place_display = {
            'gym': 'Gym',
            'home': 'Home',
            'outdoor': 'Outdoor'
        }.get(exercise_place, exercise_place)

        # Format activity level display
        activity_level_display = {
            'sedentary': 'Sedentary – little or no exercise',
            'lightly_active': 'Lightly Active – light exercise 1–3 days/week',
            'moderately_active': 'Moderately Active – moderate exercise 3–5 days/week',
            'very_active': 'Very Active – hard exercise 6–7 days/week',
            'extra_active': 'Extra Active – intense training or physical job'
        }.get(activity_level, activity_level)

        # Optional daily log context
        daily_log: Optional[Dict[str, Any]] = profile_data.get('daily_log')
        log_text = ""
        if daily_log:
            # Build a concise deviation-aware snippet
            calories_str = f"{daily_log.get('calories')} kcal"
            rec_cal = daily_log.get('recommended_calories')
            if rec_cal is not None:
                calories_str += f" (recommended: {rec_cal} kcal)"

            sleep_str = f"{daily_log.get('sleep_hours')} hours"
            rec_sleep = daily_log.get('recommended_sleep')
            if rec_sleep is not None:
                sleep_str += f" (recommended: {rec_sleep} hours)"

            exercise_str = f"{daily_log.get('exercise_minutes')} minutes"

            log_text = f"""
            \nRecent daily log (date: {daily_log.get('date', 'latest')}):
            - Calories consumed: {calories_str}
            - Sleep: {sleep_str}
            - Exercise: {exercise_str}

            If there is a deviation from recommended values, adjust the plan for the next 1–2 weeks to gently guide the user back on track, keeping safety and sustainability as top priorities. Provide concrete, actionable adjustments to meals, portions, and training volume/intensity.
            """

        prompt = f"""
        Create a comprehensive, personalized weight loss plan for the following user profile:

        **Personal Information:**
        - Age: {age} years
        - Height: {height} cm
        - Current Weight: {current_weight} kg
        - Target Weight: {target_weight if target_weight != 'Not specified' else 'Not specified'} kg
        - Gender: {gender_display}
        - BMI: {bmi if bmi != 'Not calculated' else 'Not calculated'}

        **Health Goals:**
        - Primary Goal: {goal_display}

        **Exercise Preferences:**
        - Exercise Place: {exercise_place_display}
        - Activity Level: {activity_level_display}

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

        {log_text}
        """

        return prompt

