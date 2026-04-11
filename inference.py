import os
import json
from openai import OpenAI

from aqi_openenv_project import EcoGuardAction, EcoGuardEnv

# Pre-Submission Constraints strictly followed here

API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional — if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

def run_inference():
    print("[START] Initializing environment and OpenAI client...")
    
    # All LLM calls use the OpenAI client configured via these variables
    client = OpenAI(
        base_url=API_BASE_URL if API_BASE_URL != "<your-active-endpoint>" else None,
        api_key=HF_TOKEN or "dummy-key-if-not-set",
    )
    
    # Connect to the environment
    if LOCAL_IMAGE_NAME:
        env = EcoGuardEnv.from_docker_image(LOCAL_IMAGE_NAME)
    else:
        # Fallback to local server connection if no image specified
        env = EcoGuardEnv.from_env("http://localhost:8000")

    result = env.reset()
    obs = result.observation
    print(f"[START] Environment reset. Starting AQI: {obs.current_aqi}, Starting City Efficiency: {obs.city_operational_efficiency}")

    done = False
    step_count = 0
    max_steps = 10
    
    while not done and step_count < max_steps:
        step_count += 1
        
        prompt = f"""
        Current AQI is {obs.current_aqi:.2f}.
        City Efficiency is {obs.city_operational_efficiency:.2f}.
        Time of day: {obs.time_of_day}. Wind: {obs.wind_speed:.2f}. Temperature: {obs.temperature:.2f}.
        Action format: strictly JSON with an integer "set_factories_active" (0-10) and an integer "set_traffic_policy" (0-2: 0=High Traffic, 1=Moderate, 2=Strict/Low).
        The goal is to maximize efficiency while keeping the Air Quality Index (AQI) from rising too quickly. Minimize extreme actions if conditions are fine.
        """
        
        try:
            # LLM Call
            response = client.chat.completions.create(
                model=MODEL_NAME if MODEL_NAME != "<your-active-model>" else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are the EcoGuard environment controller AI. Respond in JSON only."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                action_data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if invalid JSON is passed
                action_data = {"set_factories_active": 7, "set_traffic_policy": 1}

            factories = min(10, max(0, int(action_data.get("set_factories_active", 7))))
            traffic = min(2, max(0, int(action_data.get("set_traffic_policy", 1))))
        except Exception as e:
            # Safe action if the API call fails or env vars aren't setup correctly
            factories = 5
            traffic = 1
            print(f"[STEP] Warning: OpenAI API call failed (error: {e}). Proceeding with safe fallback action.")

        # Execute step
        action = EcoGuardAction(set_factories_active=factories, set_traffic_policy=traffic)
        result = env.step(action)
        obs = result.observation
        done = result.done
        
        # Exact structured STEP log
        print(f"[STEP] Action selected: factories {factories}, traffic {traffic}. Resulting AQI: {obs.current_aqi:.2f}, Efficiency: {obs.city_operational_efficiency:.1f}%. Step Reward: {result.reward:.2f}")

    # Exact structured END log
    print(f"[END] Episode concluded. Total steps: {step_count}. Final AQI: {obs.current_aqi:.2f}")
    
    env.close()

if __name__ == "__main__":
    run_inference()
