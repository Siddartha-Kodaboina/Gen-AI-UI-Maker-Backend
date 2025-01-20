import os
import re
import logging

logger = logging.getLogger('llm_service')

class FileGenerator:
    def __init__(self):
        self.base_dir = 'generated_files'
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"FileGenerator initialized with base_dir: {self.base_dir}")

    def parse_llm_response(self, response):
        logger.debug("Starting to parse LLM response")
        
        # Extract HTML, CSS, and JS content using regex
        html_pattern = r"```html\n(.*?)\n```"
        css_pattern = r"```css\n(.*?)\n```"
        js_pattern = r"```javascript\n(.*?)\n```"

        files = {
            'index.html': self._extract_content(response, html_pattern),
            'style.css': self._extract_content(response, css_pattern),
            'script.js': self._extract_content(response, js_pattern)
        }

        # Log what was found
        for file_name, content in files.items():
            if content:
                logger.debug(f"Found content for {file_name}: {len(content)} characters")
            else:
                logger.warning(f"No content found for {file_name}")

        return files

    def _extract_content(self, text, pattern):
        try:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1)
                logger.debug(f"Successfully extracted content with pattern {pattern[:20]}...")
                return content
            logger.warning(f"No match found for pattern {pattern[:20]}...")
            return ""
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}")
            return ""

    def save_files(self, files):
        logger.info("Starting to save files")
        saved_files = []
        
        for filename, content in files.items():
            if content:
                try:
                    filepath = os.path.join(self.base_dir, filename)
                    logger.debug(f"Saving file: {filepath}")
                    
                    with open(filepath, 'w') as f:
                        f.write(content)
                    
                    saved_files.append(filename)
                    logger.info(f"Successfully saved {filename}")
                except Exception as e:
                    logger.error(f"Error saving {filename}: {str(e)}")
            else:
                logger.warning(f"Skipping {filename} - no content")
        
        return saved_files