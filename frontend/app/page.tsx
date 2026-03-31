import HexGrid from "../components/HexGrid";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-[#0b0f0e] text-white overflow-hidden">

      {/* ✅ BACKGROUND (HEX GRID — TRUE BACKGROUND) */}
      <HexGrid />

      {/* ✅ NAVBAR */}
      <div className="relative z-10 w-full border-b border-zinc-800 px-8 py-5 flex items-center justify-between">
        <h1 className="text-lg font-semibold tracking-tight">
          Zero AI
        </h1>

        <div className="text-sm text-zinc-400">
          Agentic Code Analyzer
        </div>
      </div>

      {/* ✅ MAIN CONTENT */}
      <div className="relative z-10 flex justify-center items-center px-6 py-24">
        <div className="w-full max-w-4xl text-center">

          {/* HEADING */}
          <h1 className="text-5xl md:text-6xl font-semibold leading-tight tracking-tight">
            Understand any codebase
            <br />
            with AI-powered analysis
          </h1>

          {/* SUBTEXT */}
          <p className="mt-6 text-zinc-400 text-lg max-w-2xl mx-auto">
            Paste a GitHub repository and get structured insights,
            issues, and fixes instantly.
          </p>

          {/* INPUT */}
          <div className="mt-12 flex items-center bg-zinc-900/80 border border-zinc-700 rounded-xl px-4 py-3 shadow-xl backdrop-blur-xl max-w-2xl mx-auto">

            <input
              placeholder="https://github.com/user/repo"
              className="flex-1 bg-transparent outline-none text-sm text-white placeholder:text-zinc-500"
            />

            <button className="ml-3 px-5 py-2 rounded-lg bg-emerald-500 text-black text-sm font-medium hover:bg-emerald-400 transition">
              Analyze
            </button>

          </div>

          {/* RESULTS */}
          <div className="mt-16 space-y-6 text-left max-w-2xl mx-auto">

            <div className="border border-zinc-700 bg-zinc-900/60 backdrop-blur rounded-xl p-6 hover:border-emerald-400/50 transition">
              <h3 className="text-sm text-emerald-400 mb-3">Issues</h3>
              <p className="text-zinc-300 text-sm leading-relaxed">
                Potential null pointer dereference detected in authentication module.
                Input validation is missing before accessing user object.
              </p>
            </div>

            <div className="border border-zinc-700 bg-zinc-900/60 backdrop-blur rounded-xl p-6 hover:border-emerald-400/50 transition">
              <h3 className="text-sm text-emerald-400 mb-3">Fix</h3>
              <p className="text-zinc-300 text-sm leading-relaxed">
                Add proper null checks before accessing user properties. Implement input validation
                middleware to ensure safe execution.
              </p>
            </div>

            <div className="border border-zinc-700 bg-zinc-900/60 backdrop-blur rounded-xl p-6 hover:border-emerald-400/50 transition">
              <h3 className="text-sm text-emerald-400 mb-3">Explanation</h3>
              <p className="text-zinc-300 text-sm leading-relaxed">
                The issue occurs because the application assumes that user data is always present.
                In real-world scenarios, missing or malformed inputs can lead to runtime crashes.
              </p>
            </div>

          </div>

        </div>
      </div>

    </main>
  );
}