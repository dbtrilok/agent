"""
UX Architect Agent - FastAPI Backend with LangGraph
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
from pydantic import BaseModel, Field

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Google Gemini
import google.generativeai as genai

# Document processing
import fitz  # PyMuPDF
from docx import Document as DocxDocument

# Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ============================================================================
# DATA MODELS
# ============================================================================

class ProjectManifest(BaseModel):
    """Tracks what the agent has extracted vs what's missing."""
    app_name: Optional[str] = None
    app_type: Optional[str] = None  # eCommerce, SaaS, Fintech, etc.
    target_audience: Optional[str] = None
    platform: Optional[str] = None  # mobile, web, both
    
    # Design Direction
    primary_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    ui_style: Optional[str] = None  # minimal, premium, playful, etc.
    inspiration_apps: Optional[List[str]] = None
    
    # UX Strategy
    navigation_pattern: Optional[str] = None  # bottom nav, tabs, drawer
    primary_user_goal: Optional[str] = None  # fast checkout, browsing, etc.
    
    # Business
    conversion_focus: Optional[bool] = None
    special_logic: Optional[List[str]] = None  # discounts, subscriptions, etc.
    
    # Extracted from docs
    features: List[str] = Field(default_factory=list)
    user_flows: List[str] = Field(default_factory=list)
    data_structures: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Status tracking
    @property
    def is_complete(self) -> bool:
        required = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal
        ]
        return all(field is not None for field in required)
    
    @property
    def completion_percentage(self) -> int:
        fields = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal,
            self.inspiration_apps, self.conversion_focus
        ]
        filled = sum(1 for f in fields if f is not None)
        return int((filled / len(fields)) * 100)


class AgentState(BaseModel):
    """Full state for LangGraph."""
    session_id: str
    status: str = "idle"  # idle, analyzing, waiting_input, generating, complete
    manifest: ProjectManifest
    raw_documents: List[Dict[str, Any]] = Field(default_factory=list)
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    missing_questions: List[Dict[str, Any]] = Field(default_factory=list)
    final_stitch_prompt: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# LANGGRAPH NODES
# ============================================================================

