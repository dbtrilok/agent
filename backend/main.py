"""
UX Architect Agent - FastAPI Backend (Simplified)
Implements the Senior Product Designer AI with strict wait gate behavior.
"""
import os
import uuid
import json
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict

# OpenAI client (used for locally connecting to Ollama)
from openai import OpenAI

# Document processing
import fitz  # PyMuPDF
from docx import Document as DocxDocument

# Dual Provider Agent (Groq + Ollama)
from local_agent import DualProviderAgent

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ============================================================================
# DATA MODELS
# ============================================================================

class ProjectManifest(BaseModel):
    """Tracks what the agent has extracted vs what's missing for pure design platforms."""
    model_config = ConfigDict(validate_assignment=True, extra="allow")
    
    app_name: Optional[str] = None
    app_type: Optional[str] = None  
    target_audience: Optional[str] = None
    platform: Optional[str] = None  
    
    # Design Direction
    primary_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    ui_style: Optional[str] = None  
    inspiration_apps: Optional[List[str]] = None
    brand_assets: Optional[str] = None
    
    # UI/UX Specifications
    rtl_support: Optional[str] = None
    design_system: Optional[str] = None
    visual_content: Optional[str] = None
    
    # UX Strategy
    navigation_pattern: Optional[str] = None  
    primary_user_goal: Optional[str] = None  
    
    # Business
    conversion_focus: Optional[bool] = None
    special_logic: Optional[List[str]] = None  
    
    # Extracted from docs
    features: List[str] = Field(default_factory=list)
    screen_inventory: List[str] = Field(default_factory=list)
    user_flows: List[str] = Field(default_factory=list)
    data_structures: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Status tracking
    @property
    def is_complete(self) -> bool:
        required = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.primary_user_goal, self.rtl_support, self.design_system
        ]
        return all(field is not None for field in required)
    
    @property
    def completion_percentage(self) -> int:
        fields = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal,
            self.rtl_support, self.design_system, self.visual_content,
            self.inspiration_apps, self.conversion_focus, self.brand_assets
        ]
        filled = sum(1 for f in fields if f is not None)
        return int((filled / len(fields)) * 100)


class AgentState(BaseModel):
    """Immutable state object for the UX Architect Agent."""
    session_id: str
    status: str = "idle"  # idle, analyzing, waiting, generating, complete
    raw_documents: List[Dict[str, Any]] = Field(default_factory=list)
    manifest: ProjectManifest = Field(default_factory=ProjectManifest)
    missing_questions: List[Dict[str, Any]] = Field(default_factory=list)
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    final_stitch_prompt: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    provider: str = "ollama"  # Using local ollama exclusively
    analysis: Optional[Dict[str, Any]] = None
    pending_questions: List[Dict[str, Any]] = Field(default_factory=list)


class Question(BaseModel):
    id: str
    question: str
    type: str  # text, select, color, boolean
    options: Optional[List[str]] = None
    required: bool
    context: Optional[str] = None


# ============================================================================
# AGENT LOGIC (Simplified without LangGraph)
# ============================================================================

