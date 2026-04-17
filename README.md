# agent

## UX Architect Agent - Dual Provider Support (Groq + Ollama)

### Setup

1. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set Groq API Key:**
   ```bash
   export GROQ_API_KEY="your_key_here"
   # Or copy .env.example to .env and fill in your key
   ```

3. **Run Backend:**
   ```bash
   python3 main.py
   ```

4. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Providers

- **Groq** - Fast cloud AI (requires API key)
- **Ollama** - Local AI (requires `ollama run qwen2.5:14b`)
