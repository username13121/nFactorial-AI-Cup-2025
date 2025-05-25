import React from 'react';
import { Box, Paper, Typography, Chip, Avatar, Fade } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ComputerIcon from '@mui/icons-material/Computer';
import HotelMessage from './HotelMessage';

const MessageList = ({ messages }) => {
  return (
    <>
      {messages.map((message, index) => (
        <Fade in={true} key={index} timeout={300} style={{ transitionDelay: `${index % 3 * 50}ms` }}>
          <Box>
            <Message message={message} isLast={index === messages.length - 1} />
          </Box>
        </Fade>
      ))}
    </>
  );
};

const Message = ({ message, isLast }) => {
  const { role, content, data } = message;
  
  let backgroundColor, icon, textColor, borderColor, avatarBg;
  switch (role) {
    case 'user':
      backgroundColor = 'rgba(25, 118, 210, 0.12)';
      borderColor = 'rgba(25, 118, 210, 0.3)';
      icon = <PersonIcon />;
      textColor = '#fff';
      avatarBg = '#1976d2';
      break;
    case 'assistant':
      backgroundColor = 'rgba(45, 45, 45, 0.7)';
      borderColor = 'rgba(255, 255, 255, 0.1)';
      icon = <SmartToyIcon />;
      textColor = '#fff';
      avatarBg = '#9c27b0';
      break;
    case 'system':
      backgroundColor = 'rgba(245, 124, 0, 0.12)';
      borderColor = 'rgba(245, 124, 0, 0.3)';
      icon = <ComputerIcon />;
      textColor = '#fff';
      avatarBg = '#f57c00';
      break;
    default:
      backgroundColor = 'rgba(45, 45, 45, 0.7)';
      borderColor = 'rgba(255, 255, 255, 0.1)';
      icon = <SmartToyIcon />;
      textColor = '#fff';
      avatarBg = '#9c27b0';
  }

  // Create a unique animation name for the typing indicator
  const typingAnimationName = `typing-${Math.random().toString(36).substring(7)}`;

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: role === 'user' ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        mb: 1.5,
        gap: 1.5
      }}
    >
      {/* Avatar */}
      <Avatar
        sx={{ 
          bgcolor: avatarBg,
          width: 36,
          height: 36,
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
        }}
      >
        {icon}
      </Avatar>
      
      {/* Message bubble */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2, 
          backgroundColor,
          borderLeft: role !== 'user' ? `3px solid ${borderColor}` : 'none',
          borderRight: role === 'user' ? `3px solid ${borderColor}` : 'none',
          maxWidth: 'calc(100% - 50px)', 
          borderRadius: role === 'user' ? '12px 4px 12px 12px' : '4px 12px 12px 12px',
          position: 'relative',
          color: textColor,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          overflow: 'hidden'
        }}
      >
        {/* Role indicator */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography 
            variant="caption" 
            sx={{ 
              fontWeight: 'bold', 
              color: role === 'user' ? 'primary.light' : role === 'system' ? 'warning.light' : 'secondary.light',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              fontSize: '0.7rem'
            }}
          >
            {role}
          </Typography>
          
          {/* Typing animation for the last assistant message */}
          {isLast && role === 'assistant' && (
            <Box sx={{ 
              display: 'flex', 
              ml: 1.5, 
              alignItems: 'center',
              '@keyframes typing': {
                '0%': { transform: 'translateY(0px)' },
                '28%': { transform: 'translateY(-3px)' },
                '44%': { transform: 'translateY(0px)' }
              }
            }}>
              {[0, 1, 2].map(i => (
                <Box 
                  key={i}
                  sx={{
                    width: 4,
                    height: 4,
                    backgroundColor: 'primary.light',
                    borderRadius: '50%',
                    mx: 0.25,
                    animation: `${typingAnimationName} 1.5s infinite`,
                    animationDelay: `${i * 0.15}s`,
                    '@keyframes [typing-animation-name]': {
                      '0%': { transform: 'translateY(0px)' },
                      '28%': { transform: 'translateY(-3px)' },
                      '44%': { transform: 'translateY(0px)' }
                    }
                  }}
                />
              ))}
            </Box>
          )}
        </Box>
        
        {/* Message content */}
        <Typography 
          variant="body1" 
          component="div" 
          sx={{ 
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            '& a': {
              color: 'primary.light',
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline'
              }
            }
          }}
        >
          {content}
        </Typography>
        
        {/* Additional data components */}
        {data && content.includes('find_hotels') && (
          <HotelMessage data={data} />
        )}
      </Paper>
    </Box>
  );
};

export default MessageList; 