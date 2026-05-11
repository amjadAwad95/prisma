from groq import Groq
from dotenv import load_dotenv

from .base_model import BaseModel

load_dotenv()


class GroqModel(BaseModel):
    """
    GroqModel is a concrete implementation of the BaseModel abstract class that uses the Groq API
    to perform predictions. It initializes a Groq client and implements the generate method to
    interact with the Groq API, sending input data and configuration parameters to receive generated output.
    The generate method constructs a request to the Groq API, specifying the model to use, the input
    data, and various configuration options such as max_completion_tokens, top_p, reasoning_effort,
    and stop conditions. The response from the API is processed to extract and return the generated
    output as a string.
    """

    def __init__(self, model_name: str = "openai/gpt-oss-120b", config: dict = {}):
        """
        Initialize the GroqModel instance by creating a Groq client.
        The Groq client will be used to interact with the Groq API for generating output.
        The API key for authentication is expected to be set in the environment variables.
        """
        self.client = Groq()
        self.model_name = model_name
        self.config = config
        print("GroqModel initialized with Groq client.")

    def generate(
        self,
        prompt: str = "",
    ) -> str:
        """
        Generate output for the given input data using the specified model.
        Args:
            prompt: The prompt to be used for generating the output.
            config: A dictionary of configuration options for the generation, such as
                    max_completion_tokens, top_p, reasoning_effort, stop, and any
                    additional parameters supported by the Groq API.
        Returns:
            The generated output from the model as a string.
        Raises:
            RuntimeError: If the generation fails due to an API error or invalid configuration.
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=self.config.get("max_completion_tokens", 1000),
            top_p=self.config.get("top_p", 1),
            reasoning_effort=self.config.get("reasoning_effort", "medium"),
            stop=self.config.get("stop"),
        )
        return response.choices[0].message.content.strip()
