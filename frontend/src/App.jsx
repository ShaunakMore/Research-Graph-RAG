import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import NamePromptModal from './components/NamePromptModal';
import { sendMessage, uploadPDF, fetchUploadedPapers } from './utils/api';
import { Sparkles } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! Upload PDFs to get started, then ask me anything about your documents.' }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [uploadedPapers, setUploadedPapers] = useState([]);
  const [showNamePrompt, setShowNamePrompt] = useState(false);
  const [pendingFile, setPendingFile] = useState(null);
  const [paperName, setPaperName] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  // Load existing papers on mount
  useEffect(() => {
    const loadPapers = async () => {
      const papers = await fetchUploadedPapers();
      setUploadedPapers(papers);
    };
    loadPapers();
  }, []);

  const handleFileSelect = (file) => {
    if (file && file.type === 'application/pdf') {
      setPendingFile(file);
      setShowNamePrompt(true);
      setPaperName('');
    }
  };

  const handleConfirmUpload = async () => {
    if (!paperName.trim()) return;

    setIsUploading(true);
    
    try {
      // Call your backend API
      const result = await uploadPDF(pendingFile, paperName.trim());
      
      // Add to uploaded papers - use paper_id from backend
      setUploadedPapers([...uploadedPapers, {
        id: result.paper_id,
        name: result.paper_id,
        fileName: result.filename
      }]);

      // Add system message using backend response
      setMessages([...messages, {
        role: 'system',
        content: result.message
      }]);
    } catch (error) {
      console.error('Upload failed:', error);
      setMessages([...messages, {
        role: 'system',
        content: `Failed to upload: ${error.message}`
      }]);
    } finally {
      setShowNamePrompt(false);
      setPendingFile(null);
      setPaperName('');
      setIsUploading(false);
    }
  };

  const handleCancelUpload = () => {
    setShowNamePrompt(false);
    setPendingFile(null);
    setPaperName('');
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    setMessages([...messages, { role: 'user', content: userMessage }]);

    try {
      // Call your backend API
      const response = await sendMessage(userMessage, uploadedPapers);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response
      }]);
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    }
  };

  return (
    <div className="flex h-screen bg-linear-to-br from-slate-900 via-purple-900 to-slate-900">
      <Sidebar 
        uploadedPapers={uploadedPapers}
        onFileSelect={handleFileSelect}
      />

      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-slate-800/50 backdrop-blur-xl border-b border-purple-500/20 p-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-400" />
            Graph RAG Assistant
          </h1>
          <p className="text-slate-400 text-sm mt-1">Ask questions about your uploaded documents</p>
        </div>

        <ChatMessages messages={messages} />
        
        <ChatInput 
          inputMessage={inputMessage}
          setInputMessage={setInputMessage}
          onSendMessage={handleSendMessage}
        />
      </div>

      <NamePromptModal
        show={showNamePrompt}
        pendingFile={pendingFile}
        paperName={paperName}
        setPaperName={setPaperName}
        onConfirm={handleConfirmUpload}
        onCancel={handleCancelUpload}
        isUploading={isUploading}
      />
    </div>
  );
}