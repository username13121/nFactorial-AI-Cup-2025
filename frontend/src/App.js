import React from 'react';
import { Box, Container, Typography, Paper, useTheme, useMediaQuery } from '@mui/material';
import ChatInterface from './components/ChatInterface';
import HotelIcon from '@mui/icons-material/Hotel';

function App() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #121212 0%, #1a1a1a 100%)',
        backgroundImage: `
          radial-gradient(circle at 10% 20%, rgba(144, 202, 249, 0.1) 0%, transparent 20%),
          radial-gradient(circle at 90% 80%, rgba(156, 39, 176, 0.1) 0%, transparent 20%),
          linear-gradient(135deg, #121212 0%, #1a1a1a 100%)
        `,
        pt: 4,
        pb: 6
      }}
    >
      <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mb: 4,
            gap: 1.5
          }}
        >
          <Box 
            sx={{ 
              p: 1,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, rgba(144, 202, 249, 0.3) 0%, rgba(156, 39, 176, 0.3) 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
            }}
          >
            <HotelIcon color="primary" fontSize="large" />
          </Box>
          
          <Typography 
            variant={isMobile ? "h5" : "h4"} 
            component="h1" 
            align="center" 
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(90deg, #90CAF9 0%, #CE93D8 100%)',
              backgroundClip: 'text',
              textFillColor: 'transparent',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              letterSpacing: '0.5px'
            }}
          >
            Hotel Booking Assistant
          </Typography>
        </Box>
        
        <Paper 
          elevation={10} 
          sx={{ 
            p: { xs: 1, sm: 2 }, 
            flexGrow: 1,
            borderRadius: '16px',
            background: 'linear-gradient(to bottom, rgba(30, 30, 30, 0.9), rgba(18, 18, 18, 0.9))',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)'
          }}
        >
          <ChatInterface />
        </Paper>
        
        <Typography 
          variant="caption" 
          align="center" 
          sx={{ 
            mt: 3, 
            opacity: 0.6,
            color: 'text.secondary'
          }}
        >
          &copy; {new Date().getFullYear()} Hotel Booking Assistant • AI-powered Hotel Search
        </Typography>
      </Container>
    </Box>
  );
}

export default App; 