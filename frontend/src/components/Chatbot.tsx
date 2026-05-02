import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';
import axios from 'axios';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

export const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { text: "ask barista AI", sender: 'bot' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isOpen]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: userMessage
      });
      setMessages(prev => [...prev, { text: response.data.response, sender: 'bot' }]);
    } catch (error) {
      setMessages(prev => [...prev, { text: "Sorry, I'm having trouble connecting to the data server right now.", sender: 'bot' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-widget">
      <div className={`chatbot-window ${isOpen ? 'open' : ''}`}>
        <div className="chatbot-header">
          <MessageCircle size={20} color="#fdf8f5" />
          <div className="chatbot-header-title">Barista AI</div>
          <button 
            onClick={() => setIsOpen(false)} 
            style={{ marginLeft: 'auto', background: 'transparent', border: 'none', color: '#fdf8f5', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="chatbot-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.sender}`}>
              {msg.text}
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble bot" style={{ fontStyle: 'italic', opacity: 0.7 }}>
              Thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chatbot-input-container" onSubmit={handleSend}>
          <input
            type="text"
            className="chatbot-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about sales, margins..."
            disabled={isLoading}
          />
          <button type="submit" className="chatbot-send" disabled={isLoading || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
      </div>

      {!isOpen && (
        <div className="chatbot-toggle" onClick={() => setIsOpen(true)}>
          <MessageCircle size={28} />
        </div>
      )}
    </div>
  );
};
