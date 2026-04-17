"use client";

import React, { useState, useCallback, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "prism-react-renderer";

// Icons
const Icons = {
  Upload: () => <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>,
  File: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>,
  Check: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>,
  Alert: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
  Send: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>,
  Copy: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>,
  Download: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>,
  Sparkles: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>,
  ChevronDown: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>,
  ChevronRight: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>,
};

// Types
interface ProjectManifest {
  app_name?: string;
  app_type?: string;
  target_audience?: string;
  platform?: string;
  primary_color?: string;
  ui_style?: string;
  navigation_pattern?: string;
  tech_stack?: string;
  component_library?: string;
  icon_set?: string;
  responsive_rules?: string;
  primary_user_goal?: string;
  conversion_focus?: boolean;
  inspiration_apps?: string[];
  features: string[];
  user_flows: string[];
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface Question {
  id?: string;
  field?: string;
  question: string;
  type: "text" | "select" | "color" | "boolean";
  options?: string[];
  required: boolean;
  context?: string;
}

interface SessionState {
  session_id?: string;
  field?: string;
  status: string;
  manifest: ProjectManifest;
  chat_history: ChatMessage[];
  missing_questions: Question[];
  completion_percentage: number;
  is_complete: boolean;
  final_stitch_prompt?: string;
}

// API base URL
const API_BASE = "http://localhost:8001/api";

// Provider types
type Provider = "groq" | "ollama";

interface ProviderConfig {
  id: Provider;
  name: string;
  configured: boolean;
  description: string;
}

interface HistoricalProject {
  session_id: string;
  field?: string;
  name: string;
  status: string;
  updated_at: string;
}

const emptySessionState: SessionState = {
  session_id: "",
  status: "idle",
  manifest: {
    features: [],
    user_flows: [],
  },
  chat_history: [],
  missing_questions: [],
  completion_percentage: 0,
  is_complete: false,
};

// Components
const Button = ({ children, onClick, variant = "primary", disabled = false, className = "" }: any) => {
  const baseStyles = "px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2";
  const variants = {
    primary: "bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200 disabled:opacity-50",
    outline: "border-2 border-slate-200 text-slate-700 hover:border-slate-900 hover:text-slate-900",
    ghost: "text-slate-600 hover:text-slate-900 hover:bg-slate-50",
  };
  return (
    <button onClick={onClick} disabled={disabled} className={`${baseStyles} ${variants[variant as keyof typeof variants]} ${className}`}>
      {children}
    </button>
  );
};

const Card = ({ children, className = "" }: any) => (
  <div className={`bg-white rounded-xl border border-slate-200 shadow-sm ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, variant = "default" }: any) => {
  const variants = {
    default: "bg-slate-100 text-slate-700",
    amber: "bg-amber-50 text-amber-700 border border-amber-200",
    green: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    blue: "bg-blue-50 text-blue-700",
  };
  return (
    <span className={`px-2 py-1 rounded-md text-xs font-medium ${variants[variant as keyof typeof variants]}`}>
      {children}
    </span>
  );
};

// Progress Bar
const ProgressBar = ({ percentage }: { percentage: number }) => (
  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
    <div
      className={`h-full transition-all duration-500 ${percentage === 100 ? "bg-emerald-500" : "bg-slate-900"}`}
      style={{ width: `${percentage}%` }}
    />
  </div>
);

// Project Manifest Sidebar Item
const ManifestItem = ({ label, value, isComplete }: { label: string; value?: string; isComplete: boolean }) => (
  <div className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-slate-50 transition-colors">
    <div className="flex items-center gap-3">
      <div className={`w-5 h-5 rounded-full flex items-center justify-center ${isComplete ? "bg-emerald-100 text-emerald-600" : "bg-amber-100 text-amber-600"}`}>
        {isComplete ? <Icons.Check /> : <Icons.Alert />}
      </div>
      <span className="text-sm font-medium text-slate-700">{label}</span>
    </div>
    {value ? (
      <span className="text-sm text-slate-500 max-w-[120px] truncate">{value}</span>
    ) : (
      <Badge variant="amber">Missing</Badge>
    )}
  </div>
);

// Code Block with Copy
const CodeBlock = ({ code }: { code: string }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadMarkdown = () => {
    const blob = new Blob([code], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "stitch-prompt.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative group">
      <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" onClick={copyToClipboard} className="!px-2 !py-1 text-xs">
          {copied ? "Copied!" : <><Icons.Copy /> Copy</>}
        </Button>
        <Button variant="ghost" onClick={downloadMarkdown} className="!px-2 !py-1 text-xs">
          <Icons.Download /> .md
        </Button>
      </div>
      <pre className="bg-slate-900 text-slate-50 p-6 rounded-xl overflow-x-auto text-sm font-mono leading-relaxed max-h-[600px] overflow-y-auto">
        <code>{code}</code>
      </pre>
    </div>
  );
};

// Dynamic Question Form
const QuestionForm = ({ questions, onSubmit, disabled }: { questions: Question[]; onSubmit: (answers: any[]) => void; disabled: boolean }) => {
  const [answers, setAnswers] = useState<Record<string, any>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formattedAnswers = Object.entries(answers).map(([field, value]) => ({
      field,
      value,
    }));
    onSubmit(formattedAnswers);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {questions.map((q, idx) => {
        const fieldKey = (q.field || q.id || idx.toString()) as string;
        return (
        <div key={fieldKey} className="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <div className="flex items-start gap-3 mb-3">
            <span className="bg-slate-900 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0">
              {idx + 1}
            </span>
            <div>
              <label className="font-medium text-slate-900 block">{q.question}</label>
              {q.context && <p className="text-sm text-slate-500 mt-1">{q.context}</p>}
            </div>
          </div>

          {q.type === "text" && (
            <input
              type="text"
              value={answers[fieldKey] || ""}
              onChange={(e) => setAnswers({ ...answers, [fieldKey]: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
              placeholder="Type your answer..."
            />
          )}

          {q.type === "color" && (
            <div className="flex items-center gap-3">
              <input
                type="color"
                value={answers[fieldKey] || "#6366F1"}
                onChange={(e) => setAnswers({ ...answers, [fieldKey]: e.target.value })}
                className="w-12 h-10 rounded cursor-pointer"
              />
              <input
                type="text"
                value={answers[fieldKey] || ""}
                onChange={(e) => setAnswers({ ...answers, [fieldKey]: e.target.value })}
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                placeholder="#6366F1"
              />
            </div>
          )}

          {q.type === "select" && q.options && (
            <select
              value={answers[fieldKey] || ""}
              onChange={(e) => setAnswers({ ...answers, [fieldKey]: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 bg-white"
            >
              <option value="">Select an option...</option>
              {q.options.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          )}

          {q.type === "boolean" && (
            <div className="flex gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={fieldKey}
                  checked={answers[fieldKey] === true}
                  onChange={() => setAnswers({ ...answers, [fieldKey]: true })}
                  className="w-4 h-4 text-slate-900"
                />
                <span>Yes</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={fieldKey}
                  checked={answers[fieldKey] === false}
                  onChange={() => setAnswers({ ...answers, [fieldKey]: false })}
                  className="w-4 h-4 text-slate-900"
                />
                <span>No</span>
              </label>
            </div>
          )}
        </div>
        );
      })}

      <Button type="submit" disabled={disabled || questions.length === 0} className="w-full justify-center">
        <Icons.Check />
        Submit Answers & Continue
      </Button>
    </form>
  );
};

// Main Application Component
export default function UXArchitectApp() {
  const [session, setSession] = useState<SessionState>(emptySessionState);
  const [projectsList, setProjectsList] = useState<HistoricalProject[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [providers, setProviders] = useState<ProviderConfig[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<Provider>("groq");
  const [showProviderDropdown, setShowProviderDropdown] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch providers on mount
  useEffect(() => {
    fetch(`${API_BASE}/providers`)
      .then(res => res.json())
      .then(data => setProviders(data.providers))
      .catch(err => console.error("Failed to fetch providers:", err));
      
    // Fetch projects
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${API_BASE}/sessions`);
      const data = await res.json();
      setProjectsList(data.sessions || []);
    } catch (e) {}
  };

  const loadProject = async (sessionId: string) => {
    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
      const data = await res.json();
      setSession(data);
    } catch (e) {
      alert("Failed to load project");
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [session.chat_history]);

  // File drop handler
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploadedFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  // Analyze documents
  const analyzeDocuments = async () => {
    if (uploadedFiles.length === 0) {
      alert("Please upload at least one document");
      return;
    }

    setIsLoading(true);

    try {
      // Create session with selected provider
      const sessionResponse = await fetch(`${API_BASE}/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: "Starting new project with document analysis",
          provider: selectedProvider 
        }),
      });
      const sessionData = await sessionResponse.json();
      setSession(sessionData);

      // Upload files
      for (const file of uploadedFiles) {
        const formData = new FormData();
        formData.append("file", file);
        await fetch(`${API_BASE}/sessions/${sessionData.session_id}/upload`, {
          method: "POST",
          body: formData,
        });
      }

      // Trigger analysis
      const analysisResponse = await fetch(`${API_BASE}/sessions/${sessionData.session_id}/analyze`, {
        method: "POST",
      });
      const analysisData = await analysisResponse.json();

      // Update session with analysis results
      setSession(analysisData);
      setUploadedFiles([]);
      fetchProjects();

    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Failed to analyze documents. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      // Documents
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "application/msword": [".doc"],
      "text/markdown": [".md"],
      "text/plain": [".txt"],
      // Images
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/gif": [".gif"],
      "image/webp": [".webp"],
      "image/svg+xml": [".svg"],
      // Other
      "application/json": [".json"],
      "text/html": [".html"],
      "text/css": [".css"],
      "application/javascript": [".js"],
    },
  });

  // Send chat message
  const sendMessage = async () => {
    if (!chatInput.trim()) return;

    const newMessage: ChatMessage = { role: "user", content: chatInput };
    setSession((prev) => ({
      ...prev,
      chat_history: [...prev.chat_history, newMessage],
    }));
    setChatInput("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      setSession((prev) => ({
        ...prev,
        chat_history: [
          ...prev.chat_history,
          {
            role: "assistant",
            content: "I'm your UX Architect. I've analyzed your request and will guide you through creating a perfect Stitch prompt. The sidebar shows what information I've extracted so far.",
          },
        ],
      }));
      setIsLoading(false);
    }, 1000);
  };

  // Submit question answers
  const submitAnswers = async (answers: any[]) => {
    console.log("Submitting answers:", answers);
    setIsLoading(true);

    try {
      // Send answers to backend
      const response = await fetch(`${API_BASE}/sessions/${session.session_id}/answers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers }),
      });
      const data = await response.json();

      // Update session with response
      setSession((prev) => ({
        ...prev,
        ...data,
      }));

      // If complete, fetch the final prompt
      if (data.is_complete) {
        const promptResponse = await fetch(`${API_BASE}/sessions/${session.session_id}/prompt`);
        const promptData = await promptResponse.json();
        setSession((prev) => ({
          ...prev,
          final_stitch_prompt: promptData.stitch_prompt,
        }));
      }
    } catch (error) {
      console.error("Failed to submit answers:", error);
      alert("Failed to submit answers. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Start new session
  const startNewSession = () => {
    setSession(emptySessionState);
    setUploadedFiles([]);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Left Sidebar - Project Manifest */}
      <aside className="w-80 bg-white border-r border-slate-200 flex flex-col fixed h-full">
        <div className="p-4 border-b border-slate-200 flex-shrink-0">
          <Button onClick={startNewSession} className="w-full justify-center">
            <Icons.Sparkles /> New Project
          </Button>
        </div>

        <div className="p-4 border-b border-slate-200 flex-shrink-0">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Your Projects</span>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {projectsList.length === 0 ? (
            <div className="text-center p-4">
              <p className="text-xs text-slate-400">No projects yet</p>
            </div>
          ) : (
            projectsList.map((proj) => (
              <button
                key={proj.session_id}
                onClick={() => loadProject(proj.session_id)}
                className={`w-full text-left p-3 rounded-lg flex flex-col gap-1 transition-colors ${
                  session.session_id === proj.session_id 
                    ? "bg-slate-100 border border-slate-200" 
                    : "hover:bg-slate-50 border border-transparent"
                }`}
              >
                <span className="text-sm font-medium text-slate-900 truncate">{proj.name}</span>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">
                    {new Date(proj.updated_at).toLocaleDateString()}
                  </span>
                  <Badge variant={proj.status === "complete" ? "green" : "amber"}>
                    {proj.status}
                  </Badge>
                </div>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Main Content - Claude-style Chat */}
      <main className="flex-1 ml-80 mr-0 lg:mr-96 flex flex-col h-screen">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto">
          {(session.chat_history || []).length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center p-8">
              <div className="text-center max-w-md">
                <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Icons.Sparkles />
                </div>
                <h2 className="text-2xl font-bold text-slate-900 mb-2">
                  UX Architect
                </h2>
                <p className="text-slate-600 mb-6">
                  I analyze your product documents and convert them into perfect Stitch AI prompts. 
                  Upload a PRD, user stories, or any product documentation to get started.
                </p>

                {/* Provider Selection */}
                <div className="mb-6">
                  <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
                    AI Provider
                  </label>
                  <div className="relative">
                    <button
                      onClick={() => setShowProviderDropdown(!showProviderDropdown)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg text-left flex items-center justify-between bg-white hover:border-slate-400 transition-colors"
                    >
                      <div>
                        <span className="font-medium text-slate-900">
                          {providers.find(p => p.id === selectedProvider)?.name || "Select Provider"}
                        </span>
                        <p className="text-xs text-slate-500">
                          {providers.find(p => p.id === selectedProvider)?.description}
                        </p>
                      </div>
                      <Icons.ChevronDown />
                    </button>
                    {showProviderDropdown && (
                      <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-10">
                        {providers.map((provider) => (
                          <button
                            key={provider.id}
                            onClick={() => {
                              setSelectedProvider(provider.id);
                              setShowProviderDropdown(false);
                            }}
                            className={`w-full px-3 py-3 text-left hover:bg-slate-50 transition-colors first:rounded-t-lg last:rounded-b-lg ${
                              selectedProvider === provider.id ? "bg-slate-50" : ""
                            }`}
                          >
                            <div className="font-medium text-slate-900">{provider.name}</div>
                            <p className="text-xs text-slate-500">{provider.description}</p>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  {selectedProvider === "groq" && (
                    <p className="text-xs text-emerald-600 mt-2">
                      Fast cloud response (2-5 seconds)
                    </p>
                  )}
                  {selectedProvider === "ollama" && (
                    <p className="text-xs text-amber-600 mt-2">
                      Requires: ollama run qwen2.5:14b
                    </p>
                  )}
                </div>

        {/* File Drop Zone */}
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                    isDragActive ? "border-slate-900 bg-slate-50" : "border-slate-300 hover:border-slate-400"
                  }`}
                >
                  <input {...getInputProps()} />
                  <Icons.Upload />
                  <p className="mt-2 text-sm font-medium text-slate-700">
                    {isDragActive ? "Drop files here..." : "Drag & drop files here"}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    PDF, DOCX, or Markdown
                  </p>
                </div>

                {uploadedFiles.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {uploadedFiles.map((file, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-slate-600 bg-slate-50 p-2 rounded-lg">
                        <Icons.File />
                        <span className="truncate">{file.name}</span>
                      </div>
                    ))}
                    <Button onClick={analyzeDocuments} disabled={isLoading} className="w-full mt-2">
                      {isLoading ? "Analyzing..." : "Analyze Documents"}
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="py-8 space-y-6">
              {session.chat_history.map((msg, idx) => (
                <div
                  key={idx}
                  className={`px-4 sm:px-6 lg:px-8 ${msg.role === "assistant" ? "bg-white" : ""}`}
                >
                  <div className="max-w-3xl mx-auto py-4">
                    <div className="flex gap-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        msg.role === "assistant" ? "bg-slate-900 text-white" : "bg-blue-500 text-white"
                      }`}>
                        {msg.role === "assistant" ? "AI" : "You"}
                      </div>
                      <div className="flex-1 prose prose-slate max-w-none">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {/* Dynamic Question Form */}
              {(session.missing_questions || []).length > 0 && (
                <div className="px-4 sm:px-6 lg:px-8">
                  <div className="max-w-3xl mx-auto">
                    <Card className="p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center">
                          AI
                        </div>
                        <span className="font-medium text-slate-900">Questions Needing Answers</span>
                      </div>
                      <QuestionForm
                        questions={session.missing_questions}
                        onSubmit={submitAnswers}
                        disabled={isLoading}
                      />
                    </Card>
                  </div>
                </div>
              )}

              {/* Final Output */}
              {session.final_stitch_prompt && (
                <div className="px-4 sm:px-6 lg:px-8">
                  <div className="max-w-3xl mx-auto">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center">
                        <Icons.Check />
                      </div>
                      <span className="font-medium text-slate-900">Final Stitch Prompt</span>
                      <Badge variant="green">Ready</Badge>
                    </div>
                    <CodeBlock code={session.final_stitch_prompt} />
                  </div>
                </div>
              )}

              {isLoading && (
                <div className="px-4 sm:px-6 lg:px-8">
                  <div className="max-w-3xl mx-auto py-4">
                    <div className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center">
                        AI
                      </div>
                      <div className="flex-1 flex items-center">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                          <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                          <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="border-t border-slate-200 bg-white p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Type a message or paste product requirements..."
                className="flex-1 px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
              <Button onClick={sendMessage} disabled={!chatInput.trim() || isLoading}>
                <Icons.Send />
              </Button>
            </div>
            <p className="text-xs text-slate-500 mt-2 text-center">
              The AI will not generate the final prompt until all critical details are confirmed.
            </p>
          </div>
        </div>
      </main>

      {/* Right Panel - Quick Actions (visible on large screens) */}
      <aside className="hidden lg:block w-96 bg-white border-l border-slate-200 fixed right-0 h-full overflow-y-auto">
        <div className="p-4 border-b border-slate-200">
          <h3 className="font-medium text-slate-900">Quick Actions</h3>
        </div>
        
        <div className="p-4 space-y-4">
          {/* Upload Section */}
          <Card className="p-4">
            <h4 className="text-sm font-medium text-slate-700 mb-3 flex items-center gap-2">
              <Icons.Upload />
              Upload Documents
            </h4>
            <div
              {...getRootProps()}
              className="border-2 border-dashed border-slate-300 rounded-lg p-4 text-center cursor-pointer hover:border-slate-400 transition-colors"
            >
              <input {...getInputProps()} />
              <p className="text-xs text-slate-600">Drop PDF, DOCX, or MD files</p>
            </div>
          </Card>

          {/* Status Card */}
          <Card className="p-4">
            <h4 className="text-sm font-medium text-slate-700 mb-3">Agent Status</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Status</span>
                <Badge variant={session.is_complete ? "green" : (session.missing_questions || []).length > 0 ? "amber" : "default"}>
                  {session.is_complete ? "Complete" : (session.missing_questions || []).length > 0 ? "Waiting" : "Ready"}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Completion</span>
                <span className="font-medium">{session.completion_percentage}%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">Questions</span>
                <span className="font-medium">{(session.missing_questions || []).length} pending</span>
              </div>
            </div>
          </Card>

          {/* Help Card */}
          <Card className="p-4 bg-slate-50">
            <h4 className="text-sm font-medium text-slate-700 mb-2">How it works</h4>
            <ol className="text-xs text-slate-600 space-y-2 list-decimal list-inside">
              <li>Upload your product documents</li>
              <li>AI analyzes and extracts info</li>
              <li>Answer missing questions</li>
              <li>Get your Stitch prompt</li>
            </ol>
          </Card>
        </div>
      </aside>
    </div>
  );
}
