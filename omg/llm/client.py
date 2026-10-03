from openai import OpenAI
import json
import logging

class LLMClient:
    def __init__(self, base_url="http://localhost:1234/v1", api_key="lm-studio"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def ask(self, model="qwen2-vl-7b-instruct", messages=[], temperature=0.2, json_mode=True):
        """Sends messages to the vision model and returns the parsed response."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            
            if not json_mode:
                return {"text": content}

            # Robust JSON extraction
            try:
                # Find the first occurrences of { and the last occurrence of }
                start = content.find('{')
                end = content.rfind('}')
                if start != -1 and end != -1:
                    json_str = content[start:end+1]
                    return json.loads(json_str)
                return json.loads(content)
            except Exception as json_err:
                with open("debug_refusal.txt", "w", encoding="utf-8") as f:
                    f.write(content)
                logging.error(f"JSON Parsing Error: {json_err} | Raw response saved to debug_refusal.txt")
                return {"error": "Invalid JSON format from model", "raw": content}
        except Exception as e:
            logging.error(f"LLM API Error: {e}")
            return {"error": str(e)}

    def ask_stream(self, model="qwen2-vl-7b-instruct", messages=[], temperature=0.2):
        """Sends messages to the vision model and yields the streamed text response."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logging.error(f"LLM Stream API Error: {e}")
            yield f"Error: {str(e)}"

    def get_active_model(self):
        """Fetches the first available model name from the server."""
        try:
            models = self.client.models.list()
            if models.data:
                return models.data[0].id
            return None
        except:
            return None

    def test_connection(self):
        """Verifies if the model is reachable."""
        try:
            models = self.client.models.list()
            return True, models
        except Exception as e:
            return False, str(e)
