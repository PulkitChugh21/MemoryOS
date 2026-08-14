/**
 * MemoryOS Frontend — Chat Store (Zustand)
 */

import { create } from 'zustand';
import { chatApi } from '../api/client';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sourcesUsed?: number;
  timestamp: string;
  isStreaming?: boolean;
}

interface ChatState {
  messages: ChatMessage[];
  sessionId: string | null;
  isLoading: boolean;
  error: string | null;
  sendMessage: (projectId: string, message: string) => Promise<void>;
  sendMessageStream: (projectId: string, message: string) => Promise<void>;
  clearChat: () => void;
  setSessionId: (id: string | null) => void;
  loadSession: (messages: ChatMessage[]) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  sessionId: null,
  isLoading: false,
  error: null,

  sendMessage: async (projectId, message) => {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMsg],
      isLoading: true,
      error: null,
    }));

    try {
      const { data } = await chatApi.send(projectId, {
        message,
        session_id: get().sessionId || undefined,
      });

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.response,
        sourcesUsed: data.sources_used,
        timestamp: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, assistantMsg],
        sessionId: data.session_id,
        isLoading: false,
      }));
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail?.error?.message || 'Failed to send message';
      set({ error: errorMsg, isLoading: false });
    }
  },

  sendMessageStream: async (projectId, message) => {
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };

    const assistantId = crypto.randomUUID();

    set((state) => ({
      messages: [
        ...state.messages,
        userMsg,
        { id: assistantId, role: 'assistant', content: '', timestamp: new Date().toISOString(), isStreaming: true },
      ],
      isLoading: true,
      error: null,
    }));

    try {
      const token = localStorage.getItem('memoryos_token');
      const url = chatApi.streamUrl(projectId);

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message, session_id: get().sessionId }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No response body');

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const payload = JSON.parse(line.slice(6));
              if (payload.text) {
                set((state) => ({
                  messages: state.messages.map((m) =>
                    m.id === assistantId ? { ...m, content: m.content + payload.text } : m
                  ),
                }));
              }
            } catch { /* skip non-JSON lines */ }
          }
          if (line.startsWith('event: metadata')) {
            // Next data line has session metadata
          }
          if (line.startsWith('event: done')) {
            set((state) => ({
              messages: state.messages.map((m) =>
                m.id === assistantId ? { ...m, isStreaming: false } : m
              ),
              isLoading: false,
            }));
          }
        }
      }

      set({ isLoading: false });
    } catch (err: any) {
      set({ error: 'Streaming failed', isLoading: false });
    }
  },

  clearChat: () => set({ messages: [], sessionId: null, error: null }),
  setSessionId: (id) => set({ sessionId: id }),
  loadSession: (messages) => set({ messages, error: null }),
}));
