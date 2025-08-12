import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LLM:
  """
  Wrapper class for interacting with the OpenAI API.

  Provides a simple interface for sending prompts to the selected model
  and retrieving generated responses.
  """

  def __init__(self):
    """
    Initialize the LLM client with default model and API key.
    """

    self.model = "gpt-4.1"
    self.client = OpenAI(api_key = OPENAI_API_KEY)
    self.prompt = None

  def get_response(self, prompt:str) -> str:
    """
    Send a prompt to the LLM and return its generated response.

    Parameters
    ----------
    prompt : str
        The text prompt to send to the LLM.

    Returns
    -------
    str
        The generated output text from the LLM.
    """

    self.prompt = prompt
    response = self.client.responses.create(
        model= self.model,
        input= self.prompt
    )

    return response.output_text