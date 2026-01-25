import React from 'react';
import { X, Loader2 } from 'lucide-react';

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
    if (e.key === 'Enter' && !isUploading) {
      onConfirm();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full border border-purple-500/20">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Name Your Document</h3>
            {!isUploading && (
              <button
                onClick={onCancel}
                className="text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
          
          {isUploading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-16 h-16 text-purple-400 animate-spin mb-4" />
              <p className="text-white text-lg font-medium">Uploading...</p>
              <p className="text-slate-400 text-sm mt-2">Magic takes time ✨. Please wait while we process your document. This usually takes upto 5-10 mins.</p>
            </div>
          ) : (
            <>
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
                  disabled={!paperName.trim()}
                  className="flex-1 bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-medium transition-all"
                >
                  Confirm
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}