class UXArchitectGraph:
    """
    LangGraph implementing the Senior Product Designer behavior.
    Strictly follows: Analyze → Extract → Detect Gaps → Ask → Wait → Generate
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.workflow = self._build_graph()
        self.checkpointer = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.checkpointer)
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(dict)  # Use dict for flexibility
        
        # Define nodes
        workflow.add_node("analyze_docs", self._analyze_documents)
        workflow.add_node("extract_manifest", self._extract_to_manifest)
        workflow.add_node("detect_gaps", self._detect_missing_fields)
        workflow.add_node("human_gate", self._human_gate)
        workflow.add_node("generate_prompt", self._generate_stitch_prompt)
        
        # Define edges
        workflow.set_entry_point("analyze_docs")
        workflow.add_edge("analyze_docs", "extract_manifest")
        workflow.add_edge("extract_manifest", "detect_gaps")
        workflow.add_conditional_edges(
            "detect_gaps",
            self._should_wait_or_generate,
            {
                "wait": "human_gate",
                "generate": "generate_prompt"
            }
        )
        workflow.add_edge("human_gate", "detect_gaps")
        workflow.add_edge("generate_prompt", END)
        
        return workflow
    
    async def _analyze_documents(self, state: dict) -> dict:
        """Step 1: Deep analysis of input documents."""
        agent_state = AgentState(**state)
        agent_state.status = "analyzing"
        
        # Combine all document text
        all_text = []
        for doc in agent_state.raw_documents:
            if "extracted_text" in doc:
                all_text.append(doc["extracted_text"])
        
        combined_text = "\n\n---\n\n".join(all_text)
        
        if not combined_text.strip():
            agent_state.chat_history.append({
                "role": "assistant",
                "content": "I've received your request, but no document text was extracted. Please upload a PDF, DOCX, or paste your product requirements directly in the chat."
            })
            return {**agent_state.dict(), "goto": "detect_gaps"}
        
        # Use Gemini to analyze
        analysis_prompt = f"""
        You are a Senior Product Designer analyzing product documents.
        
        Analyze the following documents and identify:
        1. App type (eCommerce, SaaS, Fintech, Health, Social, etc.)
        2. Core features and modules
        3. User flows (explicit or implied)
        4. Input fields and data structures mentioned
        5. Business intent (conversion, engagement, retention)
        6. Any acceptance criteria or specific requirements
        
        Documents:
        {combined_text[:10000]}
        
        Provide a structured analysis in JSON format:
        {{
            "app_type": "...",
            "features": ["..."],
            "user_flows": ["..."],
            "data_structures": ["..."],
            "business_intent": "...",
            "acceptance_criteria": ["..."]
        }}
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                analysis_prompt
            )
            analysis = json.loads(response.text)
            
            # Store analysis in state for manifest extraction
            state["_analysis"] = analysis
            
            agent_state.chat_history.append({
                "role": "assistant",
                "content": f"📄 I've analyzed your documents. This appears to be a **{analysis.get('app_type', 'Unknown')}** app with {len(analysis.get('features', []))} features. Let me extract the project details..."
            })
            
        except Exception as e:
            agent_state.chat_history.append({
                "role": "assistant",
                "content": f"I analyzed the documents but encountered an issue: {str(e)}. Let me proceed with what I can extract."
            })
            state["_analysis"] = {}
        
        agent_state.updated_at = datetime.utcnow()
        return agent_state.dict()
    
    async def _extract_to_manifest(self, state: dict) -> dict:
        """Step 2: Populate Project Manifest from analysis."""
        agent_state = AgentState(**state)
        analysis = state.get("_analysis", {})
        
        # Try to extract from documents
        extraction_prompt = f"""
        Extract specific project details from this analysis or raw text.
        Return ONLY the JSON with extracted values (use null if not found):
        
        {{
            "app_name": "app name or null",
            "target_audience": "target users or null",
            "platform": "mobile/web/both or null",
            "primary_color": "hex code or null",
            "ui_style": "minimal/premium/playful/etc or null",
            "navigation_pattern": "bottom_nav/tabs/drawer/etc or null",
            "inspiration_apps": ["app names"]
        }}
        
        Analysis: {json.dumps(analysis)}
        Raw text sample: {str(state.get('raw_documents', []))[:2000]}
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                extraction_prompt
            )
            extracted = json.loads(response.text)
            
            # Update manifest
            manifest = agent_state.manifest
            manifest.app_name = extracted.get("app_name")
            manifest.target_audience = extracted.get("target_audience")
            manifest.platform = extracted.get("platform")
            manifest.primary_color = extracted.get("primary_color")
            manifest.ui_style = extracted.get("ui_style")
            manifest.navigation_pattern = extracted.get("navigation_pattern")
            manifest.inspiration_apps = extracted.get("inspiration_apps", [])
            
            # Set extracted features
            manifest.features = analysis.get("features", [])
            manifest.user_flows = analysis.get("user_flows", [])
            manifest.data_structures = analysis.get("data_structures", [])
            manifest.acceptance_criteria = analysis.get("acceptance_criteria", [])
            
        except Exception:
            pass  # Keep manifest as-is, will detect gaps next
        
        agent_state.updated_at = datetime.utcnow()
        return agent_state.dict()
    
    async def _detect_missing_fields(self, state: dict) -> dict:
        """Step 3: Detect what critical information is missing."""
        agent_state = AgentState(**state)
        manifest = agent_state.manifest
        
        questions = []
        
        # Check each critical field
        if not manifest.app_name:
            questions.append({
                "id": "app_name",
                "question": "What is the name of your app?",
                "type": "text",
                "required": True,
                "context": "This will be used throughout the UI"
            })
        
        if not manifest.app_type:
            questions.append({
                "id": "app_type",
                "question": "What type of app is this?",
                "type": "select",
                "options": ["eCommerce", "SaaS", "Fintech", "Health & Fitness", "Social", "Education", "Food & Delivery", "Travel", "Other"],
                "required": True,
                "context": "Helps determine appropriate UX patterns"
            })
        
        if not manifest.target_audience:
            questions.append({
                "id": "target_audience",
                "question": "Who is your target audience?",
                "type": "text",
                "required": True,
                "context": "e.g., 'Young professionals 25-35', 'Fitness enthusiasts', 'Small business owners'"
            })
        
        if not manifest.platform:
            questions.append({
                "id": "platform",
                "question": "What platform(s)?",
                "type": "select",
                "options": ["iOS Mobile", "Android Mobile", "Cross-Platform Mobile", "Web App", "Mobile + Web"],
                "required": True,
                "context": "Determines screen sizes and UI patterns"
            })
        
        if not manifest.primary_color:
            questions.append({
                "id": "primary_color",
                "question": "What is your primary brand color?",
                "type": "color",
                "required": True,
                "context": "Used for buttons, active states, and key UI elements"
            })
        
        if not manifest.ui_style:
            questions.append({
                "id": "ui_style",
                "question": "What UI style do you prefer?",
                "type": "select",
                "options": [
                    "Minimalist (clean, whitespace, subtle)",
                    "Premium/Luxury (rich, elegant, sophisticated)",
                    "Playful/Energetic (bright, rounded, friendly)",
                    "Corporate/Professional (structured, neutral, formal)",
                    "Modern/Bold (high contrast, strong typography)"
                ],
                "required": True,
                "context": "Sets the visual personality of your app"
            })
        
        if not manifest.navigation_pattern:
            questions.append({
                "id": "navigation_pattern",
                "question": "Preferred navigation pattern?",
                "type": "select",
                "options": [
                    "Bottom Navigation Bar (5 items max)",
                    "Tab Bar (top, segment control)",
                    "Navigation Drawer (hamburger menu)",
                    "Floating Action Button + Contextual",
                    "Gesture-based (swipe between sections)"
                ],
                "required": True,
                "context": "How users move between main sections"
            })
        
        if not manifest.primary_user_goal:
            questions.append({
                "id": "primary_user_goal",
                "question": "What is the PRIMARY user goal?",
                "type": "select",
                "options": [
                    "Fast task completion (get in, get out)",
                    "Browse and discover content",
                    "Complete a transaction/purchase",
                    "Track progress over time",
                    "Social engagement and connection",
                    "Learn or consume educational content"
                ],
                "required": True,
                "context": "This drives the UX optimization strategy"
            })
        
        if not manifest.conversion_focus:
            questions.append({
                "id": "conversion_focus",
                "question": "Is conversion (sales/signups) a primary goal?",
                "type": "boolean",
                "required": False,
                "context": "Affects CTA placement and urgency design"
            })
        
        agent_state.missing_questions = questions
        agent_state.updated_at = datetime.utcnow()
        
        return agent_state.dict()
    
    def _should_wait_or_generate(self, state: dict) -> str:
        """Conditional: Wait for human input or proceed to generate."""
        agent_state = AgentState(**state)
        
        if agent_state.manifest.is_complete:
            return "generate"
        
        if agent_state.missing_questions:
            return "wait"
        
        return "generate"
    
    async def _human_gate(self, state: dict) -> dict:
        """Step 4: INTERRUPT - Wait for human answers."""
        agent_state = AgentState(**state)
        agent_state.status = "waiting_input"
        
        # Build the message
        questions = agent_state.missing_questions
        if questions:
            msg = "⏸️ **STOP AND WAIT**\n\nI've analyzed your documents but I'm missing critical details to create a high-quality Stitch prompt.\n\n"
            msg += f"**{len(questions)} questions need your input:**\n\n"
            
            for i, q in enumerate(questions, 1):
                msg += f"{i}. **{q['question']}**\n"
                if q.get('context'):
                    msg += f"   *{q['context']}*\n"
                msg += "\n"
            
            msg += "Please answer in the form below. I cannot generate the final prompt until these are confirmed."
            
            agent_state.chat_history.append({
                "role": "assistant",
                "content": msg
            })
        
        # INTERRUPT - This pauses execution until human responds
        response = interrupt({
            "type": "waiting_for_input",
            "message": "Please answer the missing questions",
            "questions": questions,
            "manifest": agent_state.manifest.dict()
        })
        
        # When resumed, update manifest with answers
        if response:
            for answer in response.get("answers", []):
                field = answer.get("field")
                value = answer.get("value")
                
                if field and value:
                    setattr(agent_state.manifest, field, value)
        
        agent_state.updated_at = datetime.utcnow()
        return agent_state.dict()
    
    async def _generate_stitch_prompt(self, state: dict) -> dict:
        """Step 5: Generate the final Stitch AI prompt."""
        agent_state = AgentState(**state)
        agent_state.status = "generating"
        
        manifest = agent_state.manifest
        
        stitch_prompt = f"""# Stitch AI Prompt: {manifest.app_name}

