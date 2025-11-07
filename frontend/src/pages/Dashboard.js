import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { loanService } from '../services/loanService';
import { LogOut, Send, Upload, FileText, User, Phone, Mail, MapPin, RefreshCw } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationState, setConversationState] = useState(null);
  const [uploadingDocument, setUploadingDocument] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConversationState();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversationState = async () => {
    try {
      const state = await loanService.getConversationState();
      setConversationState(state);
      if (state.messages && state.messages.length > 0) {
        setMessages(state.messages);
      }
    } catch (error) {
      toast.error('Failed to load conversation state');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await loanService.sendMessage(inputMessage);
      const botMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, botMessage]);
      
      // Update conversation state
      await loadConversationState();
    } catch (error) {
      toast.error('Failed to send message');
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingDocument(true);
    try {
      // Determine document type based on file name or extension
      let documentType = 'other';
      const fileName = file.name.toLowerCase();
      if (fileName.includes('aadhaar') || fileName.includes('aadhar')) {
        documentType = 'aadhaar';
      } else if (fileName.includes('pan')) {
        documentType = 'pan';
      } else if (fileName.includes('salary') || fileName.includes('income')) {
        documentType = 'income_proof';
      } else if (fileName.includes('bank')) {
        documentType = 'bank_statement';
      }

      await loanService.uploadDocument(file, documentType);
      toast.success('Document uploaded successfully');
      await loadConversationState();
    } catch (error) {
      toast.error('Failed to upload document');
    } finally {
      setUploadingDocument(false);
      e.target.value = null; // Reset file input
    }
  };

  const resetConversation = async () => {
    try {
      await loanService.resetConversation();
      setMessages([]);
      setConversationState(null);
      toast.success('Conversation reset successfully');
    } catch (error) {
      toast.error('Failed to reset conversation');
    }
  };

  const downloadSanctionLetter = async () => {
    if (!conversationState?.sanction_letter_id) return;

    try {
      const blob = await loanService.getSanctionLetter(conversationState.sanction_letter_id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sanction_letter_${conversationState.sanction_letter_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      toast.error('Failed to download sanction letter');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Tata Capital</h1>
              <span className="ml-3 text-sm text-gray-500">Digital Loan Assistant</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={resetConversation}
                className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                  <p className="text-xs text-gray-500">{user?.email}</p>
                </div>
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="h-5 w-5 text-blue-600" />
                </div>
              </div>
              
              <button
                onClick={logout}
                className="flex items-center px-3 py-2 text-sm text-red-600 hover:text-red-800 border border-red-300 rounded-lg hover:bg-red-50"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Chat Area */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg h-96 lg:h-[600px] flex flex-col">
              {/* Chat Header */}
              <div className="p-4 border-b bg-blue-50 rounded-t-lg">
                <h3 className="text-lg font-semibold text-gray-900">Loan Assistant</h3>
                <p className="text-sm text-gray-600">
                  {conversationState?.conversation_stage || 'Ready to assist you'}
                </p>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-8">
                    <p>Welcome! How can I help you with your loan application today?</p>
                  </div>
                ) : (
                  messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs mt-1 opacity-75">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
                        <span className="text-sm">Thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <form onSubmit={sendMessage} className="p-4 border-t">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !inputMessage.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Customer Profile */}
            {conversationState?.customer_details && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Profile</h3>
                <div className="space-y-3">
                  {conversationState.customer_details.name && (
                    <div className="flex items-center text-sm">
                      <User className="h-4 w-4 text-gray-400 mr-2" />
                      <span>{conversationState.customer_details.name}</span>
                    </div>
                  )}
                  {conversationState.customer_details.email && (
                    <div className="flex items-center text-sm">
                      <Mail className="h-4 w-4 text-gray-400 mr-2" />
                      <span>{conversationState.customer_details.email}</span>
                    </div>
                  )}
                  {conversationState.customer_details.phone && (
                    <div className="flex items-center text-sm">
                      <Phone className="h-4 w-4 text-gray-400 mr-2" />
                      <span>{conversationState.customer_details.phone}</span>
                    </div>
                  )}
                  {conversationState.customer_details.address && (
                    <div className="flex items-center text-sm">
                      <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                      <span>{conversationState.customer_details.address}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Document Upload */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h3>
              <div className="space-y-3">
                <label className="flex items-center justify-center w-full px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-gray-400">
                  <Upload className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-600">
                    {uploadingDocument ? 'Uploading...' : 'Choose File'}
                  </span>
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleDocumentUpload}
                    accept=".pdf,.jpg,.jpeg,.png"
                    disabled={uploadingDocument}
                  />
                </label>
                <p className="text-xs text-gray-500 text-center">
                  PDF, JPG, PNG formats only
                </p>
              </div>
            </div>

            {/* Sanction Letter */}
            {conversationState?.sanction_letter_id && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Sanction Letter</h3>
                <button
                  onClick={downloadSanctionLetter}
                  className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Download Sanction Letter
                </button>
              </div>
            )}

            {/* Loan Status */}
            {conversationState && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Loan Status</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Stage:</span>
                    <span className="font-medium capitalize">{conversationState.conversation_stage}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Decision:</span>
                    <span className="font-medium capitalize">{conversationState.decision}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;