import React, { useState, useEffect, useRef } from 'react';
import { Send, X } from 'lucide-react';
import {
  ihrIntelligenceService,
  medicalDatabaseService,
  drugInteractionsService,
  scientificLiteratureService,
  handleApiError
} from '../services/api';

const ECDomeChatbot = ({ patientData, onClose }) => {
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      content: 'Hello! I\'m your eCBome analysis assistant. How can I help you understand the patient\'s endocannabinoid system data?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
    setIsTyping(true);

    try {
      const response = await generateResponse(userMessage);
      setMessages(prev => [...prev, { type: 'bot', content: response }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'bot',
        content: 'I apologize, but I encountered an error while processing your request. Please try again.'
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const generateResponse = async (query) => {
    const lowerQuery = query.toLowerCase();

    try {
      // Check for specific keywords and generate appropriate responses
      if (lowerQuery.includes('anandamide') || lowerQuery.includes('2-ag')) {
        const levels = patientData.metrics.endocannabinoidLevels;
        const analysis = await ihrIntelligenceService.analyzeEndocannabinoidLevels(levels);
        return `The patient's endocannabinoid levels show:\n\n` +
          `- Anandamide: ${(levels.anandamide * 100).toFixed(1)}% (${analysis.anandamide.status})\n` +
          `- 2-AG: ${(levels['2-AG'] * 100).toFixed(1)}% (${analysis['2-AG'].status})\n\n` +
          `${analysis.recommendation}`;
      }

      if (lowerQuery.includes('receptor') || lowerQuery.includes('cb1') || lowerQuery.includes('cb2')) {
        const activity = patientData.metrics.receptorActivity;
        const analysis = await ihrIntelligenceService.analyzeReceptorActivity(activity);
        return `The patient's receptor activity analysis:\n\n` +
          `- CB1: ${(activity.CB1 * 100).toFixed(1)}% (${analysis.CB1.status})\n` +
          `- CB2: ${(activity.CB2 * 100).toFixed(1)}% (${analysis.CB2.status})\n\n` +
          `${analysis.recommendation}`;
      }

      if (lowerQuery.includes('medication') || lowerQuery.includes('drug') || lowerQuery.includes('interaction')) {
        const interactions = await drugInteractionsService.checkInteractions(
          patientData.medications || [],
          patientData.cannabinoids || []
        );
        
        if (interactions.length === 0) {
          return 'No significant medication interactions have been detected with the current endocannabinoid system state.';
        }

        return `I've found ${interactions.length} potential medication interactions:\n\n` +
          interactions.map(interaction => 
            `- ${interaction.type}: ${interaction.medications.join(', ')}\n` +
            `  Effect: ${interaction.effect}\n` +
            `  Recommendation: ${interaction.recommendation}`
          ).join('\n\n');
      }

      if (lowerQuery.includes('research') || lowerQuery.includes('study') || lowerQuery.includes('literature')) {
        const literature = await scientificLiteratureService.searchLiterature(
          `endocannabinoid system ${patientData.metrics.endocannabinoidLevels.anandamide > 0.7 ? 'high' : 'low'} anandamide`
        );
        
        return `Here are some relevant research papers:\n\n` +
          literature.map(paper => 
            `- ${paper.title}\n` +
            `  Authors: ${paper.authors.join(', ')}\n` +
            `  DOI: ${paper.doi}\n` +
            `  Summary: ${paper.summary}`
          ).join('\n\n');
      }

      if (lowerQuery.includes('treatment') || lowerQuery.includes('recommendation')) {
        const recommendations = await ihrIntelligenceService.getTreatmentRecommendations(
          patientData.metrics,
          patientData.medications || []
        );
        
        return `Based on the current analysis, here are the treatment recommendations:\n\n` +
          recommendations.map(rec => 
            `- ${rec.category}:\n` +
            `  ${rec.recommendation}\n` +
            `  Expected Impact: ${rec.expectedImpact}`
          ).join('\n\n');
      }

      // Default response for general queries
      return 'I can help you understand:\n' +
        '- Endocannabinoid levels and their significance\n' +
        '- Receptor activity and implications\n' +
        '- Medication interactions\n' +
        '- Relevant research papers\n' +
        '- Treatment recommendations\n\n' +
        'What specific aspect would you like to know more about?';
    } catch (error) {
      console.error('Error generating response:', error);
      throw error;
    }
  };

  return (
    <div className="w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold">eCBome Assistant</h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="h-96 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.content.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < message.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 rounded-lg p-3">
              Typing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about the analysis..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ECDomeChatbot; 