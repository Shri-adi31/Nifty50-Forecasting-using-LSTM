import React, { useState } from 'react';
import { Container, Grid, Box, Typography } from '@mui/material';
import { HistoricalDataCard, ForecastCard, DynamicDataModelCard } from './index';

const Dashboard = () => {
    const [hoveredData, setHoveredData] = useState(null);  // State to hold the hovered data

    return (
        <Container 
            maxWidth="lg" 
            disableGutters 
            sx={{ 
                marginTop: '1rem', 
                height: '100vh', 
                padding: '1rem',
                boxSizing: 'border-box',
                overflowY: 'auto',  // Enable vertical scrolling when necessary
                overflowX: 'auto', // Avoid horizontal scrolling
            }}
        >
            <Box sx={{ textAlign: 'center', marginBottom: '1rem' }}>
                <Typography variant="h4">Nifty50 ETF Dashboard</Typography>
            </Box>
            
            <Grid 
                container 
                spacing={2} 
                sx={{ height: 'calc(100% - 64px)', }}
            >
                {/* Historical Data Card */}
                <Grid item xs={12} sm={6} md={4}>
                    <Box sx={{ height: '100%' }}>
                        <HistoricalDataCard setHoveredData={setHoveredData} />
                    </Box>
                </Grid>

                {/* Forecast Card */}
                <Grid item xs={12} sm={6} md={4}>
                    <Box sx={{ height: '100%' }}>
                        <ForecastCard />
                    </Box>
                </Grid>
                
                {/* Dynamic Data Model Card */}
                <Grid item xs={12} sm={12} md={4}>
                    <Box sx={{ height: '100%' }}>
                        <DynamicDataModelCard hoveredData={hoveredData} />
                    </Box>
                </Grid>
            </Grid>
        </Container>
    );
};

export default Dashboard;
