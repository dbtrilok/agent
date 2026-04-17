import re

with open("app/page.tsx", "r") as f:
    text = f.read()

# 1. Add fields to ProjectManifest interface
old_interface = """interface ProjectManifest {
  app_name?: string;
  app_type?: string;
  target_audience?: string;
  platform?: string;
  primary_color?: string;
  ui_style?: string;
  navigation_pattern?: string;
  primary_user_goal?: string;
  conversion_focus?: boolean;
  inspiration_apps?: string[];
  features: string[];
  user_flows: string[];
}"""

new_interface = """interface ProjectManifest {
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
}"""

text = text.replace(old_interface, new_interface)

# 2. Update Manifest Rendering in Sidebar
old_sidebar_manifest = """            <>
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
            {(session.missing_questions || []).length === 0 ? ("""

new_sidebar_manifest = """            <>
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
          <div className="flex-1 overflow-y-auto p-2 space-y-1 mt-2 mb-2">
            
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mb-2">Base Details</h4>
            <ManifestItem label="App Name" value={session.manifest.app_name} isComplete={!!session.manifest.app_name} />
            <ManifestItem label="App Type" value={session.manifest.app_type} isComplete={!!session.manifest.app_type} />
            <ManifestItem label="Platform" value={session.manifest.platform} isComplete={!!session.manifest.platform} />
            
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mt-4 mb-2">Tech Specs</h4>
            <ManifestItem label="Stack" value={session.manifest.tech_stack} isComplete={!!session.manifest.tech_stack} />
            <ManifestItem label="Components" value={session.manifest.component_library} isComplete={!!session.manifest.component_library} />
            <ManifestItem label="Icons" value={session.manifest.icon_set} isComplete={!!session.manifest.icon_set} />
            
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-3 mt-4 mb-2">Design</h4>
            <ManifestItem label="Brand Color" value={session.manifest.primary_color} isComplete={!!session.manifest.primary_color} />
            <ManifestItem label="UI Style" value={session.manifest.ui_style} isComplete={!!session.manifest.ui_style} />
            
            <div className="my-4 border-t border-slate-200" />

            {(session.missing_questions || []).length === 0 ? ("""

text = text.replace(old_sidebar_manifest, new_sidebar_manifest)

# 3. Remove API Key and Provider UI
# Provider selection block
import re

text = re.sub(
    r'\{\/\* Provider Selection \*\/\}.*?\{\/\* Object \*\/\}.*?(?=\{\/\* File Drop Zone \*\/\})',
    '',
    text,
    flags=re.DOTALL
)

# wait regex could fail, let's just do explicit string splits mapping out exactly the block between <p className="text-slate-600 mb-6">...</p> and {/* File Drop Zone */}

old_intro_to_drop = """                </p>

                {/* Provider Selection */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Select AI Provider
                  </label>
                  <select
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value as Provider)}
                    className="w-full px-4 py-3 rounded-lg border border-slate-300 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/20 transition-all"
                  >
                    {providers.map((provider) => (
                      <option key={provider.id} value={provider.id} disabled={!provider.configured}>
                        {provider.name} {!provider.configured && "(Not Configured)"}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-slate-500 mt-1">
                    {providers.find(p => p.id === selectedProvider)?.description}
                  </p>
                </div>

                {/* API Key Configuration */}
                <div className="mb-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <details className="text-sm">
                    <summary className="font-medium text-slate-700 cursor-pointer hover:text-slate-900">
                      Configure API Keys (Optional)
                    </summary>
                    <div className="mt-3 space-y-3">
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-1">Gemini API Key</label>
                        <input
                          type="password"
                          placeholder="Enter Gemini API key"
                          value={apiKeys.gemini}
                          onChange={(e) => setApiKeys(prev => ({ ...prev, gemini: e.target.value }))}
                          className="w-full px-3 py-2 rounded border border-slate-300 text-xs"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-1">OpenAI API Key</label>
                        <input
                          type="password"
                          placeholder="Enter OpenAI API key"
                          value={apiKeys.openai}
                          onChange={(e) => setApiKeys(prev => ({ ...prev, openai: e.target.value }))}
                          className="w-full px-3 py-2 rounded border border-slate-300 text-xs"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-1">Kimi API Key</label>
                        <input
                          type="password"
                          placeholder="Enter Kimi API key"
                          value={apiKeys.kimi}
                          onChange={(e) => setApiKeys(prev => ({ ...prev, kimi: e.target.value }))}
                          className="w-full px-3 py-2 rounded border border-slate-300 text-xs"
                        />
                      </div>
                      <p className="text-xs text-slate-500">
                        Keys are stored locally in browser memory. Configure keys in backend environment for production use.
                      </p>
                    </div>
                  </details>
                </div>

                {/* File Drop Zone */}"""

new_intro_to_drop = """                </p>

                {/* File Drop Zone */}"""

text = text.replace(old_intro_to_drop, new_intro_to_drop)

# Hardcode provider to ollama on submit
text = text.replace('provider: selectedProvider', 'provider: "ollama"')

with open("app/page.tsx", "w") as f:
    f.write(text)

