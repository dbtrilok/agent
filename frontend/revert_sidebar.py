with open("app/page.tsx", "r") as f:
    text = f.read()

bad_sidebar = """        {session.session_id ? (
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

good_sidebar = """        {session.session_id ? (
          <div className="flex-1 overflow-y-auto p-2">
            {(session.missing_questions || []).length === 0 ? ("""

text = text.replace(bad_sidebar, good_sidebar)

with open("app/page.tsx", "w") as f:
    f.write(text)
