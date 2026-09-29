import React from 'react';
import { 
  Bot, 
  User, 
  Briefcase, 
  GraduationCap, 
  Award, 
  Trash2, 
  Sparkles, 
  ChevronRight,
  Mail,
  Phone,
  Code
} from 'lucide-react';

export default function Sidebar({ 
  candidate, 
  loadingCandidate, 
  onSelectPrompt, 
  onClearChat, 
  isOpen,
  onCloseMobile 
}) {
  const samplePrompts = [
    "Give me a quick 2-minute summary of your profile.",
    "What are your top technical skills and strengths?",
    "Tell me about your most relevant work experience.",
    "What key projects have you worked on?",
    "Why are you a strong candidate for this role?"
  ];

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <div className="logo-badge">
          <Bot size={22} />
        </div>
        <div className="logo-text">
          <h1>HiremeAi</h1>
          <p>Candidate AI Representative</p>
        </div>
      </div>

      <div className="sidebar-content">
        {/* Candidate Profile Section */}
        <div>
          <div className="section-title">
            <User size={14} /> Candidate Profile
          </div>

          <div className="candidate-card">
            {loadingCandidate ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Extracting resume data...
              </p>
            ) : candidate ? (
              <>
                <h3 className="candidate-name">{candidate.name || "Candidate Name"}</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  AI-powered representation
                </p>

                <div className="candidate-meta">
                  {candidate.total_experience_years !== null && candidate.total_experience_years !== undefined && (
                    <span className="meta-pill">
                      <Briefcase size={12} /> {candidate.total_experience_years} Yrs Exp
                    </span>
                  )}
                  {candidate.email && (
                    <span className="meta-pill" title={candidate.email}>
                      <Mail size={12} /> Email
                    </span>
                  )}
                  {candidate.education && candidate.education.length > 0 && (
                    <span className="meta-pill">
                      <GraduationCap size={12} /> {candidate.education[0]?.school_name || "Education"}
                    </span>
                  )}
                </div>

                {candidate.skills && candidate.skills.length > 0 && (
                  <div style={{ marginTop: '1rem' }}>
                    <p style={{ fontSize: '0.725rem', color: 'var(--text-dim)', marginBottom: '0.4rem', fontWeight: 600 }}>
                      TOP SKILLS
                    </p>
                    <div className="skill-tags">
                      {candidate.skills.slice(0, 8).map((skill, index) => (
                        <span key={index} className="skill-tag">
                          {skill}
                        </span>
                      ))}
                      {candidate.skills.length > 8 && (
                        <span className="skill-tag" style={{ background: 'rgba(99,102,241,0.1)' }}>
                          +{candidate.skills.length - 8} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                Resume loaded from PDF
              </p>
            )}
          </div>
        </div>

        {/* Quick Interview Questions */}
        <div>
          <div className="section-title">
            <Sparkles size={14} /> Interview Prompts
          </div>
          <div>
            {samplePrompts.map((prompt, idx) => (
              <button
                key={idx}
                className="prompt-btn"
                onClick={() => {
                  onSelectPrompt(prompt);
                  if (onCloseMobile) onCloseMobile();
                }}
              >
                <span>{prompt}</span>
                <ChevronRight size={14} />
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="clear-btn" onClick={onClearChat}>
          <Trash2 size={15} /> Clear History
        </button>
        <span style={{ fontSize: '0.725rem', color: 'var(--text-dim)' }}>
          Groq AI Powered
        </span>
      </div>
    </aside>
  );
}
