import React, { useState } from 'react';
import { Card, CardContent, Typography, Button, TextField } from '@mui/material';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Bar, Line, ComposedChart, Legend } from 'recharts';
import axios from 'axios';
import { DatePicker } from '@mui/x-date-pickers';
import { format } from 'date-fns';

const HistoricalDataCard = ({ setHoveredData }) => {
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [data, setData] = useState([]);
    const [cumulativeReturn, setCumulativeReturn] = useState(null);

    const fetchHistoricalData = async () => {
        if (startDate && endDate) {
            const formattedStartDate = format(startDate, 'yyyy-MM-dd');
            const formattedEndDate = format(endDate, 'yyyy-MM-dd');

            try {
                // Use environment variable for API base URL
                const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/historical`, {
                    params: { start: formattedStartDate, end: formattedEndDate },
                });
                
                const fetchedData = response.data;
                setData(fetchedData);

                // Calculate Cumulative Return
                if (fetchedData.length > 0) {
                    const initialPrice = fetchedData[0].close;
                    const finalPrice = fetchedData[fetchedData.length - 1].close;
                    const cumulativeReturn = ((finalPrice - initialPrice) / initialPrice) * 100;
                    setCumulativeReturn(cumulativeReturn.toFixed(2));  // Round to 2 decimal places
                }
            } catch (error) {
                console.error("Error fetching historical data:", error);
            }
        }
    };

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length && payload[0]) {
            const hoveredData = payload[0].payload;  // Full data of the hovered point
            setHoveredData(hoveredData);

            return (
                <div style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>
                    <Typography variant="body2">Date: {hoveredData.timestamp}</Typography>
                    <Typography variant="body2">Close: {hoveredData.close}</Typography>
                    <Typography variant="body2">Volume: {hoveredData.volume}</Typography>
                </div>
            );
        }
        return null;
    };

    return (
        <Card>
            <CardContent>
                <Typography variant="h5">Historical Data</Typography>
                <DatePicker
                    label="Start Date"
                    value={startDate}
                    onChange={(newValue) => setStartDate(newValue)}
                    renderInput={(params) => <TextField {...params} />}
                />
                <DatePicker
                    label="End Date"
                    value={endDate}
                    onChange={(newValue) => setEndDate(newValue)}
                    renderInput={(params) => <TextField {...params} />}
                />
                <Button variant="contained" onClick={fetchHistoricalData}>Fetch Data</Button>

                <ResponsiveContainer width="100%" height={250}>
                    <ComposedChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis yAxisId="left" domain={['auto', 'auto']} />
                        <YAxis yAxisId="right" orientation="right" domain={['auto', 'auto']} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />

                        {/* Closing Price Line */}
                        <Line
                            yAxisId="left"
                            type="monotone"
                            dataKey="close"
                            stroke="#8884d8"
                            dot={false}
                            name="Closing Price"
                        />

                        {/* Volume Bar */}
                        <Bar
                            yAxisId="right"
                            dataKey="volume"
                            fill="#82ca9d"
                            name="Volume"
                        />
                    </ComposedChart>
                </ResponsiveContainer>

                {/* Display Cumulative Return */}
                {cumulativeReturn !== null && (
                    <Typography variant="h6" style={{ marginTop: '1rem' }}>
                        Cumulative Return: {cumulativeReturn}%
                    </Typography>
                )}
            </CardContent>
        </Card>
    );
};

export default HistoricalDataCard;
