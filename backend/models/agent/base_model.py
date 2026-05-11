from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    BaseModel is an abstract base class that defines the interface for machine learning models used in the application.
    It declares an abstract method generate that must be implemented by any concrete subclass. The generate method is
    designed to take input prompt as a parameter, and return a string output
    representing the model's generated text. This class serves as a blueprint for implementing specific model classes that interact with different machine learning APIs or libraries, ensuring a consistent interface for generating output across the application.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate output using the specified model and input data.
        Args:
            prompt: The prompt to be used for generating the output.
        Returns:
            The generated output as a string.
        """
        pass
