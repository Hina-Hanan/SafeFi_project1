import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Chip,
  Stack,
  Alert,
  Button,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { colors, getStatusColor } from '../utils/riskColors';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface LLMHealthResponse {
  ollama_available: boolean;
  vector_store_initialized: boolean;
  model: string;
  embedding_model: string;
  document_count: number;
}

interface LLMQueryResponse {
  answer: string;
  sources: any[];
  query: string;
  model: string;
  processing_time: number;
}

const fetchLLMHealth = async (): Promise<LLMHealthResponse> => {
  const { data } = await api.get<LLMHealthResponse>('/llm/health');
  return data;
};

const queryLLM = async (query: string): Promise<LLMQueryResponse> => {
  const { data } = await api.post<LLMQueryResponse>('/llm/query', { query });
  return data;
};

const initializeVectorStore = async (): Promise<void> => {
  await api.post('/llm/initialize');
};

export default function AIAssistantChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your DeFi Risk Assistant. Ask me anything about protocols, risk scores, or metrics.\n\nExamples:\n• "What are the high-risk protocols?"\n• "Show me Aave\'s metrics"\n• "Which protocols have TVL above $1B?"',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: health, refetch: refetchHealth } = useQuery({
    queryKey: ['llm-health'],
    queryFn: fetchLLMHealth,
    refetchInterval: 30000,
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await queryLLM(userMessage.content);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message || 'Unknown error'}. Please check if the LLM service is running.`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Chat cleared. How can I help you?',
        timestamp: new Date(),
      },
    ]);
  };

  const llmStatus = health?.ollama_available && health?.vector_store_initialized;

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper
        sx={{
          p: 2,
          mb: 2,
          background: colors.darkGray,
          border: `2px solid ${colors.gray}`,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                background: colors.black,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: `2px solid ${colors.gray}`,
              }}
            >
              <BotIcon sx={{ fontSize: 32, color: colors.white }} />
            </Box>
            <Box>
              <Typography
                variant="h5"
                sx={{
                  color: colors.white,
                  fontWeight: 700,
                }}
              >
                AI Risk Assistant
              </Typography>
              <Typography variant="caption" sx={{ color: colors.textGray }}>
                Powered by {health?.model || 'TinyLlama'} • RAG-enabled
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip
              label={llmStatus ? 'ONLINE' : 'OFFLINE'}
              sx={{
                background: getStatusColor(llmStatus || false, 'background'),
                border: `2px solid ${getStatusColor(llmStatus || false, 'border')}`,
                color: getStatusColor(llmStatus || false, 'text'),
                fontWeight: 700,
              }}
            />
            <IconButton 
              onClick={() => refetchHealth()} 
              size="small"
              sx={{
                background: colors.darkGray,
                border: `2px solid ${colors.gray}`,
                color: colors.white,
                '&:hover': {
                  background: colors.black,
                },
              }}
            >
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>

        {health && (
          <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
            <Chip
              label={`${health.document_count} docs`}
              size="small"
              sx={{
                background: colors.black,
                border: `2px solid ${colors.gray}`,
                color: colors.white,
                fontWeight: 600,
              }}
            />
            <Chip
              label={`Model: ${health.model}`}
              size="small"
              sx={{
                background: colors.black,
                border: `2px solid ${colors.gray}`,
                color: colors.white,
                fontWeight: 600,
              }}
            />
          </Stack>
        )}
      </Paper>

      {/* Status Alert */}
      {!llmStatus && (
        <Alert
          severity="error"
          sx={{
            mb: 2,
            background: colors.redDark,
            border: `2px solid ${colors.red}`,
            color: colors.white,
          }}
          action={
            !health?.vector_store_initialized && health?.ollama_available && (
              <Button
                color="inherit"
                size="small"
                onClick={async () => {
                  try {
                    await initializeVectorStore();
                    refetchHealth();
                  } catch (error) {
                    console.error('Failed to initialize vector store:', error);
                  }
                }}
                sx={{
                  border: `2px solid ${colors.white}`,
                  fontWeight: 600,
                }}
              >
                Initialize Now
              </Button>
            )
          }
        >
          {!health?.ollama_available && 'LLM service unavailable. Run: ollama serve'}
          {health?.ollama_available && !health?.vector_store_initialized && 'Vector store not initialized. Click "Initialize Now" or restart backend.'}
        </Alert>
      )}

      {/* Messages */}
      <Paper
        sx={{
          flex: 1,
          p: 2,
          mb: 2,
          overflow: 'auto',
          background: colors.black,
          border: `2px solid ${colors.gray}`,
          minHeight: 400,
          maxHeight: 600,
        }}
      >
        <Stack spacing={2}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                gap: 1,
              }}
            >
              {message.role === 'assistant' && (
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    background: colors.darkGray,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: `2px solid ${colors.gray}`,
                    flexShrink: 0,
                  }}
                >
                  <BotIcon sx={{ fontSize: 20, color: colors.white }} />
                </Box>
              )}

              <Paper
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  background: message.role === 'user' ? colors.darkGray : colors.black,
                  border: `2px solid ${colors.gray}`,
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    color: colors.white,
                  }}
                >
                  {message.content}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ 
                    display: 'block', 
                    mt: 1,
                    color: colors.textGray,
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Paper>

              {message.role === 'user' && (
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    background: colors.darkGray,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: `2px solid ${colors.gray}`,
                    flexShrink: 0,
                  }}
                >
                  <PersonIcon sx={{ fontSize: 20, color: colors.white }} />
                </Box>
              )}
            </Box>
          ))}

          {isLoading && (
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  background: colors.darkGray,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: `2px solid ${colors.gray}`,
                }}
              >
                <BotIcon sx={{ fontSize: 20, color: colors.white }} />
              </Box>
              <Paper
                sx={{
                  p: 2,
                  background: colors.black,
                  border: `2px solid ${colors.gray}`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <CircularProgress size={20} sx={{ color: colors.white }} />
                <Typography variant="body2" sx={{ color: colors.white }}>
                  Thinking...
                </Typography>
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Stack>
      </Paper>

      {/* Input */}
      <Paper
        sx={{
          p: 2,
          background: colors.darkGray,
          border: `2px solid ${colors.gray}`,
        }}
      >
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about DeFi protocols, risk scores, metrics..."
            disabled={!llmStatus || isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                background: colors.black,
                color: colors.white,
                '& fieldset': {
                  borderColor: colors.gray,
                  borderWidth: 2,
                },
              },
            }}
          />
          <IconButton
            onClick={handleSend}
            disabled={!input.trim() || !llmStatus || isLoading}
            sx={{
              background: colors.darkGray,
              border: `2px solid ${colors.gray}`,
              color: colors.white,
              '&:hover': {
                background: colors.black,
              },
              '&:disabled': {
                background: colors.black,
                color: colors.lightGray,
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button
            size="small"
            onClick={() => setInput('What are the high-risk protocols?')}
            sx={{
              background: colors.black,
              border: `2px solid ${colors.gray}`,
              color: colors.white,
              '&:hover': {
                background: colors.darkGray,
              },
            }}
          >
            High-risk protocols?
          </Button>
          <Button
            size="small"
            onClick={() => setInput('Show me the latest protocol metrics')}
            sx={{
              background: colors.black,
              border: `2px solid ${colors.gray}`,
              color: colors.white,
              '&:hover': {
                background: colors.darkGray,
              },
            }}
          >
            Latest metrics?
          </Button>
          <Button
            size="small"
            onClick={handleClearChat}
            sx={{
              background: colors.redDark,
              border: `2px solid ${colors.red}`,
              color: colors.red,
              '&:hover': {
                background: colors.red,
                color: colors.white,
              },
            }}
          >
            Clear chat
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}