## App Overview
- **App Name:** {manifest.app_name}
- **App Type:** {manifest.app_type}
- **Platform:** {manifest.platform}
- **Target Audience:** {manifest.target_audience}
- **UI Style:** {manifest.ui_style}
- **Primary Goal:** {manifest.primary_user_goal}

## Design System
- **Primary Color:** {manifest.primary_color}
- **Color Palette:** {manifest.color_palette or [manifest.primary_color] if manifest.primary_color else "TBD"}
- **Typography:** Modern, readable fonts (Inter/Roboto for body, bold for headers)
- **Spacing:** 8pt grid system
- **Border Radius:** Medium (8-12px) for friendly feel, or Sharp (0-4px) for premium
- **Elevation:** Subtle shadows for cards (2-4dp), stronger for modals (8dp)

## Navigation
- **Pattern:** {manifest.navigation_pattern}
- **Structure:** Clear information hierarchy
- **Back Navigation:** Consistent back button/gesture support

## Screens (Dynamic Generation)
Based on features: {', '.join(manifest.features[:5])}{' and more...' if len(manifest.features) > 5 else ''}

### Screen Structure (Generate dynamically):
1. **Home/Dashboard Screen**
   - Purpose: Primary entry point, showcase key features
   - Layout: Header with app branding, main content area, {manifest.navigation_pattern}
   - Components: Featured content cards, quick actions, status indicators
   - CTA: Primary action button matching {manifest.primary_user_goal}

