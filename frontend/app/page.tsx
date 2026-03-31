'use client';
import React, { useState, useEffect, useRef } from "react";
import HexGrid from "../components/HexGrid";

export default function Home() {
  const [particles, setParticles] = useState<
    { id: number; top: number; left: number; duration: number; dx: number; dy: number; size: number; opacity: number }[]
  >([]);
  useEffect(() => {
    const generated = Array.from({ length: 18 }).map((_, i) => ({
      id: i,
      top: Math.random() * 100,
      left: Math.random() * 100,
      duration: 12 + Math.random() * 8,
      dx: (Math.random() - 0.5) * 16,
      dy: (Math.random() - 0.5) * 16,
      size: Math.random() < 0.5 ? 1 : 2,
      opacity: 0.08 + Math.random() * 0.08,
    }));
    setParticles(generated);
  }, []);
  
  const staticLine = "Understand any codebase";
  const typingLine = "AI-powered analysis";
  const [typedText, setTypedText] = useState("");
  const [typedDone, setTypedDone] = useState(false);
  const [showHeadingCursor, setShowHeadingCursor] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const [inputFocused, setInputFocused] = useState(false);
  const [loading, setLoading] = useState(false);
  const steps = [
    "Analyzing repository...",
    "Parsing files",
    "Understanding architecture",
    "Detecting issues",
    "Generating fixes",
  ];
  const [stepIndex, setStepIndex] = useState(0);
  useEffect(() => {
    let i = 0;
    const interval = window.setInterval(() => {
      i++;
      setTypedText(typingLine.slice(0, i));
      setShowHeadingCursor(true);
      if (i >= typingLine.length) {
        window.clearInterval(interval);
        setTypedDone(true);
      }
    }, 50 + Math.random() * 30);
    return () => window.clearInterval(interval);
  }, []);
  useEffect(() => {
    if (typedDone) {
      const t = window.setTimeout(() => {
        setShowHeadingCursor(false);
        inputRef.current?.focus();
      }, 800);
      return () => window.clearTimeout(t);
    }
  }, [typedDone]);
  useEffect(() => {
    if (!loading) return;
    setStepIndex(0);
    const interval = window.setInterval(() => {
      setStepIndex((prev) => prev + 1);
    }, 800);
    return () => window.clearInterval(interval);
  }, [loading]);
  useEffect(() => {
    if (loading && stepIndex >= steps.length) {
      setLoading(false);
    }
  }, [loading, stepIndex]);
  
  const [parallax, setParallax] = useState({ x: 0, y: 0 });
  const handleMouseMove = (e: React.MouseEvent) => {
    const { clientX, clientY, currentTarget } = e;
    const rect = (currentTarget as HTMLElement).getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const dx = ((clientX - centerX) / rect.width) * 16;
    const dy = ((clientY - centerY) / rect.height) * 16;
    setParallax({
      x: Math.max(-10, Math.min(10, dx)),
      y: Math.max(-10, Math.min(10, dy)),
    });
  };
  return (
    <main className="relative min-h-screen bg-[#0b0f0e] text-white overflow-hidden" onMouseMove={handleMouseMove}>

      {/* ✅ BACKGROUND (HEX GRID — TRUE BACKGROUND) */}
      <HexGrid offsetX={parallax.x} offsetY={parallax.y} />
      {/* Vignette overlay */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(1200px 600px at 50% 45%, rgba(255,255,255,0.04) 0%, rgba(0,0,0,0) 60%)",
          }}
        />
        {particles.map((p) => (
          <div
            key={`p-${p.id}`}
            className="absolute rounded-full"
            style={{
              top: `${p.top}%`,
              left: `${p.left}%`,
              width: p.size,
              height: p.size,
              opacity: p.opacity,
              backgroundColor: "rgba(255,255,255,0.6)",
              animation: `particle-${p.id} ${p.duration}s ease-in-out infinite alternate`,
            }}
          />
        ))}
        <style jsx>{`
          ${particles
            .map(
              (p) => `
            @keyframes particle-${p.id} {
              from { transform: translate(0px, 0px); }
              to { transform: translate(${p.dx}px, ${p.dy}px); }
            }
          `
            )
            .join("\n")}
          @keyframes blink {
            0%, 50%, 100% { opacity: 1; }
            25%, 75% { opacity: 0; }
          }
        `}</style>
      </div>

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
        <div className="w-full max-w-4xl text-center relative">

          {/* HEADING */}
          <div className="relative inline-block">
            <div
              className="absolute -z-10 pointer-events-none left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              style={{
                width: 700,
                height: 700,
                background:
                  "radial-gradient(circle at center, rgba(16,185,129,0.10) 0%, rgba(16,185,129,0.0) 55%)",
                filter: "blur(220px)",
              }}
            />
            <h1 className="text-5xl md:text-6xl font-semibold leading-tight tracking-tight text-white">
              Understand any codebase
              <br />
              <span className="text-white/70">with</span>{" "}
              <span className="inline-flex items-baseline text-emerald-400 drop-shadow-[0_0_6px_rgba(16,185,129,0.35)]">
                {typedText}
                {showHeadingCursor && typedText.length > 0 && (
                  <span className="w-[1.5px] h-[1em] bg-emerald-200/80 ml-[2px] rounded animate-[blink_1.2s_ease-in-out_infinite]" />
                )}
              </span>
            </h1>
          </div>

          {/* SUBTEXT */}
          <p className="mt-6 text-zinc-400 text-lg max-w-2xl mx-auto">
            Paste a GitHub repository and get structured insights,
            issues, and fixes instantly.
          </p>

          {/* INPUT */}
          <div className="mt-12 group flex items-center bg-zinc-900/80 border border-zinc-700 focus-within:border-emerald-500/40 rounded-xl px-4 py-3 shadow-inner shadow-xl backdrop-blur-xl max-w-2xl mx-auto transition-all duration-200 transform hover:scale-[1.02]"
            style={{
              boxShadow:
                "inset 0 1px 8px rgba(0,0,0,0.35), 0 0 0 0px rgba(16,185,129,0), 0 20px 40px rgba(0,0,0,0.35)",
            }}
            onFocus={(e) => {
              (e.currentTarget.style.boxShadow =
                "inset 0 1px 8px rgba(0,0,0,0.25), 0 0 0 3px rgba(16,185,129,0.20), 0 18px 36px rgba(0,0,0,0.30)");
              (e.currentTarget.style.backgroundColor = "rgba(24,24,24,0.85)");
            }}
            onBlur={(e) => {
              (e.currentTarget.style.boxShadow =
                "inset 0 1px 8px rgba(0,0,0,0.35), 0 0 0 0px rgba(16,185,129,0), 0 20px 40px rgba(0,0,0,0.35)");
              (e.currentTarget.style.backgroundColor = "");
            }}
          >

            <span className="mr-3 text-emerald-400 font-mono text-lg">{">"}</span>
            <input
              ref={inputRef}
              placeholder="https://github.com/user/repo"
              className={`flex-1 bg-transparent outline-none text-sm text-white caret-emerald-400 ${inputFocused ? 'placeholder:text-zinc-400' : 'placeholder:text-zinc-500'}`}
              onFocus={() => setInputFocused(true)}
              onBlur={() => setInputFocused(false)}
            />

            <button
              className="ml-3 px-5 py-2 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-400 text-black text-sm font-medium transition-all hover:shadow-[0_0_22px_rgba(16,185,129,0.35)] active:scale-95"
              disabled={loading}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = "0 0 24px rgba(16,185,129,0.35)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = "0 6px 18px rgba(0,0,0,0.25)";
              }}
              onMouseDown={(e) => {
                e.currentTarget.style.transform = "scale(0.96)";
              }}
              onMouseUp={(e) => {
                e.currentTarget.style.transform = "scale(1)";
              }}
              onClick={() => {
                setLoading(true);
                setStepIndex(0);
              }}
              style={{ boxShadow: "0 6px 18px rgba(0,0,0,0.25)" }}
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>

          </div>

          {/* RESULTS */}
          {loading ? (
            <div className="mt-16 max-w-2xl mx-auto">
              <div className="border border-zinc-700 bg-zinc-900/60 backdrop-blur rounded-xl p-6 animate-pulse">
                <div className="w-full h-1 bg-zinc-800 rounded-full overflow-hidden mb-4">
                  <div
                    className="h-full bg-emerald-500 transition-all duration-500"
                    style={{ width: `${Math.min((stepIndex / steps.length) * 100, 100)}%` }}
                  />
                </div>
                <div className="text-xs text-emerald-400 font-mono mb-3">
                  {`> ${steps[Math.min(stepIndex, steps.length - 1)]}`}
                  <span className="animate-pulse ml-1">_</span>
                </div>
                <ul className="space-y-3">
                  {steps.map((label, idx) => {
                    const isActive = idx === stepIndex && stepIndex < steps.length;
                    const isCompleted = idx < stepIndex;
                    const cls = isActive
                      ? "text-emerald-400"
                      : isCompleted
                      ? "text-emerald-300"
                      : "text-zinc-500";
                    return (
                      <li
                        key={label}
                        className={`flex items-center ${cls} transition-all duration-300 ${isActive ? "scale-105 drop-shadow-[0_0_8px_rgba(16,185,129,0.35)]" : ""}`}
                      >
                        <span className={`mr-2 text-xs ${isActive ? "animate-pulse" : ""}`}>●</span>
                        <span className="text-sm">
                          {label}
                          {isActive && <span className="animate-pulse ml-1">...</span>}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          ) : (
            <div className="mt-16 space-y-6 text-left max-w-2xl mx-auto">
            {[
              {
                title: "Issues",
                content:
                  "Potential null pointer dereference detected in authentication module. Input validation is missing before accessing user object.",
              },
              {
                title: "Fix",
                content:
                  "Add proper null checks before accessing user properties. Implement input validation middleware to ensure safe execution.",
              },
              {
                title: "Explanation",
                content:
                  "The issue occurs because the application assumes that user data is always present. In real-world scenarios, missing or malformed inputs can lead to runtime crashes.",
              },
            ].map((card, idx) => (
              <div
                key={card.title}
                className="relative border border-zinc-700 bg-zinc-900/60 backdrop-blur rounded-xl p-6 hover:border-emerald-400/50 transition transform hover:scale-[1.01]"
                style={{
                  opacity: 0,
                  transform: "translateY(8px)",
                  transition: "opacity 600ms ease, transform 600ms ease",
                  transitionDelay: `${idx * 100}ms`,
                }}
                onAnimationStart={(e) => {
                  // no-op
                }}
                onMouseEnter={(e) => {
                  // keep premium feel
                }}
                ref={(el) => {
                  if (el) {
                    requestAnimationFrame(() => {
                      el.style.opacity = "1";
                      el.style.transform = "translateY(0)";
                    });
                  }
                }}
              >
                <span className="absolute -top-2 -left-2 text-[10px] px-2 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold tracking-widest">
                  AI
                </span>
                <h3 className="text-sm text-emerald-400 mb-4">{card.title}</h3>
                <p className="text-zinc-300 text-sm leading-relaxed">
                  {card.content}
                </p>
              </div>
            ))}
            </div>
          )}

        </div>
      </div>

    </main>
  );
}