class UXArchitectAgent:
    """
    Senior Product Designer AI that converts product documents to Stitch prompts.
    Supports both Groq (fast cloud) and Ollama (local) providers.
    """
    
    def __init__(self, provider: str = "ollama"):
        self.provider = provider.lower()
        self.agent = DualProviderAgent(provider=self.provider)
    
    async def generate_content(self, prompt: str) -> str:
        """Generate content using the selected provider (Groq or Ollama)."""
        return await self.agent.generate_content(prompt)
    
    async def analyze_documents(self, state: AgentState) -> AgentState:
        """Step 1: Deep analysis using the user's proven manual prompt structure."""
        state.status = "analyzing"
        
        # Combine all document text
        all_text = []
        for doc in state.raw_documents:
            if "extracted_text" in doc:
                all_text.append(doc["extracted_text"])
        
        combined_text = "\n\n---\n\n".join(all_text)
        
        if not combined_text.strip():
            state.chat_history.append({
                "role": "assistant",
                "content": "I've received your request, but no document text was extracted. Please upload a PDF, DOCX, or paste your product requirements directly in the chat."
            })
            return state
        
        # Use the user's proven system prompt for analysis
        system_prompt = """You are a Senior Product Designer and AI Figma/Stitch Prompt Engineer.

Your task is to intelligently convert provided product documents into a PERFECT high-fidelity blueprint prompt for an AI GUI Generator (like Stitch or Figma Make).

ZERO-HALLUCINATION RULE (STRICTLY FOLLOW):
You are strictly forbidden from guessing or inventing ANY missing details. If the app name, Target Audience, RTL Support, Design System style, or Brand Colors are not explicitly clear in the provided documents, YOU MUST NOT IMAGINE THEM. Instead, YOU MUST ask the user.

DO NOT ASK ANY QUESTIONS ABOUT CODE, TECH STACKS, COMPONENT LIBRARIES, OR FRAMEWORKS. Focus PURELY on the UI Design, Screen Inventory, and aesthetics.

CORE BEHAVIOR:
1. Analyze the input documents.
2. Extract all relevant UI/UX details.
3. Identify missing UI platform generation requirements.
4. Ask precise questions to collect the missing requirements.

GOAL: Build an unbreakable blueprint architecture prompt that platforms can map perfectly into visual screens."""

        analysis_prompt = f"""
{system_prompt}

YOUR EXACT TASK:
1. Review the input text.
2. Extract features, user_flows, and the SCREEN INVENTORY.
3. Determine what DESIGN elements are missing based on the exact fields below.

DOCUMENTS:
{combined_text[:8000]}

MISSING REQUIREMENT CATEGORIES YOU MUST CHECK FOR AND ASK ABOUT:
- Design Direction (Color System/Branding, UI Style, Logo/Brand Assets) -> fields: 'primary_color', 'ui_style', 'brand_assets'
- UX Strategy (Primary UX Goal, RTL (Arabic) Layout Support) -> fields: 'primary_user_goal', 'rtl_support'
- Component Preferences (Design System Approach) -> field: 'design_system'
- Visual Content (Product Imagery style) -> field: 'visual_content'

OUTPUT JSON FORMAT EXACTLY (Do not output markdown, only raw parsable JSON):
{{
    "extracted_data": {{
        "app_name": "string or null",
        "app_type": "string or null",
        "target_audience": "string or null",
        "platform": "string or null",
        "primary_color": "string or null",
        "ui_style": "string or null",
        "primary_user_goal": "string or null",
        "rtl_support": "string or null",
        "design_system": "string or null",
        "visual_content": "string or null",
        "brand_assets": "string or null",
        "features": ["list", "of", "features"],
        "screen_inventory": ["list", "of", "screens", "to", "build"],
        "user_flows": ["list", "of", "flows"]
    }},
    "questions_to_ask": [
        {{
            "field": "rtl_support",
            "type": "select",
            "options": ["Next.js (App Router)", "React (Vite)", "Vanilla HTML/JS"],
            "required": true,
            "question": "What tech stack should the UI generator use?",
            "context": "AI platforms need to know the framework."
        }},
        {{
            "field": "component_library",
            "type": "select",
            "options": ["Tailwind + shadcn/ui", "Material UI", "Tailwind + Headless UI"],
            "required": true,
            "question": "Which component library do you prefer?",
            "context": "Dictates how buttons and modals are styled."
        }},
        {{
            "field": "icon_set",
            "type": "select",
            "options": ["lucide-react", "heroicons", "radix-icons"],
            "required": true,
            "question": "What icon set should the AI import from?",
            "context": "Prevents broken SVG hallucination."
        }},
        {{
            "field": "app_name",
            "type": "text",
            "required": true,
            "question": "What is the App Name?"
        }},
        {{
            "field": "primary_color",
            "type": "color",
            "required": true,
            "question": "What is the primary brand color?"
        }}
    ]
}}

If an item is explicitly written in the document, DO NOT add a question for it.
"""
        
        try:
            result_text = await self.generate_content(analysis_prompt)
            
            # Check for empty response
            if not result_text or not result_text.strip():
                raise ValueError("AI returned empty response")
            
            # Parse JSON from response (handle markdown code blocks)
            result_text = result_text.strip()
            
            # Remove markdown code block if present
            if result_text.startswith("```"):
                result_text = result_text.split("```", 2)[-1]  # Get content after last ```
                if result_text.startswith("json"):
                    result_text = result_text[4:]  # Remove "json" language tag
                result_text = result_text.strip()
            
            if "{" in result_text and "}" in result_text:
                json_start = result_text.index("{")
                json_end = result_text.rindex("}") + 1
                json_str = result_text[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(result_text)
            
            # Store analysis in state
            state.analysis = analysis
            
            # Extract into manifest
            if "features" in analysis:
                state.manifest.features = analysis["features"]
            if "user_flows" in analysis:
                state.manifest.user_flows = analysis["user_flows"]
            if "app_type" in analysis:
                state.manifest.app_type = analysis["app_type"]
            
            # Store questions for next step
            state.pending_questions = analysis.get("questions_to_ask", [])
            
            # Provide feedback
            num_questions = len(state.pending_questions)
            if num_questions > 0:
                state.chat_history.append({
                    "role": "assistant",
                    "content": f"📄 I've analyzed your documents. This appears to be a **{analysis.get('app_type', 'Unknown')}** app with {len(analysis.get('features', []))} features.\n\n🔍 I've identified **{num_questions} critical details** that need clarification to generate the perfect Stitch prompt. Please answer these questions in the sidebar."
                })
            else:
                state.chat_history.append({
                    "role": "assistant",
                    "content": f"📄 I've analyzed your documents. This appears to be a **{analysis.get('app_type', 'Unknown')}** app with {len(analysis.get('features', []))} features.\n\n✅ All critical details are present! I can now generate the Stitch prompt directly."
                })
                state.manifest.is_complete = True
                state.manifest.completion_percentage = 100
            
        except Exception as e:
            state.chat_history.append({
                "role": "assistant",
                "content": f"I analyzed the documents but encountered an issue: {str(e)}. Please try again or provide more details."
            })
        
        state.updated_at = datetime.utcnow()
        return state
    
    async def extract_manifest(self, state: AgentState) -> AgentState:
        """Step 2: Extract manifest details from the document."""
        combined_text = "\n\n---\n\n".join([doc.get("extracted_text", "") for doc in state.raw_documents])
        
        extraction_prompt = f"""
Extract specific project details from the document text.
Return ONLY the JSON with extracted values (use null if not found). Do NOT guess.

{{
    "app_name": "app name or null",
    "target_audience": "target audience or null",
    "platform": "platform or null",
    "primary_color": "primary color or null",
    "ui_style": "ui style or null",
    "navigation_pattern": "navigation pattern or null",
    "tech_stack": "mentioned tech stack or null",
    "component_library": "mentioned component library or null",
    "icon_set": "mentioned icon set or null"
}}

Document text:
{combined_text[:8000]}
"""
        
        try:
            result_text = await self.generate_content(extraction_prompt)
            extracted = json.loads(result_text)
            
            # Update manifest
            state.manifest.app_name = extracted.get("app_name")
            state.manifest.target_audience = extracted.get("target_audience")
            state.manifest.platform = extracted.get("platform")
            state.manifest.primary_color = extracted.get("primary_color")
            state.manifest.ui_style = extracted.get("ui_style")
            state.manifest.navigation_pattern = extracted.get("navigation_pattern")
            state.manifest.tech_stack = extracted.get("tech_stack")
            state.manifest.component_library = extracted.get("component_library")
            state.manifest.icon_set = extracted.get("icon_set")
            
        except Exception:
            pass  # Keep manifest as-is, will detect gaps next
        
        state.updated_at = datetime.utcnow()
        return state
    
    async def detect_missing_fields(self, state: AgentState) -> AgentState:
        """Step 3: Use questions from the AI analysis instead of generating new ones."""
        # Use the questions generated during analyze_documents
        if hasattr(state, 'pending_questions'):
            state.missing_questions = state.pending_questions
        else:
            state.missing_questions = []
        
        state.updated_at = datetime.utcnow()
        return state
    
    async def generate_stitch_prompt(self, state: AgentState) -> AgentState:
        """Step 4: Generate the final Stitch AI prompt using the user's proven structure."""
        state.status = "generating"
        
        manifest = state.manifest
        analysis = state.analysis if hasattr(state, 'analysis') else {}
        
        # Prepare lists for f-string
        if manifest.features:
            features_list = "\n".join(f"- {feature}" for feature in manifest.features[:15])
        else:
            features_list = "- Home Screen\n- Product Listing\n- Product Detail\n- Cart\n- Checkout"
        
        if manifest.user_flows:
            flows_list = "\n".join(f"- {flow}" for flow in manifest.user_flows[:10])
        else:
            flows_list = "- Guest checkout flow\n- Order tracking flow\n- Product browsing flow"
        
        # Generate dynamic screen inventory string
        screen_list = "\n".join(f"{i+1}. {s}" for i, s in enumerate(manifest.screen_inventory)) if manifest.screen_inventory else "1. HOME SCREEN\n2. DASHBOARD"
        
        final_prompt = f"""You are the Ultimate AI GUI Generator Prompt Engineer.
You have successfully collected all project variables. Now you must generate the absolute perfect blueprint instructions for an AI Design Platform (like Figma Make or Stitch) to generate the UI exactly as specified.

YOUR OUTPUT REQUIREMENT:
Generate ONLY the comprehensive prompt text that the user will paste into their AI UI generation platform.
DO NOT WRITE ANY CODE OR FRAMEWORK INSTRUCTIONS. Focus ENTIRELY on design tokens, layouts, screen inventories, and UX states.

You MUST format your output EXACTLY mirroring the following structural format with ASCII boxes for the screens:

Generate a complete, high-fidelity app UI for "{manifest.app_name}" — {manifest.ui_style}.

🔹 APP OVERVIEW
• App Name: {manifest.app_name}
• Platform: {manifest.platform}
• Target Audience: {manifest.target_audience}
• Style: {manifest.ui_style}
• Primary Brand Color: {manifest.primary_color}

🔹 DESIGN SYSTEM
COLORS:
• Primary: {manifest.primary_color}
[Define Background, Surface, Border, Text Primary, Text Secondary, Success, Error]

TYPOGRAPHY:
[Define Headings, Body, Arabic support if applicable]

COMPONENTS:
[Define Buttons, Cards, Inputs, Icons based on: {manifest.design_system}]

🔹 SCREEN INVENTORY
{screen_list}

🔹 DETAILED SCREEN SPECIFICATIONS
[For EVERY screen in the Screen Inventory, create a detailed ASCII box template exactly like this:]
┌─────────────────────────────────────────────┐
│ 1. [SCREEN NAME]                            │
├─────────────────────────────────────────────┤
│ LAYOUT:                                     │
│ • [Layout instructions]                     │
│                                             │
│ CONTENT:                                    │
│ • [Component instructions]                  │
└─────────────────────────────────────────────┘

🔹 BOTTOM NAVIGATION (If applicable)
[Define tabs and active states]

🔹 GLOBAL COMPONENTS & PATTERNS
[Define LOADING STATES, EMPTY STATES, ERROR STATES, TOASTS]

🔹 RTL (ARABIC) SPECIFICATIONS
[Define RTL rules based on: {manifest.rtl_support}]

🔹 UX ENHANCEMENTS & MICRO-INTERACTIONS
[Define Haptics, Swipe behaviors, Transitions]

Do NOT converse. Output only the final blueprint prompt ready to be copy-pasted into Stitch/Figma.
"""
        
        # Use AI to generate the final refined prompt
        try:
            result_text = await self.generate_content(final_prompt)
            
            # Extract the generated prompt
            state.final_stitch_prompt = result_text.strip()
            
            state.chat_history.append({
                "role": "assistant",
                "content": "✅ I've generated the comprehensive Stitch prompt based on your document and answers. You can now use this prompt in Stitch AI to generate your app UI!"
            })
            
        except Exception as e:
            # Fallback to the structured prompt we built
            state.final_stitch_prompt = final_prompt
            state.chat_history.append({
                "role": "assistant",
                "content": f"I've generated the Stitch prompt. Note: {str(e)}"
            })
        
        state.status = "complete"
        state.manifest.is_complete = True
        state.manifest.completion_percentage = 100
        state.updated_at = datetime.utcnow()
        
        return state


# Initialize agent
ux_agent = UXArchitectAgent()

# FASTAPI APP
# ============================================================================

# In-memory session store (replace with Redis for production)
sessions: Dict[str, AgentState] = {}

app = FastAPI(
    title="UX Architect Agent",
    description="Senior Product Designer AI that creates perfect Stitch prompts",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

class CreateSessionRequest(BaseModel):
    message: Optional[str] = None
    provider: str = "ollama"

class AnswerQuestionsRequest(BaseModel):
    answers: List[Dict[str, Any]]

class ChatMessageRequest(BaseModel):
    message: str


@app.post("/api/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new UX Architect session."""
    session_id = str(uuid.uuid4())
    
    manifest = ProjectManifest()
    
    session = AgentState(
        session_id=session_id,
        manifest=manifest,
        chat_history=[],
        provider=request.provider
    )
    
    if request.message:
        session.chat_history.append({
            "role": "user",
            "content": request.message
        })
        session.raw_documents.append({
            "type": "text",
            "extracted_text": request.message
        })
    
    sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "status": session.status,
        "manifest": session.manifest.dict(),
        "message": "Session created. Upload documents or start chatting to begin analysis."
    }


@app.get("/api/sessions")
async def list_sessions():
    """List all available UX Architect sessions."""
    result = []
    # Sort by updated_at descending (newest first)
    sorted_sessions = sorted(sessions.values(), key=lambda s: s.updated_at, reverse=True)
    
    for session in sorted_sessions:
        name = session.manifest.app_name or "Untitled Project"
        result.append({
            "session_id": session.session_id,
            "name": name,
            "status": session.status,
            "updated_at": session.updated_at.isoformat()
        })
    return {"sessions": result}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get current session state."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    return {
        "session_id": session_id,
        "status": session.status,
        "manifest": session.manifest.dict(),
        "completion_percentage": session.manifest.completion_percentage,
        "chat_history": session.chat_history,
        "missing_questions": session.missing_questions,
        "final_stitch_prompt": session.final_stitch_prompt,
        "is_complete": session.manifest.is_complete
    }


@app.post("/api/sessions/{session_id}/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    """Upload and process a document."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Extract text
    extracted_text = ""
    content_type = file.content_type or ""
    
    try:
        if "pdf" in content_type:
            doc = fitz.open(file_path)
            for page in doc:
                extracted_text += page.get_text()
            doc.close()
        
        elif "word" in content_type or "docx" in content_type:
            doc = DocxDocument(file_path)
            extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        
        else:
            # Try as text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
    
    except Exception as e:
        extracted_text = f"[Extraction error: {str(e)}]"
    
    # Add to session
    session.raw_documents.append({
        "filename": file.filename,
        "type": content_type,
        "extracted_text": extracted_text[:50000],  # Limit size
        "uploaded_at": datetime.utcnow().isoformat()
    })
    
    return {
        "message": f"Uploaded {file.filename}",
        "extracted_length": len(extracted_text),
        "session_id": session_id
    }


@app.post("/api/sessions/{session_id}/analyze")
async def start_analysis(session_id: str):
    """Start document analysis."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Create agent with the session's provider
    agent = UXArchitectAgent(provider=session.provider)
    
    # Run analysis pipeline
    session = await agent.analyze_documents(session)
    session = await agent.extract_manifest(session)
    session = await agent.detect_missing_fields(session)
    sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "status": session.status,
        "manifest": session.manifest.dict(),
        "chat_history": session.chat_history,
        "missing_questions": session.missing_questions,
        "completion_percentage": session.manifest.completion_percentage,
        "is_complete": session.manifest.is_complete
    }


@app.post("/api/sessions/{session_id}/answers")
async def submit_answers(session_id: str, request: AnswerQuestionsRequest):
    """Submit answers to missing questions."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Update manifest with answers
    for answer in request.answers:
        field = answer.get("field")
        value = answer.get("value")
        if field and value:
            setattr(session.manifest, field, value)
    
    # Clear missing questions since all answers received
    session.missing_questions = []
    
    # Generate final prompt
    agent = UXArchitectAgent(provider=session.provider)
    session = await agent.generate_stitch_prompt(session)
    sessions[session_id] = session
    
    return {
        "manifest": session.manifest.dict(),
        "is_complete": session.manifest.is_complete,
        "completion_percentage": session.manifest.completion_percentage
    }


@app.get("/api/sessions/{session_id}/sse")
async def session_sse(session_id: str):
    """Server-Sent Events for real-time updates."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    async def event_generator() -> AsyncGenerator[str, None]:
        last_state = None
        
        while True:
            session = sessions.get(session_id)
            if not session:
                break
            
            current_state = {
                "status": session.status,
                "manifest": session.manifest.dict(),
                "completion": session.manifest.completion_percentage,
                "chat_history_length": len(session.chat_history)
            }
            
            if current_state != last_state:
                yield f"data: {json.dumps(current_state)}\n\n"
                last_state = current_state
            
            if session.status == "complete":
                break
            
            await asyncio.sleep(1)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/api/sessions/{session_id}/prompt")
async def get_final_prompt(session_id: str):
    """Get the final Stitch prompt."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if not session.manifest.is_complete:
        raise HTTPException(
            status_code=400,
            detail="Project not complete. Answer all questions first."
        )
    
    # Generate if not already
    if not session.final_stitch_prompt:
        session = await ux_agent.generate_stitch_prompt(session)
        sessions[session_id] = session
    
    return {
        "stitch_prompt": session.final_stitch_prompt,
        "manifest": session.manifest.dict()
    }


@app.post("/api/sessions/{session_id}/chat")
async def chat_message(session_id: str, request: ChatMessageRequest):
    """Send a chat message to the agent."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    session.chat_history.append({
        "role": "user",
        "content": request.message
    })
    
    # Quick response for general chat
    response = "I'm your UX Architect. Upload documents and I'll analyze them to create a perfect Stitch AI prompt for your app. The sidebar shows what information I've extracted."
    
    session.chat_history.append({
        "role": "assistant",
        "content": response
    })
    
    return {
        "response": response,
        "chat_history": session.chat_history
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/api/providers")
async def get_providers():
    """Get available AI providers and their configuration status."""
    return {
        "providers": [
            {
                "id": "groq",
                "name": "Groq (Fast Cloud API)",
                "configured": True,
                "description": "Fast cloud inference with free 1M tokens/day"
            },
            {
                "id": "ollama",
                "name": "Ollama (Local - Private)",
                "configured": True,
                "description": "Local inference - requires 'ollama run qwen2.5:14b'"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
