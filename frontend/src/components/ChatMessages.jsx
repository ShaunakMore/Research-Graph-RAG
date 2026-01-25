import React, { useRef, useEffect } from 'react';

export default function ChatMessages({ messages }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
        >
          {message.role === 'system' ? (
            <div className="bg-green-500/10 border border-green-500/20 text-green-400 px-4 py-3 rounded-lg text-sm max-w-2xl">
              {message.content}
            </div>
          ) : (
            <div
              className={`max-w-2xl ${
                message.role === 'user'
                  ? 'bg-linear-to-r from-purple-600 to-pink-600 text-white'
                  : 'bg-slate-700/50 text-slate-100 border border-purple-500/10'
              } rounded-2xl px-5 py-4 shadow-lg`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
            </div>
          )}
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}