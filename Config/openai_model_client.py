from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.WARNING)

class FallbackClient:
    def __init__(self, clients):
        self._clients = clients
        self._current_client_index = 0

    @property
    def model_info(self):
        # Return the model info of the primary client
        return self._clients[0].model_info

    async def create(self, messages, **kwargs):
        for i, client in enumerate(self._clients):
            try:
                return await client.create(messages, **kwargs)
            except Exception as e:
                msg = f"Client {i} ({client.model_info.get('family', 'unknown')}) failed: {e}"
                print(f"Warning: {msg}")
                logging.warning(msg)
                if i == len(self._clients) - 1:
                    raise e

    async def create_stream(self, messages, **kwargs):
        for i, client in enumerate(self._clients):
            try:
                async for chunk in client.create_stream(messages, **kwargs):
                    yield chunk
                return
            except Exception as e:
                msg = f"Client {i} ({client.model_info.get('family', 'unknown')}) failed: {e}"
                print(f"Warning: {msg}")
                logging.warning(msg)
                if i == len(self._clients) - 1:
                    raise e


def get_model_client():
    clients = []



    # 3. OpenRouter Client
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY",'')
    if openrouter_api_key:
        openrouter_client = OpenAIChatCompletionClient(
            model="tngtech/deepseek-r1t2-chimera:free",
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            model_info={
                "vision": True,
                "function_calling": True,
                "json_output": True,
                "family": "unknown",
                "structured_output": True,
            }
        )
        clients.append(openrouter_client)

    return FallbackClient(clients)
