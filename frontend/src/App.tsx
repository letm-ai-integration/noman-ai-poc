import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Settings, History, Cpu, Binary, LayoutGrid, Trash2, RefreshCcw } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Message {
  role: 'user' | 'bot';
  content: string;
  tokens?: number;
  id: string;
}

interface Role {
  [key: string]: string;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [roles, setRoles] = useState<Role>({});
  const [selectedRole, setSelectedRole] = useState('qa');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'chat' | 'history' | 'tokens' | 'embeddings'>('chat');
  
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchRoles();
    fetchHistory();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchRoles = async () => {
    try {
      const res = await axios.get('/api/roles');
      setRoles(res.data);
    } catch (e) {
      console.error("Failed to fetch roles", e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get('/api/history');
      const history = res.data.flatMap((item: any, idx: number) => [
        { role: 'user', content: item.question, id: `q-${idx}` },
        { role: 'bot', content: item.answer, id: `a-${idx}` }
      ]);
      setMessages(history);
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: 'user', content: input, id: Date.now().toString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await axios.post('/api/chat', {
        question: input,
        role: selectedRole,
        temperature,
        max_tokens: maxTokens
      });

      const botMsg: Message = { 
        role: 'bot', 
        content: res.data.response, 
        tokens: res.data.response_token_count,
        id: (Date.now() + 1).toString() 
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (e) {
      const errorMsg: Message = { 
        role: 'bot', 
        content: "Error: Failed to get response from the model.", 
        id: (Date.now() + 1).toString() 
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      await axios.delete('/api/history');
      setMessages([]);
    } catch (e) {
      console.error("Failed to clear history", e);
    }
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-200 overflow-hidden font-sans">
      {/* Sidebar */}
      <div className="w-64 border-r border-slate-800 bg-[#1e293b] flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold flex items-center gap-2 text-indigo-400">
            <Cpu size={24} /> LLM QnA Bot
          </h1>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <button 
            onClick={() => setActiveTab('chat')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              activeTab === 'chat' ? "bg-indigo-600 text-white" : "hover:bg-slate-800 text-slate-400"
            )}
          >
            <Send size={18} /> Chat
          </button>
          <button 
             onClick={() => setActiveTab('history')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              activeTab === 'history' ? "bg-indigo-600 text-white" : "hover:bg-slate-800 text-slate-400"
            )}
          >
            <History size={18} /> History
          </button>
          <div className="pt-4 pb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider px-4">
            Analysis
          </div>
          <button 
             onClick={() => setActiveTab('tokens')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              activeTab === 'tokens' ? "bg-indigo-600 text-white" : "hover:bg-slate-800 text-slate-400"
            )}
          >
            <Binary size={18} /> Tokens
          </button>
          <button 
             onClick={() => setActiveTab('embeddings')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
              activeTab === 'embeddings' ? "bg-indigo-600 text-white" : "hover:bg-slate-800 text-slate-400"
            )}
          >
            <LayoutGrid size={18} /> Embeddings
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button 
            onClick={clearHistory}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-900/20 text-red-400 transition-colors"
          >
            <Trash2 size={18} /> Clear Session
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative">
        {/* Header/Controls */}
        <header className="h-16 border-b border-slate-800 bg-[#0f172a] flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-6">
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 font-medium">ROLE</span>
              <select 
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="bg-transparent border-none focus:ring-0 text-indigo-400 font-semibold p-0 cursor-pointer uppercase text-sm"
              >
                {Object.keys(roles).map(role => (
                  <option key={role} value={role} className="bg-slate-900 text-slate-200">{role}</option>
                ))}
              </select>
            </div>
            
            <div className="h-8 w-px bg-slate-800" />
            
            <div className="flex flex-col">
              <span className="text-xs text-slate-500 font-medium">TEMP: {temperature}</span>
              <input 
                type="range" min="0.1" max="2.0" step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-24 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500 mt-2"
              />
            </div>

            <div className="flex flex-col ml-2">
              <span className="text-xs text-slate-500 font-medium">MAX TOKENS: {maxTokens}</span>
              <input 
                type="range" min="10" max="512" step="10"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                className="w-24 h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500 mt-2"
              />
            </div>
          </div>
          
          <button className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400">
            <Settings size={20} />
          </button>
        </header>

        {/* Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-8 space-y-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
                <Cpu size={64} className="opacity-20" />
                <p className="text-xl font-light">Ask me anything using the <b>{selectedRole}</b> role</p>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={cn(
                  "flex flex-col max-w-[80%]",
                  msg.role === 'user' ? "ml-auto items-end" : "mr-auto items-start"
                )}>
                  <div className={cn(
                    "px-4 py-3 rounded-2xl text-sm leading-relaxed",
                    msg.role === 'user' 
                      ? "bg-indigo-600 text-white rounded-tr-none" 
                      : "bg-[#1e293b] text-slate-200 border border-slate-800 rounded-tl-none"
                  )}>
                    {msg.content}
                  </div>
                  {msg.tokens && (
                    <span className="text-[10px] text-slate-500 mt-1 uppercase tracking-tighter">
                      {msg.tokens} tokens
                    </span>
                  )}
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex items-center gap-2 text-indigo-400 animate-pulse">
                <RefreshCcw size={16} className="animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-8 pt-0">
            <div className="relative max-w-4xl mx-auto">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Message the bot..."
                className="w-full bg-[#1e293b] border border-slate-800 rounded-2xl px-6 py-4 pr-16 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none transition-all placeholder:text-slate-600 h-16 min-h-[64px]"
              />
              <button 
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="absolute right-3 bottom-3 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 text-white rounded-xl transition-colors"
              >
                <Send size={20} />
              </button>
            </div>
            <p className="text-center text-[10px] text-slate-600 mt-4 uppercase tracking-[0.2em]">
              Powered by DistilGPT-2 & Transformers
            </p>
          </div>
        </main>
      </div>
      
      {/* Tailwind CSS injection since I can't use it directly via npm install with full config easily here */}
      <style>{`
        @import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');
        body { font-family: 'Inter', sans-serif; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
      `}</style>
    </div>
  );
}