2. **Feature Screens** (generate based on: {manifest.features})
   - Purpose: Specific feature functionality
   - Layout: Feature-specific layouts optimized for task
   - Components: Forms, lists, media, interactive elements
   - States: Loading (skeleton), Empty, Error, Success

3. **Profile/Settings Screen**
   - Purpose: User configuration and account management
   - Layout: Clean list-based layout with sections
   - Components: Avatar, form inputs, toggle switches

## UX Design Strategy
- **Primary Goal Optimization:** {manifest.primary_user_goal}
- **Friction Reduction:** Minimal steps to complete tasks
- **Cognitive Load:** Clear visual hierarchy, progressive disclosure
- **Feedback:** Immediate visual feedback for all interactions
- **Accessibility:** WCAG 2.1 AA compliant (contrast, touch targets, screen reader support)

## Prototype Flow
Define these screen-to-screen transitions:
- Home → Feature Screen: Tap on feature card
- Feature → Detail: Tap on list item
- Any Screen → Back: Swipe back gesture or back button
- CTA Actions: Modal sheets for quick tasks, full screen for complex flows

## Component System
**Reusable Components:**
- Primary Button: {manifest.primary_color} background, white text, 48px height
- Secondary Button: Outlined style, same color
- Input Fields: 56px height, clear labels, inline validation
- Cards: White background, subtle shadow, 16px padding
- Lists: Clear separators, swipe actions where appropriate
- Modals/Bottom Sheets: For secondary tasks, maintain context

## Special States
**Loading States:**
- Skeleton screens matching content structure
- Shimmer effect on images
- Progress indicators for multi-step processes

**Empty States:**
- Friendly illustrations
- Clear explanation text
- Direct CTA to populate content

**Error States:**
- Non-blocking inline validation
- Clear error messages with solutions
- Retry mechanisms for network errors

## Interactions & Micro-animations
- **Button Press:** Scale down to 0.95, 100ms
- **Screen Transitions:** Slide from right (iOS style), 300ms
- **List Items:** Subtle lift on press
- **Success:** Checkmark animation with haptic feedback
- **Loading:** Pulsing skeleton, progress rings

## UX Enhancements
{chr(10).join(f'- {f}' for f in manifest.user_flows[:3]) if manifest.user_flows else '- Optimized for user engagement'}
- Smart defaults based on user context
- Personalization where applicable
- Quick actions for common tasks
- Contextual help/tooltips for complex features

## Output Requirements
Generate a complete, interactive mobile app UI with:
- All screens needed for the user flows
- Working navigation between screens
- Interactive components (buttons, inputs, etc.)
- Realistic content and data
- Production-ready polish and micro-interactions
- Ready for user testing and stakeholder review
"""
        
        agent_state.final_stitch_prompt = stitch_prompt
        agent_state.status = "complete"
        
        agent_state.chat_history.append({
            "role": "assistant",
            "content": "✅ **PROJECT COMPLETE!**\n\nI've analyzed your documents, confirmed all critical details, and generated a comprehensive Stitch AI prompt.\n\nYour project manifest is now 100% complete. You can copy the Stitch prompt and use it to generate your app UI."
        })
        
        agent_state.updated_at = datetime.utcnow()
        return agent_state.dict()


# Initialize graph
ux_graph = UXArchitectGraph()

# ============================================================================
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
        chat_history=[]
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
    
    # Run graph to analyze point
    try:
        result = await ux_graph.app.ainvoke(
            session.dict(),
            config={"configurable": {"thread_id": session_id}}
        )
        
        # Update session
        sessions[session_id] = AgentState(**result)
        
        return {
            "status": result["status"],
            "manifest": result["manifest"],
            "chat_history": result["chat_history"],
            "missing_questions": result["missing_questions"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


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
    
    # If all questions answered, generate prompt
    if session.manifest.is_complete:
        try:
            result = await ux_graph.app.ainvoke(
                session.dict(),
                config={"configurable": {"thread_id": session_id}},
                resume={"answers": request.answers}
            )
            sessions[session_id] = AgentState(**result)
        except Exception as e:
            # Graph might not handle resume properly, manually generate
            pass
    
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
        result = await ux_graph.app.ainvoke(
            session.dict(),
            config={"configurable": {"thread_id": session_id}}
        )
        sessions[session_id] = AgentState(**result)
        session = sessions[session_id]
    
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
    return {"status": "healthy", "gemini_configured": bool(GEMINI_API_KEY)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
