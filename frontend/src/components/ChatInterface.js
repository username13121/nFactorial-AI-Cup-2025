import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  CircularProgress, 
  Divider,
  Paper,
  InputAdornment,
  IconButton,
  Fade
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import MicIcon from '@mui/icons-material/Mic';
import MessageList from './MessageList';
import ForumIcon from '@mui/icons-material/Forum';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const webSocketRef = useRef(null);
  const messagesEndRef = useRef(null);
  const [isReconnecting, setIsReconnecting] = useState(false);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    // Adjust the URL to match your backend
    setIsReconnecting(true);
    const ws = new WebSocket('ws://localhost:8080/ws/chat');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setIsReconnecting(false);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Message received:', data);
      
      switch(data.type) {
        case 'user_message':
          // User message is already added by sendMessage
          break;
        case 'ai_message':
          setMessages(prev => [...prev, { role: 'assistant', content: data.content }]);
          setIsLoading(false);
          break;
        case 'tool_start':
          setMessages(prev => [...prev, { role: 'system', content: `Using tool: ${data.name}...` }]);
          break;
        case 'tool_result':
          setMessages(prev => [...prev, { 
            role: 'system', 
            content: `Tool result from ${data.name}:`, 
            data: data.result 
          }]);
          break;
        case 'tool_error':
          setMessages(prev => [...prev, { 
            role: 'system', 
            content: `Error from tool ${data.name}: ${data.error}` 
          }]);
          break;
        default:
          console.warn('Unknown message type:', data.type);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      // Attempt to reconnect after a delay
      setTimeout(() => {
        if (!webSocketRef.current || webSocketRef.current.readyState === WebSocket.CLOSED) {
          connectWebSocket();
        }
      }, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsReconnecting(true);
    };
    
    webSocketRef.current = ws;
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (input.trim() === '' || !isConnected || isLoading) return;
    
    const message = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setInput('');
    setIsLoading(true);
    
    if (webSocketRef.current && webSocketRef.current.readyState === WebSocket.OPEN) {
      webSocketRef.current.send(JSON.stringify({ message }));
    } else {
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: 'Connection lost. Trying to reconnect...' 
      }]);
      setIsLoading(false);
      connectWebSocket();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '70vh',
        backgroundColor: 'transparent',
        borderRadius: '12px',
        overflow: 'hidden'
      }}
    >
      {/* Chat header */}
      <Box sx={{ 
        p: 2, 
        backgroundColor: 'rgba(144, 202, 249, 0.1)', 
        display: 'flex', 
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ForumIcon color="primary" />
          <Typography variant="h6" color="primary" fontWeight="medium">
            Hotel Assistant
          </Typography>
        </Box>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: 1,
          backgroundColor: isConnected ? 'rgba(46, 125, 50, 0.2)' : 'rgba(211, 47, 47, 0.2)',
          borderRadius: '16px',
          px: 1.5,
          py: 0.5,
          fontSize: '0.75rem'
        }}>
          <Box 
            sx={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              backgroundColor: isConnected ? '#4caf50' : '#f44336',
              animation: isReconnecting ? 'pulse 1.5s infinite' : 'none',
              '@keyframes pulse': {
                '0%': { opacity: 0.6 },
                '50%': { opacity: 1 },
                '100%': { opacity: 0.6 }
              }
            }} 
          />
          <Typography variant="caption" color="text.primary">
            {isConnected ? 'Connected' : isReconnecting ? 'Reconnecting...' : 'Disconnected'}
          </Typography>
        </Box>
      </Box>
      
      {/* Messages area */}
      <Box 
        sx={{ 
          flexGrow: 1, 
          overflow: 'auto', 
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 1.5,
          backgroundImage: 'radial-gradient(circle at 25% 25%, rgba(30, 30, 30, 0.2) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(20, 20, 20, 0.2) 0%, transparent 50%)'
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%',
            gap: 2,
            opacity: 0.7
          }}>
            <ForumIcon color="primary" sx={{ fontSize: 48 }} />
            <Typography variant="body1" color="text.secondary" align="center">
              Ask me about hotels, travel plans, or room availability.
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              Try: "Find hotels in Paris for 2 adults from June 10 to June 15"
            </Typography>
          </Box>
        ) : (
          <MessageList messages={messages} />
        )}
        <div ref={messagesEndRef} />
      </Box>
      
      {/* Input area */}
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        background: 'rgba(18, 18, 18, 0.8)'
      }}>
        <form onSubmit={sendMessage} style={{ display: 'flex', gap: '8px' }}>
          <TextField
            fullWidth
            placeholder="Ask about hotels, provide dates and guests..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!isConnected || isLoading}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '24px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.07)',
                },
                '& fieldset': {
                  borderColor: 'rgba(144, 202, 249, 0.2)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(144, 202, 249, 0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                }
              },
              '& .MuiInputBase-input': {
                padding: '10px 14px',
              }
            }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    edge="end"
                    color="primary"
                    disabled={!isConnected}
                    sx={{ mr: -0.5 }}
                  >
                    <MicIcon fontSize="small" />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button 
            type="submit" 
            variant="contained" 
            color="primary" 
            disabled={!isConnected || isLoading || input.trim() === ''}
            sx={{ 
              borderRadius: '24px',
              minWidth: '56px',
              width: '56px',
              height: '40px',
              p: 0
            }}
          >
            {isLoading ? (
              <CircularProgress size={24} color="inherit" />
            ) : (
              <SendIcon />
            )}
          </Button>
        </form>
        
        <Fade in={!isConnected}>
          <Typography variant="body2" color="error" sx={{ mt: 1, textAlign: 'center' }}>
            {isReconnecting ? 'Trying to reconnect to server...' : 'Disconnected from server'}
          </Typography>
        </Fade>
      </Box>
    </Paper>
  );
};

export default ChatInterface; 