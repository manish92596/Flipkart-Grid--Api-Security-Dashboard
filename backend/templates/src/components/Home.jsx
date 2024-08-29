import React from 'react';
import { Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Box, Container } from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faShieldHalved } from '@fortawesome/free-solid-svg-icons';

function Home() {
  return (
    <Box
      sx={{
        backgroundImage: 'url(/background.png)', // Use the image from the public folder
        backgroundSize: 'cover', // Cover the entire container
        backgroundPosition: 'center', // Center the image
        backgroundRepeat: 'no-repeat', // Prevent the image from repeating
        height: '100vh',
        width: '100vw',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column', // Stack navbar and content vertically
        color: '#ffffff',
        overflowX: 'hidden', // Prevent horizontal scrolling
      }}
    >
      {/* Transparent Navbar */}
      <AppBar 
        position="static" 
        sx={{ 
          backgroundColor: 'transparent', // Make navbar transparent
          boxShadow: 'none', // Remove shadow
          width: '100%', // Ensure it spans the full width
          maxWidth: '1200px', // Keep it within container's width
        }}
      >
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            API Security
          </Typography>
          <Button 
            component={Link} 
            to="/" 
            sx={{ 
              color: '#ffffff', 
              '&:hover': {
                color: '#c101fb', // Change hover color to match the "Security" word color
              }
            }}
          >
            Home
          </Button>
          <Button 
            component={Link} 
            to="/dashboard" 
            sx={{ 
              color: '#ffffff', 
              '&:hover': {
                color: '#c101fb', // Change hover color to match the "Security" word color
              }
            }}
          >
            Dashboard
          </Button>
          <Button 
            component={Link} 
            to="/about" 
            sx={{ 
              color: '#ffffff', 
              '&:hover': {
                color: '#c101fb', // Change hover color to match the "Security" word color
              }
            }}
          >
            About Us
          </Button>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container 
        maxWidth="md" 
        sx={{ 
          textAlign: 'center',
          flexGrow: 1, // Ensures the container grows to fill available space
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <Typography variant="h2" sx={{ fontWeight: 'bold', marginBottom: '1rem' }}>
          API <span style={{ color: '#c101fb' }}>Security </span><FontAwesomeIcon icon={faShieldHalved} />
        </Typography>
        <Typography variant="h6" sx={{ marginBottom: '2rem' }}>
          Instant API security to inventory APIs, understand exposure, and achieve compliance.
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            component={Link}
            to="/apis"
            variant="contained"
            sx={{
              background: 'linear-gradient(90deg, #ff6a00, #ee0979)',
              padding: '10px 30px',
              fontSize: '1rem',
              fontWeight: 'bold',
              transition: 'all 1s ease',
              '&:hover': {
                color: 'black',
                background: 'linear-gradient(90deg, #ee0979, #ff6a00)',
              }
            }}
          >
            Show All APIs
          </Button>
          <Button
            component={Link}
            to="/vulnerabilities"
            variant="outlined"
            sx={{
              border: '2px solid',
              borderImageSlice: 1,
              borderImageSource: 'linear-gradient(90deg, #ff6a00, #ee0979)',
              color: '#ffffff',
              backgroundColor: 'transparent',
              fontSize: '1rem',
              fontWeight: 'bold',
              transition: 'all 1s ease',
              '&:hover': {
                color: '#000',
                background: 'linear-gradient(90deg, #ff6a00, #ee0979)'
              },
            }}
          >
            Show Vulnerabilities
          </Button>
        </Box>
      </Container>
    </Box>
  );
}

export default Home;
