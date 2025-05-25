import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardMedia, 
  Chip, 
  Button, 
  Collapse,
  Rating,
  Divider,
  Avatar
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import HotelIcon from '@mui/icons-material/Hotel';
import WifiIcon from '@mui/icons-material/Wifi';
import LocalParkingIcon from '@mui/icons-material/LocalParking';
import AcUnitIcon from '@mui/icons-material/AcUnit';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import PoolIcon from '@mui/icons-material/Pool';

const HotelMessage = ({ data }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Parse the data if it's a string
  let hotelData;
  try {
    hotelData = typeof data === 'string' ? JSON.parse(data) : data;
  } catch (error) {
    return (
      <Box mt={2}>
        <Typography color="error">Error parsing hotel data</Typography>
      </Box>
    );
  }
  
  // Check if data has a valid format
  if (!hotelData || !Array.isArray(hotelData.hotels)) {
    return (
      <Box mt={2}>
        <Typography>No hotels found or invalid data format</Typography>
      </Box>
    );
  }
  
  const { hotels } = hotelData;
  
  // Show only first 3 hotels when collapsed
  const displayedHotels = expanded ? hotels : hotels.slice(0, 3);
  
  return (
    <Box mt={3} sx={{ width: '100%' }}>
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        mb: 2,
        gap: 1,
        backgroundColor: 'rgba(144, 202, 249, 0.1)',
        p: 1.5,
        borderRadius: '8px'
      }}>
        <HotelIcon color="primary" />
        <Typography variant="subtitle1" fontWeight="medium" color="primary">
          Found {hotels.length} hotels matching your criteria
        </Typography>
      </Box>
      
      <Grid container spacing={2}>
        {displayedHotels.map((hotel, index) => (
          <Grid item xs={12} key={index}>
            <HotelCard hotel={hotel} />
          </Grid>
        ))}
      </Grid>
      
      {hotels.length > 3 && (
        <Button 
          fullWidth 
          startIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          onClick={() => setExpanded(!expanded)}
          sx={{ 
            mt: 2,
            py: 1,
            borderRadius: '8px',
            background: expanded ? 'rgba(144, 202, 249, 0.08)' : 'rgba(144, 202, 249, 0.15)',
            '&:hover': {
              background: expanded ? 'rgba(144, 202, 249, 0.15)' : 'rgba(144, 202, 249, 0.25)',
            }
          }}
          variant="outlined"
          color="primary"
        >
          {expanded ? 'Show Less' : `Show ${hotels.length - 3} More Hotels`}
        </Button>
      )}
    </Box>
  );
};

// Map amenities to icons
const getAmenityIcon = (amenity) => {
  const amenityLower = amenity.toLowerCase();
  if (amenityLower.includes('wifi') || amenityLower.includes('internet')) return <WifiIcon fontSize="small" />;
  if (amenityLower.includes('parking')) return <LocalParkingIcon fontSize="small" />;
  if (amenityLower.includes('ac') || amenityLower.includes('air') || amenityLower.includes('climate')) return <AcUnitIcon fontSize="small" />;
  if (amenityLower.includes('restaurant') || amenityLower.includes('breakfast') || amenityLower.includes('food')) return <RestaurantIcon fontSize="small" />;
  if (amenityLower.includes('pool') || amenityLower.includes('swim')) return <PoolIcon fontSize="small" />;
  return null;
};

const HotelCard = ({ hotel }) => {
  const { 
    name, 
    starRating = 0,
    pricePerNight = 'N/A',
    address = {},
    description = 'No description available',
    amenities = []
  } = hotel;
  
  // Placeholder image if none is provided
  const imageUrl = hotel.image || 'https://via.placeholder.com/300x200?text=Hotel+Image';
  
  return (
    <Card 
      variant="outlined" 
      sx={{ 
        borderRadius: '12px', 
        backgroundColor: 'rgba(30, 30, 30, 0.7)', 
        borderColor: 'rgba(255, 255, 255, 0.1)',
        overflow: 'hidden',
        transition: 'transform 0.3s, box-shadow 0.3s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.3)'
        }
      }}
    >
      <Grid container>
        <Grid item xs={12} md={4} sx={{ position: 'relative' }}>
          <CardMedia
            component="img"
            height="100%"
            image={imageUrl}
            alt={name}
            sx={{ 
              height: '100%', 
              minHeight: { xs: '200px', md: '100%' },
              objectFit: 'cover'
            }}
          />
          <Box 
            sx={{ 
              position: 'absolute', 
              top: 10, 
              left: 10, 
              backgroundColor: 'rgba(0,0,0,0.7)', 
              borderRadius: '4px',
              px: 1,
              py: 0.5
            }}
          >
            <Rating value={parseFloat(starRating)} readOnly precision={0.5} size="small" />
          </Box>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" component="div" color="primary" fontWeight="bold" gutterBottom>
              {name}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <LocationOnIcon color="action" fontSize="small" sx={{ mr: 0.5 }} />
              <Typography variant="body2" color="text.secondary">
                {address.street ? `${address.street}, ` : ''}
                {address.city ? `${address.city}, ` : ''}
                {address.country || ''}
              </Typography>
            </Box>
            
            <Divider sx={{ my: 1.5 }} />
            
            <Typography variant="body2" sx={{ mb: 2, flexGrow: 1 }}>
              {description.length > 150 ? `${description.substring(0, 150)}...` : description}
            </Typography>
            
            <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 0.8 }}>
              {amenities.slice(0, 5).map((amenity, index) => {
                const icon = getAmenityIcon(amenity);
                return (
                  <Chip 
                    key={index} 
                    label={amenity} 
                    size="small" 
                    color="secondary" 
                    variant="outlined"
                    icon={icon}
                    sx={{ 
                      borderRadius: '4px',
                      '& .MuiChip-label': {
                        fontSize: '0.75rem'
                      }
                    }}
                  />
                );
              })}
              {amenities.length > 5 && (
                <Chip 
                  label={`+${amenities.length - 5} more`} 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                  sx={{ borderRadius: '4px' }}
                />
              )}
            </Box>
            
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              alignItems: 'center',
              backgroundColor: 'rgba(144, 202, 249, 0.1)',
              borderRadius: '8px',
              p: 1.5
            }}>
              <Typography variant="h6" color="primary" fontWeight="bold">
                {typeof pricePerNight === 'object' 
                  ? `${pricePerNight.currency || '$'}${pricePerNight.amount || 'N/A'}`
                  : pricePerNight}
                <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                  / night
                </Typography>
              </Typography>
              
              <Button 
                variant="contained" 
                color="primary" 
                size="small"
                sx={{ 
                  borderRadius: '8px',
                  textTransform: 'none',
                  fontWeight: 'bold'
                }}
              >
                View Details
              </Button>
            </Box>
          </CardContent>
        </Grid>
      </Grid>
    </Card>
  );
};

export default HotelMessage; 