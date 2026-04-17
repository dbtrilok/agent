import re

with open("app/page.tsx", "r") as f:
    text = f.read()

# Add History Interface
interface_block = """interface HistoricalProject {
  session_id: string;
  name: string;
  status: string;
  updated_at: string;
}

const emptySessionState: SessionState = {"""

text = text.replace("const emptySessionState: SessionState = {", interface_block)

# Add Projects State
state_block = """  const [session, setSession] = useState<SessionState>(emptySessionState);
  const [projectsList, setProjectsList] = useState<HistoricalProject[]>([]);"""

text = text.replace("  const [session, setSession] = useState<SessionState>(emptySessionState);", state_block)

# Fetch projects list
fetch_providers = """  // Fetch providers on mount
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
  };"""

text = text.replace("""  // Fetch providers on mount
  useEffect(() => {
    fetch(`${API_BASE}/providers`)
      .then(res => res.json())
      .then(data => setProviders(data.providers))
      .catch(err => console.error("Failed to fetch providers:", err));
  }, []);""", fetch_providers)

# Update analyze document
analyze_fetch = """      // Trigger analysis
      const analysisResponse = await fetch(`${API_BASE}/sessions/${sessionData.session_id}/analyze`, {
        method: "POST",
      });
      const analysisData = await analysisResponse.json();

      // Update session with analysis results
      setSession(analysisData);
      setUploadedFiles([]);
      fetchProjects();"""

text = text.replace("""      // Trigger analysis
      const analysisResponse = await fetch(`${API_BASE}/sessions/${sessionData.session_id}/analyze`, {
        method: "POST",
      });
      const analysisData = await analysisResponse.json();

      // Update session with analysis results
      setSession(analysisData);
      setUploadedFiles([]);""", analyze_fetch)

# Sidebar HTML
old_sidebar_code = """        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center gap-2 mb-1">
            <Icons.Sparkles />
            <h1 className="font-bold text-lg text-slate-900">UX Architect</h1>
          </div>
          <p className="text-xs text-slate-500">Stitch Prompt Generator</p>
        </div>

        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-700">Project Manifest</span>
            {session.session_id ? (
              <Badge variant={session.completion_percentage === 100 ? "green" : "amber"}>
                {session.completion_percentage}%
              </Badge>
            ) : (
              <Badge variant="default">Not Started</Badge>
            )}
          </div>
          {session.session_id ? (
            <>
              <ProgressBar percentage={session.completion_percentage} />
              <p className="text-xs text-slate-500 mt-2">
                {session.completion_percentage === 100
                  ? "✅ Complete! Ready to generate."
                  : `⏸️ ${(session.missing_questions || []).length} questions need answers`}
              </p>
            </>
          ) : (
            <p className="text-xs text-slate-500 mt-2">
              Upload documents to start analysis
            </p>
          )}
        </div>

        {session.session_id ? (
          <div className="flex-1 overflow-y-auto p-2">
            {(session.missing_questions || []).length === 0 ? (
              <div className="text-center p-4">
                <Icons.Check />
                <p className="text-sm text-slate-600 mt-2">All information complete</p>
              </div>
            ) : (
              (session.missing_questions || []).map((question, idx) => (
                <div key={idx} className="mb-2 p-2 bg-amber-50 border border-amber-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Icons.Alert />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900">{question.question}</p>
                      {question.context && (
                        <p className="text-xs text-slate-500 mt-1">{question.context}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center p-4">
            <div className="text-center">
              <Icons.Upload />
              <p className="text-sm text-slate-500 mt-2">No project started</p>
              <p className="text-xs text-slate-400 mt-1">Upload documents to begin</p>
            </div>
          </div>
        )}

        <div className="p-4 border-t border-slate-200">
          <Button variant="outline" onClick={startNewSession} className="w-full justify-center">
            New Project
          </Button>
        </div>"""

new_sidebar_code = """        <div className="p-4 border-b border-slate-200 flex-shrink-0">
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
        </div>"""

text = text.replace(old_sidebar_code, new_sidebar_code)

with open("app/page.tsx", "w") as f:
    f.write(text)
