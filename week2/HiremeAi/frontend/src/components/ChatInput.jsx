import React, { useState, useRef, useEffect } from 'react';
import { SendHorizontal } from 'lucide-react';

export default function ChatInput({ onSendMessage, isLoading, inputRef }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  // Combine external inputRef if passed
  const handleRef = (el) => {
    textareaRef.current = el;
    if (inputRef) {
      if (typeof inputRef === 'function') inputRef(el);
      else inputRef.current = el;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (!text.trim() || isLoading) return;
    onSendMessage(text);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleChange = (e) => {
    setText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  };

  return (
    <div className="input-container-wrapper">
      <div className="input-box">
        <textarea
          ref={handleRef}
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask candidate AI a question about experience, skills, or projects..."
          className="chat-textarea"
          rows={1}
          disabled={isLoading}
        />
        <button
          className="send-btn"
          onClick={handleSubmit}
          disabled={!text.trim() || isLoading}
          title="Send message"
        >
          <SendHorizontal size={18} />
        </button>
      </div>
      <p className="disclaimer-text">
        HiremeAi answers are generated strictly using the candidate's resume via Groq LLM.
      </p>
    </div>
  );
}
