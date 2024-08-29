import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Container, Typography } from '@mui/material';
import APICard from './APICard';
import './APIList.css'; // Import custom CSS for the horizontal scroll and layout
import LoadingComponent from './Loading';

function APIList() {
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:5000/api/routes')
      .then(response => {
        setApis(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('There was an error fetching the API routes!', error);
        setApis([]);
        setLoading(false);
      });
  }, [apis]);

  if (loading) {
    return <LoadingComponent />;
  }

  const totalAPIs = apis.length;

  return (
    <Box
      sx={{
        backgroundImage: 'url(/all_background.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed', // Make the background fixed
        minHeight: '100vh',
        minWidth: '100vw',
        padding: '2rem 0',
        overflowX: 'hidden',
      }}
    >
      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 2 }}>
        <Typography
          variant="h4"
          align="center"
          gutterBottom
          sx={{ marginTop: '2rem', marginBottom: '1rem', color: '#fff' }} // Added marginTop for space above the heading
        >
          List of APIs
        </Typography>
        <Typography
          variant="h6"
          align="center"
          gutterBottom
          sx={{ marginBottom: '2rem', color: '#fff' }}
        >
          Total APIs Found: {totalAPIs}
        </Typography>
        <Box className="horizontal-scroll">
          {Array.isArray(apis) && apis.length > 0 ? (
            apis.map((route, index) => (
              <div className="card-item" key={index}>
                <APICard path={route.path} method={route.methods[0]} />
              </div>
            ))
          ) : (
            <Typography variant="body1" align="center" sx={{ color: '#fff' }}>
              No APIs found.
            </Typography>
          )}
        </Box>
      </Container>
    </Box>
  );
}

export default APIList;
