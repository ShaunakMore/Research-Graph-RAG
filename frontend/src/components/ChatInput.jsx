import React from 'react';
import { Send } from 'lucide-react';

export default function ChatInput({ inputMessage, setInputMessage, onSendMessage }) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  return (
    <div className="p-6 bg-slate-800/30 backdrop-blur-xl border-t border-purple-500/20">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask anything about your documents..."
            className="flex-1 bg-slate-700/50 border border-purple-500/20 text-white placeholder-slate-400 rounded-xl px-5 py-3 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20"
          />
          <button
            onClick={onSendMessage}
            disabled={!inputMessage.trim()}
            className="bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all shadow-lg shadow-purple-500/25"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}