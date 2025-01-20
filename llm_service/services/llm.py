import openai
from django.conf import settings
import os
from dotenv import load_dotenv
import logging
import traceback  # Add this import

logger = logging.getLogger('llm_service')

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not configured")
        self.client = openai.OpenAI(api_key=self.api_key)  # Create client instance
        logger.info("LLMService initialized successfully")

    def generate_code(self, prompt):
        try:
            logger.debug(f"Generating code for prompt: {prompt[:50]}...")
            
            logger.debug("Making API call to OpenAI")
            response = self.client.chat.completions.create(  # Updated API call
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a web developer. Generate HTML, CSS, and JavaScript code based on the prompt. Always wrap your code in appropriate markdown code blocks like ```html, ```css, and ```javascript."},
                    {"role": "user", "content": prompt}
                ]
            )
            logger.debug("Received response from OpenAI")
            
            content = response.choices[0].message.content  # Updated response access
            logger.debug(f"Generated content length: {len(content)}")
            return content

        except Exception as e:
            logger.error(f"Error in generate_code: {str(e)}")
            logger.error(f"Full error details: {traceback.format_exc()}")
            raise Exception(f"LLM Error: {str(e)}")