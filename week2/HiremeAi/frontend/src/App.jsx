import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import ChatInput from './components/ChatInput';
import { fetchCandidateProfile, sendChatMessageStream } from './api';
import { Menu, Bot, RefreshCw } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [candidate, setCandidate] = useState(null);
  const [loadingCandidate, setLoadingCandidate] = useState(true);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    async function loadCandidate() {
      setLoadingCandidate(true);
      const data = await fetchCandidateProfile();
      if (data) {
        setCandidate(data);
      }
      setLoadingCandidate(false);
    }
    loadCandidate();
  }, []);

  const handleSendMessage = async (text) => {
    const userMsg = { sender: 'user', text };
    const aiMsgPlaceholder = { sender: 'ai', text: '' };

    setMessages((prev) => [...prev, userMsg, aiMsgPlaceholder]);
    setIsLoading(true);

    try {
      await sendChatMessageStream(text, (accumulatedText) => {
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastIndex = newMessages.length - 1;
          if (lastIndex >= 0 && newMessages[lastIndex].sender === 'ai') {
            newMessages[lastIndex] = { ...newMessages[lastIndex], text: accumulatedText };
          }
          return newMessages;
        });
      });
    } catch (err) {
      console.error(err);
      setMessages((prev) => {
        const newMessages = [...prev];
        const lastIndex = newMessages.length - 1;
        const errorText = `⚠️ Error: Could not connect to Candidate AI. (${err.message})`;
        if (lastIndex >= 0 && newMessages[lastIndex].sender === 'ai') {
          newMessages[lastIndex] = { ...newMessages[lastIndex], text: errorText };
        } else {
          newMessages.push({ sender: 'ai', text: errorText });
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectPrompt = (promptText) => {
    handleSendMessage(promptText);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="app-container">
      <Sidebar
        candidate={candidate}
        loadingCandidate={loadingCandidate}
        onSelectPrompt={handleSelectPrompt}
        onClearChat={handleClearChat}
        isOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />

      <main className="main-chat">
        <header className="chat-header">
          <div className="chat-header-left">
            <button 
              className="mobile-menu-toggle" 
              onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
            >
              <Menu size={22} />
            </button>
            <div className="active-candidate-badge">
              <span className="status-dot"></span>
              <span>{candidate?.name ? `${candidate.name} (AI Candidate)` : 'AI Candidate Ready'}</span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button 
              onClick={() => {
                setLoadingCandidate(true);
                fetchCandidateProfile().then(data => {
                  if (data) setCandidate(data);
                  setLoadingCandidate(false);
                });
              }}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-color)',
                color: 'var(--text-muted)',
                borderRadius: '8px',
                padding: '0.35rem 0.65rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                fontSize: '0.75rem'
              }}
              title="Refresh candidate resume"
            >
              <RefreshCw size={12} className={loadingCandidate ? 'spin' : ''} /> Refresh Profile
            </button>
          </div>
        </header>

        <ChatArea
          messages={messages}
          isLoading={isLoading}
          candidate={candidate}
          onSelectPrompt={handleSelectPrompt}
        />

        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          inputRef={inputRef}
        />
      </main>
    </div>
  );
}
