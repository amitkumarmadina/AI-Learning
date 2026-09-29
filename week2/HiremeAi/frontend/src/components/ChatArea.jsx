import React, { useEffect, useRef, useState } from 'react';
import { Bot, User, Copy, Check, Sparkles, MessageSquare, Briefcase, GraduationCap, Code } from 'lucide-react';

export default function ChatArea({ messages, isLoading, candidate, onSelectPrompt }) {
  const messagesEndRef = useRef(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const starterCards = [
    {
      icon: <Briefcase size={18} color="var(--accent-primary)" />,
      title: "Work Experience",
      desc: "Where have you worked and what were your key responsibilities?"
    },
    {
      icon: <Code size={18} color="var(--accent-cyan)" />,
      title: "Technical Skills",
      desc: "What tools, frameworks, and programming languages do you master?"
    },
    {
      icon: <GraduationCap size={18} color="var(--accent-secondary)" />,
      title: "Projects & Impact",
      desc: "Tell me about your most impressive project and achievements."
    },
    {
      icon: <Sparkles size={18} color="var(--accent-emerald)" />,
      title: "Fit for Role",
      desc: "Why should our company hire you for this position?"
    }
  ];

  return (
    <div className="messages-container">
      {messages.length === 0 ? (
        <div className="welcome-screen">
          <div className="welcome-icon">
            <Bot size={32} />
          </div>
          <h2 className="welcome-title">
            Interview {candidate?.name || 'the Candidate'}
          </h2>
          <p className="welcome-subtitle">
            Ask any question to interview the AI candidate representative. All answers are derived directly and strictly from their parsed resume.
          </p>

          <div className="starter-grid">
            {starterCards.map((card, idx) => (
              <div 
                key={idx} 
                className="starter-card"
                onClick={() => onSelectPrompt(card.desc)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {card.icon}
                  <h4>{card.title}</h4>
                </div>
                <p>{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`message-wrapper ${msg.sender}`}
            >
              <div className={`avatar ${msg.sender}`}>
                {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>

              <div className="message-bubble">
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </div>

                {msg.sender === 'ai' && (
                  <div className="message-meta">
                    <span style={{ fontSize: '0.725rem', color: 'var(--text-dim)' }}>
                      Candidate AI
                    </span>
                    <button 
                      className="copy-btn"
                      onClick={() => handleCopy(msg.text, index)}
                      title="Copy response"
                    >
                      {copiedIndex === index ? (
                        <>
                          <Check size={13} color="var(--accent-emerald)" /> Copied
                        </>
                      ) : (
                        <>
                          <Copy size={13} /> Copy
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-wrapper ai">
              <div className="avatar ai">
                <Bot size={18} />
              </div>
              <div className="message-bubble typing-bubble">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          )}
        </>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
