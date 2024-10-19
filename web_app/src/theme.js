import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#1c1c1e',
      paper: '#2c2c2e',
    },
    primary: {
      main: '#00BFA6',
    },
    secondary: {
      main: '#29B6F6',
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#B0BEC5',
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
});

export default theme;
