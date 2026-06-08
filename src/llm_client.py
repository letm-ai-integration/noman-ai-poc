"""LLM client for text generation without frameworks"""

from typing import Dict, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.config import MODEL_NAME, DEVICE, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from src.token_visualizer import TokenVisualizer


class LLMClient:
    """Simple LLM client using Hugging Face transformers"""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.device = DEVICE
        
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
        # Add pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.token_visualizer = TokenVisualizer(model_name)
        print(f"Model loaded successfully!\n")

    def generate(
        self,
        prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = 0.9,
        visualize_tokens: bool = True,
    ) -> Dict:
        """
        Generate text response
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.1-2.0)
            top_p: Nucleus sampling parameter
            visualize_tokens: Whether to visualize tokens
            
        Returns:
            Dictionary with response and metadata
        """
        if visualize_tokens:
            print("\nPrompt Token Analysis:")
            self.token_visualizer.print_tokens(prompt)

        # Encode prompt
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        # Generate
        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                attention_mask=torch.ones_like(input_ids),
            )

        # Decode
        generated_text = self.tokenizer.decode(
            output_ids[0], skip_special_tokens=True
        )
        
        # Extract only the new tokens (remove prompt)
        prompt_length = len(input_ids[0])
        new_tokens = output_ids[0][prompt_length:]
        generated_response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        result = {
            "prompt": prompt,
            "response": generated_response,
            "full_output": generated_text,
            "prompt_token_count": len(input_ids[0]),
            "response_token_count": len(new_tokens),
            "total_token_count": len(output_ids[0]),
            "parameters": {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            },
        }

        return result

    def batch_generate(
        self,
        prompts: list,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = 0.9,
    ) -> list:
        """Generate responses for multiple prompts"""
        results = []
        for prompt in prompts:
            result = self.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                visualize_tokens=False,
            )
            results.append(result)
        return results

    def print_response(self, result: Dict):
        """Pretty print generation result"""
        print("\n" + "=" * 80)
        print("GENERATION RESULT")
        print("=" * 80)
        print(f"\nPrompt:\n{result['prompt']}")
        print(f"\n{'-' * 80}")
        print(f"Response:\n{result['response']}")
        print(f"\n{'-' * 80}")
        print(f"Generation Parameters:")
        print(f"  Temperature: {result['parameters']['temperature']}")
        print(f"  Max Tokens: {result['parameters']['max_tokens']}")
        print(f"  Top P: {result['parameters']['top_p']}")
        print(f"\nToken Usage:")
        print(f"  Prompt Tokens: {result['prompt_token_count']}")
        print(f"  Response Tokens: {result['response_token_count']}")
        print(f"  Total Tokens: {result['total_token_count']}")
        print("=" * 80 + "\n")

    def compare_temperatures(
        self,
        prompt: str,
        temperatures: list = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> list:
        """
        Compare responses with different temperature values
        
        Args:
            prompt: Input prompt
            temperatures: List of temperatures to try (default: [0.3, 0.7, 1.2])
            max_tokens: Maximum tokens
            
        Returns:
            List of results
        """
        if temperatures is None:
            temperatures = [0.3, 0.7, 1.2]

        print("\n" + "=" * 80)
        print(f"TEMPERATURE COMPARISON - {len(temperatures)} variations")
        print("=" * 80)

        results = []
        for temp in temperatures:
            result = self.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temp,
                visualize_tokens=False,
            )
            results.append(result)
            
            print(f"\n[Temperature: {temp}]")
            print(f"Response: {result['response']}")

        print("\n" + "=" * 80)
        return results

    def compare_max_tokens(
        self,
        prompt: str,
        token_limits: list = None,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> list:
        """
        Compare responses with different max_token values
        
        Args:
            prompt: Input prompt
            token_limits: List of max token values (default: [30, 60, 100])
            temperature: Temperature value
            
        Returns:
            List of results
        """
        if token_limits is None:
            token_limits = [30, 60, 100]

        print("\n" + "=" * 80)
        print(f"MAX TOKENS COMPARISON - {len(token_limits)} variations")
        print("=" * 80)

        results = []
        for max_tok in token_limits:
            result = self.generate(
                prompt,
                max_tokens=max_tok,
                temperature=temperature,
                visualize_tokens=False,
            )
            results.append(result)
            
            print(f"\n[Max Tokens: {max_tok}]")
            print(f"Response: {result['response']}")
            print(f"Actual Tokens Used: {result['response_token_count']}")

        print("\n" + "=" * 80)
        return results
