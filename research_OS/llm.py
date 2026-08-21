import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel
from config import settings
from openai import OpenAI


T = TypeVar('T', bound=BaseModel)

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
            timeout=settings.REQUEST_TIMEOUT,
        )
        self.default_model =settings.DEFAULT_MODEL
        self.fast_model = settings.FAST_MODEL


    def generate_text(self, system_prompt:str,
                      user_prompt:str,
                      use_fast_model:bool=False,
                      temperature: float = 0.2):

        """Standard text generator worker"""

        model = self.fast_model if use_fast_model else self.default_model

        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {
                    "role":"system",
                    "content":system_prompt
                },
                {
                    "role":"user",
                    "content":user_prompt
                }
            ]


        )
        return response.choices[0].message.content or ""

    def generate_structured(
            self,
            system_prompt:str,
            user_prompt:str,
            response_model:Type[T],
            use_fast_model:bool=False) -> T:
        """Force the generated text to structured output"""

        model = self.fast_model if use_fast_model else self.default_model
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)

        stucture_system_prompt = (
            f"{system_prompt}\n\n"
            f"CRITICAL: You must return ONLY a raw, valid JSON object that matches "
            f"this exact JSON Schema:\n{schema_json}\n"
            f"Do not include any markdown formatting like ```json or explanation."
        )

        response = self.client.chat.completions.create(
            model=model,
            temperature=0.0,
            response_format={"type":"json_object"},
            messages=[
                {
                    "role":"system","content":stucture_system_prompt,
                },
                {
                    "role":"user","content":user_prompt
                }
            ]
        )

        raw_content = response.choices[0].message.content or "{}"

        clean_content = re.sub(r"^```json\s*|\s*```$", "", raw_content.strip())

        return response_model.model_validate_json(clean_content)

llm_client = LLMClient()

if __name__ == "__main__":
    print("Testing live NVIDIA  NTM connection:")
    test_response = llm_client.generate_text(
        system_prompt="You are a helpful technical assistant.",
        user_prompt="Explain what a multi-agent system is in one sentence.",
        use_fast_model=True,
    )
    print("\n✅ Live Test Response:")
    print(test_response)
