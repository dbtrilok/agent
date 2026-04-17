import re

with open("main.py", "r") as f:
    content = f.read()

# Chunk 1
content = re.sub(
    r"from pydantic import BaseModel, Field\n\n# Google Gemini\nimport google\.generativeai as genai\n\n# OpenAI\nfrom openai import OpenAI\n\n# Document processing\nimport fitz  # PyMuPDF\nfrom docx import Document as DocxDocument\n\n# Setup - Multiple AI Providers\nGEMINI_API_KEY = os\.getenv\(\"GEMINI_API_KEY\", \"\"\)\nOPENAI_API_KEY = os\.getenv\(\"OPENAI_API_KEY\", \"\"\)\nKIMI_API_KEY = os\.getenv\(\"KIMI_API_KEY\", \"sk-BQltRQt7oXjW3gv69BMhQX0oRIllH1ziZQnOfJdlUWjXbc9h\"\).*?\n\nUPLOAD_DIR = \"\./uploads\"\nos\.makedirs\(UPLOAD_DIR, exist_ok=True\)\n\n# Configure providers\nif GEMINI_API_KEY:\n    genai\.configure\(api_key=GEMINI_API_KEY\)\n\nopenai_client = None\nif OPENAI_API_KEY:\n    openai_client = OpenAI\(api_key=OPENAI_API_KEY\)",
    """from pydantic import BaseModel, Field

# OpenAI client (used for locally connecting to Ollama)
from openai import OpenAI

# Document processing
import fitz  # PyMuPDF
from docx import Document as DocxDocument

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)""",
    content,
    flags=re.DOTALL
)

# Chunk 2
content = content.replace(
    '    provider: str = "gemini"  # gemini, openai, kimi, ollama',
    '    provider: str = "ollama"  # Using local ollama exclusively'
)

# Chunk 3
old_agent_class = """class UXArchitectAgent:
    \"\"\"
    Senior Product Designer AI that converts product documents to Stitch prompts.
    Supports multiple AI providers: Gemini, OpenAI, Kimi.
    \"\"\"
    
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.model = None
        self.openai_client = None
        
        if provider == "gemini" and GEMINI_API_KEY:
            self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        elif provider == "openai" and OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        elif provider == "kimi" and KIMI_API_KEY:
            # Kimi/Moonshot uses OpenAI-compatible API
            self.openai_client = OpenAI(
                api_key=KIMI_API_KEY,
                base_url="https://api.moonshot.cn/v1"
            )
        elif provider == "ollama":
            # Ollama provides a local OpenAI-compatible API
            self.openai_client = OpenAI(
                api_key="ollama", # Key is required by client but ignored by Ollama
                base_url="http://localhost:11434/v1"
            )
        else:
            # Fallback to Gemini if no provider specified
            if GEMINI_API_KEY:
                self.model = genai.GenerativeModel('models/gemini-2.0-flash')
    
    async def generate_content(self, prompt: str) -> str:
        \"\"\"Generate content using the selected provider.\"\"\"
        if self.provider == "gemini" and self.model:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text
        elif (self.provider in ["openai", "kimi", "ollama"]) and self.openai_client:
            model_name = "gpt-4o-mini"
            if self.provider == "kimi":
                model_name = "moonshot-v1-8k"
            elif self.provider == "ollama":
                model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
                
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            raise ValueError(f"Provider {self.provider} not configured or available")"""

new_agent_class = """class UXArchitectAgent:
    \"\"\"
    Senior Product Designer AI that converts product documents to Stitch prompts.
    Supports local open-source models via Ollama.
    \"\"\"
    
    def __init__(self, provider: str = "ollama"):
        self.provider = "ollama"
        # Ollama provides a local OpenAI-compatible API
        self.openai_client = OpenAI(
            api_key="ollama", # Key is required by client but ignored by Ollama
            base_url="http://localhost:11434/v1"
        )
    
    async def generate_content(self, prompt: str) -> str:
        \"\"\"Generate content using the local Ollama provider.\"\"\"
        model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            
        response = await asyncio.to_thread(
            self.openai_client.chat.completions.create,
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content"""

content = content.replace(old_agent_class, new_agent_class)

# Chunk 4
content = content.replace(
    '    provider: str = "gemini"',
    '    provider: str = "ollama"'
)

# Chunk 5
old_providers = """@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "gemini_configured": bool(GEMINI_API_KEY)}


@app.get("/api/providers")
async def get_providers():
    \"\"\"Get available AI providers and their configuration status.\"\"\"
    return {
        "providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "configured": bool(GEMINI_API_KEY),
                "description": "Google's Gemini AI models"
            },
            {
                "id": "openai",
                "name": "OpenAI (ChatGPT)",
                "configured": bool(OPENAI_API_KEY),
                "description": "OpenAI GPT models"
            },
            {
                "id": "kimi",
                "name": "Kimi (Moonshot AI)",
                "configured": bool(KIMI_API_KEY),
                "description": "Moonshot AI's Kimi models"
            },
            {
                "id": "ollama",
                "name": "Local (Ollama)",
                "configured": True,  # Ollama doesn't need an API key
                "description": "Local Open-Source AI Models"
            }
        ]
    }"""

new_providers = """@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/providers")
async def get_providers():
    \"\"\"Get available AI providers and their configuration status.\"\"\"
    return {
        "providers": [
            {
                "id": "ollama",
                "name": "Local (Ollama)",
                "configured": True,
                "description": "Local Open-Source AI Models"
            }
        ]
    }"""

content = content.replace(old_providers, new_providers)

with open("main.py", "w") as f:
    f.write(content)

