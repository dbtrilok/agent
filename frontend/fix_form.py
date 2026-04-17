with open("app/page.tsx", "r") as f:
    text = f.read()

# Add field to Question interface
text = text.replace("id: string;", "id?: string;\n  field?: string;")

# Fix QuestionForm map
old_form = """      {questions.map((q, idx) => (
        <div key={q.id || q.field || idx} className="bg-slate-50 p-4 rounded-lg border border-slate-200">"""

new_form = """      {questions.map((q, idx) => {
        const fieldKey = (q.field || q.id || idx.toString()) as string;
        return (
        <div key={fieldKey} className="bg-slate-50 p-4 rounded-lg border border-slate-200">"""

text = text.replace(old_form, new_form)

# Now fix answers[q.id] -> answers[fieldKey] in the return block
old_body = """            <span className="bg-slate-900 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0">
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
              value={answers[q.id] || ""}
              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
              placeholder="Type your answer..."
            />
          )}

          {q.type === "color" && (
            <div className="flex items-center gap-3">
              <input
                type="color"
                value={answers[q.id] || "#6366F1"}
                onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                className="w-12 h-10 rounded cursor-pointer"
              />
              <input
                type="text"
                value={answers[q.id] || ""}
                onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
                className="flex-1 px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900"
                placeholder="#6366F1"
              />
            </div>
          )}

          {q.type === "select" && q.options && (
            <select
              value={answers[q.id] || ""}
              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
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
                  name={q.id}
                  checked={answers[q.id] === true}
                  onChange={() => setAnswers({ ...answers, [q.id]: true })}
                  className="w-4 h-4 text-slate-900"
                />
                <span>Yes</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={q.id}
                  checked={answers[q.id] === false}
                  onChange={() => setAnswers({ ...answers, [q.id]: false })}
                  className="w-4 h-4 text-slate-900"
                />
                <span>No</span>
              </label>
            </div>
          )}
        </div>
      ))}"""

new_body = old_body.replace("q.id", "fieldKey").replace("}))}", "});\n      })}").replace("</div>\n      ))}", "</div>\n        );\n      })}")

text = text.replace(old_body, new_body)

with open("app/page.tsx", "w") as f:
    f.write(text)
