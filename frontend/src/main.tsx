import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import Dashboard from './pages/Dashboard'

// Dark theme with black background - minimal colors
// Only use colors for risk indicators: Green (safe), Orange (medium), Red (danger)
const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#000000',  // Pure black background
      paper: '#0A0A0A',    // Very dark gray for cards
    },
    text: {
      primary: '#FFFFFF',   // White text
      secondary: '#AAAAAA', // Light gray text
    },
    primary: { 
      main: '#FFFFFF',      // White for primary elements
      light: '#FFFFFF',
      dark: '#CCCCCC',
    },
    secondary: { 
      main: '#666666',      // Gray for secondary elements
      light: '#888888',
      dark: '#444444',
    },
    success: {
      main: '#00CC00',      // Green (stable/low risk)
      light: '#00FF00',
      dark: '#009900',
    },
    warning: {
      main: '#FF6600',      // Orange (medium risk)
      light: '#FF9933',
      dark: '#CC5200',
    },
    error: {
      main: '#FF0000',      // Red (high risk/danger)
      light: '#FF3333',
      dark: '#CC0000',
    },
    info: {
      main: '#FFFFFF',      // White for info
      light: '#FFFFFF',
      dark: '#CCCCCC',
    },
  },
  shape: { 
    borderRadius: 4,  // Minimal border radius for flat design
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: '#000000',  // Pure black
          color: '#FFFFFF',       // White text
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: '#0A0A0A',  // Very dark gray
          border: '2px solid #222222',  // Dark gray border
          boxShadow: 'none',
          borderRadius: '4px',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          padding: '10px 24px',
          boxShadow: 'none',  // No shadow
          '&:hover': {
            boxShadow: 'none',  // No shadow on hover
          },
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        outlined: {
          borderWidth: 2,
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          border: '2px solid #333333',
          background: '#0A0A0A',
          color: '#FFFFFF',
          '&:hover': {
            background: '#1A1A1A',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          borderRadius: 4,
          border: '2px solid #333333',
          boxShadow: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: '#000000',  // Black header
          borderBottom: '2px solid #222222',  // Dark border
          boxShadow: 'none',
          color: '#FFFFFF',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '1rem',
          minHeight: 48,
          color: '#AAAAAA',
          '&.Mui-selected': {
            color: '#FFFFFF',
            background: 'transparent',
          },
          '&:hover': {
            background: '#1A1A1A',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          background: '#0A0A0A',  // Very dark gray
          border: '2px solid #222222',  // Dark border
          boxShadow: 'none',
          borderRadius: 4,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          border: '2px solid',
          boxShadow: 'none',
        },
        standardError: {
          background: '#1A0000',  // Very dark red
          borderColor: '#FF0000',  // Red border
          color: '#FFFFFF',
        },
        standardSuccess: {
          background: '#001A00',  // Very dark green
          borderColor: '#00CC00',  // Green border
          color: '#FFFFFF',
        },
        standardWarning: {
          background: '#1A0A00',  // Very dark orange
          borderColor: '#FF6600',  // Orange border
          color: '#FFFFFF',
        },
        standardInfo: {
          background: '#0A0A0A',  // Dark gray
          borderColor: '#666666',  // Gray border
          color: '#FFFFFF',
        },
      },
    },
  },
})

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <Dashboard />
      </QueryClientProvider>
    </ThemeProvider>
  </React.StrictMode>
)



