import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Send, 
  Paperclip, 
  Smile, 
  Clock,
  CheckCheck,
  AlertCircle,
  FileText,
  Image as ImageIcon,
  Video
} from 'lucide-react';
import toast from 'react-hot-toast';

const MessageModal = ({ isOpen, onClose, patientData }) => {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [messageType, setMessageType] = useState('secure'); // secure, urgent, routine
  const [attachments, setAttachments] = useState([]);

  // Previous messages (mock data)
  const [previousMessages] = useState([
    {
      id: 1,
      from: 'Dr. Martinez',
      to: patientData?.name,
      message: 'Hello! How are you feeling today?',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      read: true,
      type: 'sent'
    },
    {
      id: 2,
      from: patientData?.name,
      to: 'Dr. Martinez',
      message: 'Much better, thank you! The medication is helping.',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
      read: true,
      type: 'received'
    }
  ]);

  const handleSendMessage = () => {
    if (!message.trim() && attachments.length === 0) {
      toast.error('Please enter a message or attach a file');
      return;
    }

    setIsSending(true);

    // Simulate sending message
    setTimeout(() => {
      setIsSending(false);
      toast.success(`✉️ Secure message sent to ${patientData?.name}`, {
        duration: 3000
      });
      
      // Clear form
      setMessage('');
      setAttachments([]);
      
      // Close modal after a short delay
      setTimeout(() => {
        onClose();
      }, 1000);
    }, 1500);
  };

  const handleFileAttach = () => {
    toast.success('File attachment coming soon', {
      icon: '📎'
    });
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 3600000) {
      // Less than 1 hour
      return `${Math.floor(diff / 60000)} min ago`;
    } else if (diff < 86400000) {
      // Less than 1 day
      return `${Math.floor(diff / 3600000)} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black bg-opacity-50"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <Send className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">
                  Send Secure Message
                </h3>
                <p className="text-sm text-blue-100">
                  To: {patientData?.name} ({patientData?.id})
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Message Type Selector */}
          <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
            <div className="flex space-x-2">
              <button
                onClick={() => setMessageType('secure')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  messageType === 'secure'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="flex items-center space-x-2">
                  <CheckCheck className="h-4 w-4" />
                  <span>Secure</span>
                </span>
              </button>
              <button
                onClick={() => setMessageType('urgent')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  messageType === 'urgent'
                    ? 'bg-red-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4" />
                  <span>Urgent</span>
                </span>
              </button>
              <button
                onClick={() => setMessageType('routine')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  messageType === 'routine'
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <span className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Routine</span>
                </span>
              </button>
            </div>
          </div>

          {/* Previous Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-gray-50">
            <div className="text-center text-sm text-gray-500 mb-4">
              Previous Conversation
            </div>
            {previousMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'sent' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-sm px-4 py-3 rounded-2xl ${
                    msg.type === 'sent'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-medium opacity-75">
                      {msg.from}
                    </span>
                    <span className="text-xs opacity-50">
                      {formatTimestamp(msg.timestamp)}
                    </span>
                  </div>
                  <p className="text-sm">{msg.message}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Message Composer */}
          <div className="border-t border-gray-200 bg-white">
            {/* Attachments Preview */}
            {attachments.length > 0 && (
              <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Attachments:</span>
                  {attachments.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-1 px-3 py-1 bg-white rounded-lg text-sm"
                    >
                      <Paperclip className="h-4 w-4 text-gray-400" />
                      <span>{file.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Text Area */}
            <div className="px-6 py-4">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your secure message here..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={4}
                disabled={isSending}
              />
            </div>

            {/* Action Bar */}
            <div className="px-6 py-4 flex items-center justify-between bg-gray-50 border-t border-gray-200">
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleFileAttach}
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Attach file"
                  disabled={isSending}
                >
                  <Paperclip className="h-5 w-5" />
                </button>
                <button
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Add emoji"
                  disabled={isSending}
                >
                  <Smile className="h-5 w-5" />
                </button>
                <button
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Attach document"
                  disabled={isSending}
                >
                  <FileText className="h-5 w-5" />
                </button>
                <button
                  className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Attach image"
                  disabled={isSending}
                >
                  <ImageIcon className="h-5 w-5" />
                </button>
              </div>

              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-500">
                  {message.length} / 5000 characters
                </span>
                <button
                  onClick={handleSendMessage}
                  disabled={isSending || (!message.trim() && attachments.length === 0)}
                  className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
                    isSending || (!message.trim() && attachments.length === 0)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {isSending ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <Send className="h-4 w-4" />
                      <span>Send Message</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Security Notice */}
          <div className="px-6 py-3 bg-blue-50 border-t border-blue-100">
            <p className="text-xs text-blue-800 flex items-center">
              <CheckCheck className="h-4 w-4 mr-2" />
              This message is encrypted and HIPAA compliant. Only you and {patientData?.name} can read it.
            </p>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default MessageModal;

