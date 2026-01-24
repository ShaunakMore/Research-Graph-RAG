import React from 'react';
import { X } from 'lucide-react';

export default function NamePromptModal({ 
  show, 
  pendingFile, 
  paperName, 
  setPaperName, 
  onConfirm, 
  onCancel, 
  isUploading 
}) {
  if (!show) return null;

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onConfirm();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full border border-purple-500/20">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Name Your Document</h3>
            <button
              onClick={onCancel}
              className="text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="mb-4">
            <p className="text-slate-300 text-sm mb-3">
              File: <span className="text-purple-400 font-medium">{pendingFile?.name}</span>
            </p>
            
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 mb-4">
              <p className="text-blue-300 text-sm">
                💡 <strong>Note:</strong> Please assign a simple and memorable name. Use only lowercase letters, numbers, and underscores. This paper will be referred to using this name only in future conversations.
              </p>
            </div>

            <label className="block text-slate-300 text-sm font-medium mb-2">
              Paper Name
            </label>
            <input
              type="text"
              value={paperName}
              onChange={(e) => setPaperName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., transformer_paper, covid_study"
              className="w-full bg-slate-700 border border-purple-500/20 text-white placeholder-slate-400 rounded-lg px-4 py-3 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20"
              autoFocus
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 bg-slate-700 hover:bg-slate-600 text-white py-3 px-4 rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              disabled={!paperName.trim() || isUploading}
              className="flex-1 bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-medium transition-all"
            >
              {isUploading ? 'Uploading...' : 'Confirm'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}