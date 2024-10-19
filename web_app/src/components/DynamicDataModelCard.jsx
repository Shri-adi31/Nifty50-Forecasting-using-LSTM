import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const DynamicDataModelCard = ({ hoveredData }) => {
    return (
        <Card>
            <CardContent>
                <Typography variant="h5">Infomation</Typography>
                {hoveredData ? (
                    <>
                        <Typography variant="body2">Date: {hoveredData.timestamp}</Typography>
                        <Typography variant="body2">Open: {hoveredData.open}</Typography>
                        <Typography variant="body2">Close: {hoveredData.close}</Typography>
                        <Typography variant="body2">High: {hoveredData.high}</Typography>
                        <Typography variant="body2">Low: {hoveredData.low}</Typography>
                        <Typography variant="body2">P/E Ratio: {hoveredData.pe_ratio}</Typography>
                    </>
                ) : (
                    <Typography variant="body2">Hover over a point in the chart to see the details here.</Typography>
                )}
            </CardContent>
        </Card>
    );
};

export default DynamicDataModelCard;
