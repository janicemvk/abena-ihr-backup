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
      content: 'Hello! I\'m your eCDome analysis assistant. How can I help you understand the patient\'s endocannabinoid system data?'
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
      // Check for specific keywords and generate appropriate responses with mock data
      if (lowerQuery.includes('anandamide') || lowerQuery.includes('2-ag') || lowerQuery.includes('endocannabinoid')) {
        const levels = patientData.endocannabinoidData.levels;
        const anandamideStatus = levels.anandamide > 0.4 ? 'Optimal' : levels.anandamide > 0.3 ? 'Moderate' : 'Low';
        const ag2Status = levels['2-AG'] > 0.35 ? 'Optimal' : levels['2-AG'] > 0.25 ? 'Moderate' : 'Low';
        
        return `The patient's endocannabinoid levels show:\n\n` +
          `- Anandamide: ${(levels.anandamide * 100).toFixed(1)}% (${anandamideStatus})\n` +
          `- 2-AG: ${(levels['2-AG'] * 100).toFixed(1)}% (${ag2Status})\n` +
          `- PEA: ${(levels.PEA * 100).toFixed(1)}%\n` +
          `- OEA: ${(levels.OEA * 100).toFixed(1)}%\n\n` +
          `Analysis: ${anandamideStatus === 'Optimal' ? 'The endocannabinoid system appears well-balanced.' : 'Consider lifestyle interventions to support endocannabinoid production.'}`;
      }

      if (lowerQuery.includes('receptor') || lowerQuery.includes('cb1') || lowerQuery.includes('cb2') || lowerQuery.includes('implication')) {
        // Get receptor activity data from patient metrics or endocannabinoid data
        const activity = patientData.metrics?.receptorActivity || patientData.endocannabinoidData?.receptorActivity || {
          CB1: 0.78,
          CB2: 0.65
        };
        
        const cb1Status = activity.CB1 > 0.7 ? 'Optimal' : activity.CB1 > 0.5 ? 'Moderate' : 'Low';
        const cb2Status = activity.CB2 > 0.7 ? 'Optimal' : activity.CB2 > 0.5 ? 'Moderate' : 'Low';
        
        return `The patient's receptor activity analysis:\n\n` +
          `- CB1 Receptor: ${(activity.CB1 * 100).toFixed(1)}% (${cb1Status})\n` +
          `- CB2 Receptor: ${(activity.CB2 * 100).toFixed(1)}% (${cb2Status})\n\n` +
          `Clinical Implications:\n` +
          `- CB1 receptors are primarily located in the brain and central nervous system, affecting pain perception, mood, and appetite.\n` +
          `- CB2 receptors are found in immune cells and peripheral tissues, influencing inflammation and immune response.\n\n` +
          `Recommendation: ${cb1Status === 'Optimal' && cb2Status === 'Optimal' ? 
            'Receptor activity is well-balanced. Continue current treatment plan and monitor for any changes.' : 
            'Consider lifestyle modifications (exercise, stress reduction) and targeted interventions to optimize receptor function and system balance.'}`;
      }

      if (lowerQuery.includes('medication') || lowerQuery.includes('drug') || lowerQuery.includes('interaction')) {
        // Mock medication interactions data
        const mockInteractions = [
          {
            type: 'Moderate',
            medications: ['Warfarin', 'Cannabinoids'],
            effect: 'Increased bleeding risk due to enhanced anticoagulant effects',
            recommendation: 'Monitor INR levels closely and adjust warfarin dosage as needed'
          },
          {
            type: 'Mild',
            medications: ['Metformin', 'Endocannabinoid system'],
            effect: 'Potential enhancement of glucose metabolism',
            recommendation: 'Monitor blood glucose levels and adjust diabetes medication if needed'
          },
          {
            type: 'Severe',
            medications: ['SSRIs', 'Cannabinoids'],
            effect: 'Increased risk of serotonin syndrome',
            recommendation: 'Avoid concurrent use or monitor for serotonin syndrome symptoms'
          }
        ];

        return `I've found ${mockInteractions.length} potential medication interactions:\n\n` +
          mockInteractions.map(interaction => 
            `- ${interaction.type}: ${interaction.medications.join(', ')}\n` +
            `  Effect: ${interaction.effect}\n` +
            `  Recommendation: ${interaction.recommendation}`
          ).join('\n\n');
      }

      if (lowerQuery.includes('research') || lowerQuery.includes('study') || lowerQuery.includes('literature')) {
        // Mock research literature data
        const mockLiterature = [
          {
            title: "Endocannabinoid System in Chronic Pain Management",
            authors: "Smith et al.",
            journal: "Nature Medicine",
            year: 2023,
            relevance: "High",
            summary: "Study demonstrates the role of anandamide in pain modulation and CB1 receptor activation in chronic pain patients."
          },
          {
            title: "CB1 Receptor Activity in Metabolic Disorders",
            authors: "Johnson et al.",
            journal: "Cell Metabolism",
            year: 2023,
            relevance: "Moderate",
            summary: "Research shows CB1 receptor dysfunction in patients with metabolic syndrome and potential therapeutic interventions."
          },
          {
            title: "2-AG Levels in Inflammatory Conditions",
            authors: "Brown et al.",
            journal: "Journal of Immunology",
            year: 2022,
            relevance: "High",
            summary: "Investigation of 2-AG levels in patients with chronic inflammation and its correlation with CB2 receptor activity."
          }
        ];
        
        return `Here are some relevant research papers:\n\n` +
          mockLiterature.map(paper => 
            `- ${paper.title}\n` +
            `  Authors: ${paper.authors}\n` +
            `  Journal: ${paper.journal}\n` +
            `  Year: ${paper.year}\n` +
            `  Relevance: ${paper.relevance}\n` +
            `  Summary: ${paper.summary}`
          ).join('\n\n');
      }

      if (lowerQuery.includes('treatment') || lowerQuery.includes('recommendation')) {
        // Mock treatment recommendations
        const mockRecommendations = [
          {
            category: "Lifestyle Modifications",
            recommendation: "Implement regular exercise routine focusing on low-impact activities to support endocannabinoid production",
            expectedImpact: "Improved anandamide levels and CB1 receptor activity"
          },
          {
            category: "Nutritional Support",
            recommendation: "Increase omega-3 fatty acid intake and consider endocannabinoid-supporting supplements",
            expectedImpact: "Enhanced 2-AG levels and reduced inflammation markers"
          },
          {
            category: "Stress Management",
            recommendation: "Implement mindfulness practices and stress reduction techniques",
            expectedImpact: "Improved CB2 receptor activity and overall system balance"
          }
        ];
        
        return `Based on the current analysis, here are the treatment recommendations:\n\n` +
          mockRecommendations.map(rec => 
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
    <div className="fixed bottom-4 right-4 w-96 bg-white rounded-lg shadow-xl border border-gray-200">
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold">eCDome Assistant</h3>
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