import api from './authService';

export const loanService = {
  async sendMessage(message) {
    const response = await api.post('/protected/message', { message });
    return response.data;
  },

  async getConversationState() {
    const response = await api.get('/protected/conversation-state');
    return response.data;
  },

  async uploadDocument(file, documentType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const response = await api.post('/protected/upload-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getSanctionLetter(sanctionLetterId) {
    const response = await api.get(`/sanction-letter/${sanctionLetterId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async resetConversation() {
    const response = await api.post('/protected/reset-conversation');
    return response.data;
  },
};