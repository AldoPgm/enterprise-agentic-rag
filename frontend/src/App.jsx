import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, MagnifyingGlass, Sparkle, ChatCircleText, GitBranch, ArrowRight, SpinnerGap, WarningCircle } from '@phosphor-icons/react';

// Falsa API URL
const API_URL = "http://127.0.0.1:8000/chat";

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: "init_1",
      role: "ai",
      content: "Engine initialized. Neural pathways active.",
      sources: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const [threadId] = useState(() => `session_${Math.random().toString(36).substring(7)}_${Date.now()}`);

  const bottomRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!inputValue.trim()) return;

    const newMsgObj = {
      id: `user_${Date.now()}`,
      role: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };

    setMessages(prev => [...prev, newMsgObj]);
    setInputValue("");
    setIsTyping(true);
    setConnectionError(false);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: newMsgObj.content,
          thread_id: threadId
        })
      });
      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [...prev, {
          id: `ai_${Date.now()}`,
          role: "ai",
          content: data.response,
          sources: data.sources || [],
          usedWebSearch: data.used_web_search || false,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        }]);
      } else {
        throw new Error(data.detail || "Server fault.");
      }
    } catch (err) {
      setConnectionError(true);
      setMessages(prev => [...prev, {
        id: `sys_error_${Date.now()}`,
        role: "system",
        content: "CRITICAL: Connection to LangGraph Nexus failed. Ensure Python backend is active.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-[100dvh] w-full flex items-center justify-center p-4 md:p-8 bg-zinc-950 font-sans text-zinc-100 relative overflow-hidden">
      {/* Background Particles/Noise Filter */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-20" style={{ backgroundImage: "url('data:image/svg+xml,%3Csvg viewBox=\"0 0 200 200\" xmlns=\"http://www.w3.org/2000/svg\"%3E%3Cfilter id=\"noiseFilter\"%3E%3CfeTurbulence type=\"fractalNoise\" baseFrequency=\"0.65\" numOctaves=\"3\" stitchTiles=\"stitch\"/%3E%3C/filter%3E%3Crect width=\"100%25\" height=\"100%25\" filter=\"url(%23noiseFilter)\"/%3E%3C/svg%3E')" }}></div>

      {/* Dynamic Refraction Orb (Perpetual Micro-Interaction) */}
      <motion.div
        animate={{
          rotate: 360,
          scale: [1, 1.05, 1],
          opacity: [0.1, 0.15, 0.1]
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="fixed top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-emerald-600/20 blur-[120px] pointer-events-none z-0"
      />

      <div className="w-full max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-[3fr_7fr] gap-6 md:gap-8 z-10 relative">

        {/* SIDEBAR BENTO (Asymmetric Structure) */}
        <div className="flex flex-col gap-6">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 100, damping: 20 }}
            className="glass-panel rounded-[2rem] p-8 flex flex-col gap-8"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center relative shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]">
                <Sparkle weight="fill" className="text-emerald-500 w-5 h-5" />
                <motion.div
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="absolute inset-0 rounded-full border border-emerald-500/30"
                />
              </div>
              <div className="flex flex-col">
                <h1 className="text-xl font-semibold tracking-tight leading-none text-zinc-50">Firma Legal - Corp</h1>
                <span className="text-xs text-zinc-500 font-mono mt-1 mt-1">LEGAL_NEXUS_v1.0</span>
              </div>
            </div>

            <div className="border-t border-zinc-800/50 pt-6">
              <span className="text-[10px] font-mono tracking-widest text-zinc-500 uppercase mb-4 block">Engine Status</span>

              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between group cursor-default">
                  <div className="flex items-center gap-3 text-sm text-zinc-300">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 3, repeat: Infinity }}
                      className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"
                    />
                    <span>Vector DB (Pinecone)</span>
                  </div>
                  <span className="font-mono text-xs text-emerald-500 opacity-0 group-hover:opacity-100 transition-opacity">ONLINE</span>
                </div>
              </div>
            </div>

            <div className="border-t border-zinc-800/50 pt-6 mt-auto">
              <span className="text-[10px] font-mono tracking-widest text-zinc-500 uppercase mb-4 block">Base Jurisprudencial</span>
              <div className="glass-input rounded-xl p-3 flex items-center gap-3 mb-8">
                <FileText className="text-zinc-500" />
                <span className="text-sm font-medium text-zinc-300 truncate">codigo_civil_ejemplo.txt</span>
              </div>

              <div className="flex flex-col items-center justify-center gap-1 opacity-60 hover:opacity-100 transition-opacity cursor-default">
                <span className="text-[9px] font-mono tracking-widest text-zinc-500 uppercase">Powered by</span>
                <span className="text-sm font-bold tracking-widest text-emerald-500 uppercase flex items-center gap-2">
                  AGENTEER
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* MAIN CHAT BENTO */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 100, damping: 20, delay: 0.1 }}
          className="glass-panel rounded-[2.5rem] p-2 flex flex-col h-[85vh] md:h-[90vh] diffusion-shadow"
        >
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto hide-scrollbar p-6 md:p-10 flex flex-col gap-8">
            <AnimatePresence>
              {messages.map((m, idx) => (
                <motion.div
                  key={m.id}
                  initial={{ opacity: 0, y: 10, filter: "blur(4px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  layout
                  className={`flex flex-col max-w-[85%] ${m.role === 'user' ? 'self-end' : 'self-start'}`}
                >
                  <div className="flex items-center gap-2 mb-2 px-1">
                    {m.role === 'ai' ? <GitBranch weight="bold" className="text-emerald-500 w-3 h-3" /> : null}
                    {m.role === 'system' ? <WarningCircle weight="bold" className="text-red-500 w-3 h-3" /> : null}
                    <span className="font-mono text-[10px] text-zinc-500 uppercase tracking-widest">
                      {m.role === 'user' ? 'GUEST_USER' : m.role === 'system' ? 'SYSTEM_ALERT' : 'AGENT_CORE'} • {m.timestamp}
                    </span>
                  </div>

                  <div className={`
                    p-5 rounded-2xl text-[15px] leading-relaxed
                    ${m.role === 'user' ? 'bg-zinc-800/80 text-zinc-100 border border-zinc-700/50 rounded-tr-sm' : ''}
                    ${m.role === 'ai' ? 'glass-input !bg-zinc-900/50 text-zinc-300 rounded-tl-sm' : ''}
                    ${m.role === 'system' ? 'border border-red-900/50 bg-red-950/20 text-red-200 rounded-tl-sm' : ''}
                  `}>
                    <div dangerouslySetInnerHTML={{ __html: m.content.replace(/\*\*(.*?)\*\*/g, '<strong class="text-zinc-100 font-medium">$1</strong>').replace(/\n/g, '<br/>') }} />
                  </div>

                  {m.sources && m.sources.length > 0 && (
                    <div className="flex gap-2 mt-3 flex-wrap">
                      {m.sources.map((src, i) => (
                        <div key={i} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono border ${src.includes('Tavily') || m.usedWebSearch ? 'bg-emerald-950/30 text-emerald-400 border-emerald-900/50' : 'bg-zinc-900 border-zinc-800 text-zinc-400'}`}>
                          {src.includes('Tavily') || m.usedWebSearch ? <MagnifyingGlass /> : <FileText />}
                          {src}
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {isTyping && (
              <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="self-start flex flex-col gap-2"
              >
                <span className="font-mono text-[10px] text-zinc-500 uppercase tracking-widest px-1">AGENT_CORE • PROCESSING</span>
                <div className="glass-input !bg-zinc-900/50 p-4 rounded-2xl rounded-tl-sm flex items-center gap-3 w-fit">
                  <SpinnerGap className="w-5 h-5 text-emerald-500 animate-spin" />
                  <span className="text-sm font-mono text-zinc-400">Synthesizing parameters...</span>
                </div>
              </motion.div>
            )}
            <div ref={bottomRef} className="h-1 text-transparent" />
          </div>

          {/* Input Interface */}
          <div className="p-4 md:p-6 pb-4 border-t border-zinc-800/50">
            {connectionError && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-red-400 mb-3 ml-2 flex items-center gap-1.5">
                <WarningCircle /> Backend connection refused.
              </motion.p>
            )}
            <form onSubmit={handleSubmit} className="relative group">
              <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                <ChatCircleText className="w-5 h-5 text-zinc-500 group-focus-within:text-emerald-500 transition-colors" />
              </div>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Inicia consulta legal (Ej. Resolución de contratos)..."
                className="w-full glass-input rounded-2xl py-5 pl-12 pr-16 text-[15px] shadow-lg text-zinc-100 placeholder:text-zinc-600 focus:bg-zinc-900/80"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isTyping}
                className="absolute inset-y-2 right-2 px-4 bg-zinc-100 text-zinc-900 hover:bg-white disabled:opacity-50 disabled:hover:bg-zinc-100 rounded-xl font-medium transition-all hover:scale-[0.98] active:scale-95 flex items-center gap-2"
              >
                <span className="hidden md:inline">Execute</span>
                <ArrowRight weight="bold" className="w-4 h-4" />
              </button>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
