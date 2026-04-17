"""
Dual Provider Agent - Supports both Groq API (fast cloud) and Ollama (slow local).
"""
import os
import asyncio
import aiohttp
from typing import Optional
from openai import OpenAI

# Groq API Key - Set via environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


class DualProviderAgent:
    """
    Agent that supports both Groq (fast cloud) and Ollama (local) providers.
    
    Provider options:
    - "groq": Fast cloud inference via Groq API (2-5 seconds)
    - "ollama": Local inference via Ollama (10-30 seconds, private)
    """
    
    def __init__(self, provider: str = "ollama"):
        self.provider = provider.lower()
        
        if self.provider == "groq":
            # Groq uses OpenAI-compatible client
            self.openai_client = OpenAI(
                api_key=GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.1-8b-instant"
        elif self.provider == "ollama":
            # Ollama local server
            self.openai_client = OpenAI(
                api_key="ollama",  # Key is required by client but ignored by Ollama
                base_url="http://localhost:11434/v1"
            )
            self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:14b")
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'groq' or 'ollama'.")
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using the selected provider.
        
        Args:
            prompt: The prompt to send to the AI
            
        Returns:
            The generated text response
        """
        if self.provider == "groq":
            return await self._generate_groq(prompt)
        else:
            return await self._generate_ollama(prompt)
    
    async def _generate_groq(self, prompt: str) -> str:
        """Generate content using Groq API (fast cloud)."""
        try:
            print(f"[GROQ] Sending request to model: {self.model}")
            print(f"[GROQ] Prompt length: {len(prompt)} chars")
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that always returns valid JSON responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4096
            )
            
            print(f"[GROQ] Response received, choices: {len(response.choices)}")
            
            if not response.choices:
                raise ValueError("Groq returned no choices in response")
            
            content = response.choices[0].message.content
            print(f"[GROQ] Content length: {len(content) if content else 0} chars")
            print(f"[GROQ] Content preview: {content[:200] if content else 'EMPTY'}")
            
            if not content:
                raise ValueError("Groq returned empty content")
            return content
        except Exception as e:
            print(f"[GROQ ERROR] {type(e).__name__}: {str(e)}")
            raise Exception(f"Groq API error: {str(e)}")
    
    async def _generate_ollama(self, prompt: str) -> str:
        """Generate content using local Ollama server."""
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    async def check_ollama_status(self) -> dict:
        """Check if Ollama is running and which models are available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/tags", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m.get("name", "unknown") for m in data.get("models", [])]
                        return {
                            "running": True,
                            "models": models,
                            "message": f"Ollama is running with {len(models)} models"
                        }
                    else:
                        return {
                            "running": False,
                            "models": [],
                            "message": f"Ollama returned status {resp.status}"
                        }
        except Exception as e:
            return {
                "running": False,
                "models": [],
                "message": f"Ollama not accessible: {str(e)}"
            }
    
    async def check_groq_status(self) -> dict:
        """Check if Groq API is accessible."""
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            return {
                "accessible": True,
                "message": "Groq API is accessible and responding"
            }
        except Exception as e:
            return {
                "accessible": False,
                "message": f"Groq API error: {str(e)}"
            }
    
    async def check_provider_status(self) -> dict:
        """Check the status of the current provider."""
        if self.provider == "groq":
            return await self.check_groq_status()
        else:
            return await self.check_ollama_status()
