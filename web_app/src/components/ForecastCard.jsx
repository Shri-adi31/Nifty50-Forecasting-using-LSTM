import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts';
import axios from 'axios';
import { format } from 'date-fns';

const ForecastCard = () => {
  const [forecastType, setForecastType] = useState('7-day');
  const [combinedData, setCombinedData] = useState([]);
  const [lastHistoricalIndex, setLastHistoricalIndex] = useState(null);

  // Function to fetch data from the FastAPI backend
  const fetchForecastData = async (type) => {
    const endpoint = type === '7-day' ? '/api/forecast_7day' : '/api/forecast_1day';
    try {
      // Use environment variable for the API base URL
      const response = await axios.post(`${process.env.REACT_APP_API_BASE_URL}${endpoint}`);
      const { historical_data, forecast } = response.data;

      // Process historical data
      const processedHistoricalData = historical_data.map(item => ({
        timestamp: format(new Date(item.timestamp), 'yyyy-MM-dd'),
        close: item.close,
        isForecast: false,
      }));

      // Process forecast data by adding the dates incrementally
      const lastDate = new Date(processedHistoricalData[processedHistoricalData.length - 1].timestamp);
      const processedForecastData = forecast.map((item, index) => {
        const forecastDate = new Date(lastDate);
        forecastDate.setDate(forecastDate.getDate() + (index + 1));
        return {
          timestamp: format(forecastDate, 'yyyy-MM-dd'),
          close: item,
          isForecast: true,
        };
      });

      // Combine historical and forecast data
      const combinedData = [...processedHistoricalData, ...processedForecastData];

      // Set the combined data for charting and the last index of historical data
      setCombinedData(combinedData);
      setLastHistoricalIndex(processedHistoricalData.length - 1);
    } catch (error) {
      console.error("Error fetching forecast data:", error);
    }
  };

  // Handle forecast type change
  const handleForecastChange = (event, newForecastType) => {
    if (newForecastType) {
      setForecastType(newForecastType);
      fetchForecastData(newForecastType);
    }
  };

  const minValue = combinedData.length ? Math.floor(Math.min(...combinedData.map(item => item.close))) : 0;
  const maxValue = combinedData.length ? Math.ceil(Math.max(...combinedData.map(item => item.close))) : 0;

  // Fetch default forecast data on component mount
  useEffect(() => {
    fetchForecastData('7-day');
  }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5">Nifty50 Forecast</Typography>
        <ToggleButtonGroup
          value={forecastType}
          exclusive
          onChange={handleForecastChange}
          aria-label="forecast type"
          style={{ marginBottom: '1rem' }}
        >
          <ToggleButton value="7-day">7-Day Forecast</ToggleButton>
          <ToggleButton value="2-day">2-Day Forecast</ToggleButton>
        </ToggleButtonGroup>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={combinedData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" />
            <YAxis domain={[minValue, maxValue]} />
            <Tooltip />

            {/* Historical and Forecast Data Line */}
            <Line
              type="monotone"
              dataKey="close"
              stroke="#8884d8"
              name="Price"
              dot={false}
              isAnimationActive={false}
            />

            {/* Forecast Area Shading */}
            <ReferenceArea
              x1={combinedData[lastHistoricalIndex + 1]?.timestamp}
              x2={combinedData[combinedData.length - 1]?.timestamp}
              fill="#82ca9d"
              fillOpacity={0.3}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default ForecastCard;
