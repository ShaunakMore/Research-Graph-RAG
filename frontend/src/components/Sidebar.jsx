import React, { useRef } from 'react';
import { Upload, FileText } from 'lucide-react';

export default function Sidebar({ uploadedPapers, onFileSelect }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    onFileSelect(file);
    e.target.value = null;
  };

  return (
    <div className="w-72 bg-slate-800/50 backdrop-blur-xl border-r border-purple-500/20 flex flex-col">
      <div className="p-6 border-b border-purple-500/20">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <FileText className="w-5 h-5 text-purple-400" />
          Uploaded Papers
        </h2>
        <p className="text-sm text-slate-400 mt-1">{uploadedPapers.length} documents</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {uploadedPapers.length === 0 ? (
          <div className="text-center text-slate-500 mt-8">
            <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No papers uploaded yet</p>
          </div>
        ) : (
          uploadedPapers.map((paper) => (
            <div
              key={paper.id}
              className="bg-slate-700/50 rounded-lg p-3 border border-purple-500/10 hover:border-purple-500/30 transition-colors"
            >
              <div className="flex items-start gap-2">
                <FileText className="w-4 h-4 text-purple-400 mt-1 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium text-sm truncate">{paper.name}</p>
                  <p className="text-slate-400 text-xs truncate mt-0.5">{paper.fileName}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="p-4 border-t border-purple-500/20">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 px-4 rounded-lg font-medium flex items-center justify-center gap-2 transition-all shadow-lg shadow-purple-500/25"
        >
          <Upload className="w-4 h-4" />
          Upload PDF
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
    </div>
  );
}