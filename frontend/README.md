# DeFi Risk Assessment Frontend

A comprehensive, responsive React dashboard for DeFi protocol risk assessment with real-time data visualization, ML model management, and portfolio analysis.

## 🚀 Features

### 📊 **Protocol Heatmap**
- Interactive visual representation of all protocols
- Color-coded risk levels (Low/Medium/High)
- Real-time TVL, volume, and price change data
- Click-to-select for detailed analysis
- Sortable by risk score, TVL, volume, or price change
- Filterable by risk level

### 📈 **Risk Analysis Dashboard**
- Detailed risk score visualization with timeline charts
- Risk trend analysis with 7d/30d/90d time ranges
- Volatility and liquidity score breakdowns
- Interactive risk score timeline
- Real-time data updates

### 🤖 **ML Model Management**
- Train ML models with one-click functionality
- Real-time model performance metrics (F1, Accuracy, Precision, Recall)
- Model version comparison and tracking
- Performance visualization with progress bars
- Model status monitoring

### 💼 **Portfolio Analyzer**
- Multi-protocol portfolio risk assessment
- Weighted risk score calculation
- Risk distribution analysis
- Interactive protocol selection
- Comprehensive protocol comparison table
- Real-time portfolio metrics

### 🚨 **Alert Management System**
- Configurable alert rules and thresholds
- Real-time alert notifications
- Alert acknowledgment system
- Alert history tracking
- Alert statistics dashboard

### 📱 **Responsive Design**
- Mobile-first approach
- Tablet and desktop optimized
- Touch-friendly interface
- Adaptive layouts for all screen sizes

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Material-UI (MUI) v6** - Component library and theming
- **React Query (TanStack Query)** - Server state management
- **Axios** - HTTP client for API communication
- **Vite** - Fast build tool and dev server

## 📦 Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### API Integration
The frontend connects to the backend API endpoints:
- `/protocols` - Protocol data
- `/risk/protocols/{id}/risk-details` - Risk analysis
- `/models/train` - ML model training
- `/models/performance` - Model metrics
- `/health` - System health status

## 🎨 UI Components

### Core Components
- **ProtocolHeatmap** - Interactive protocol visualization
- **RiskChart** - Risk score timeline and analysis
- **ModelMetrics** - ML model performance dashboard
- **PortfolioAnalyzer** - Portfolio risk assessment
- **AlertManager** - Alert system management
- **RiskMetricsCards** - System overview metrics

### Design System
- **Light theme** with professional color palette
- **Consistent spacing** and typography
- **Card-based layout** with subtle shadows
- **Responsive grid system** for all screen sizes
- **Interactive elements** with hover states and animations

## 📊 Data Flow

1. **Real-time Updates**: Components automatically refresh every 30 seconds
2. **Error Handling**: Graceful error states with retry functionality
3. **Loading States**: Skeleton loaders and progress indicators
4. **Caching**: React Query provides intelligent caching and background updates

## 🔄 State Management

- **React Query** for server state (API data)
- **React useState** for local component state
- **React Context** for global application state (if needed)

## 📱 Responsive Breakpoints

- **Mobile**: < 600px
- **Tablet**: 600px - 960px
- **Desktop**: > 960px
- **Large Desktop**: > 1200px

## 🎯 Key Features Explained

### Protocol Heatmap
The heatmap provides an at-a-glance view of all protocols with:
- **Color intensity** based on risk score
- **Hover tooltips** with detailed metrics
- **Click interaction** to select protocols
- **Sorting and filtering** options

### Risk Analysis
Detailed risk analysis includes:
- **Timeline visualization** of risk scores over time
- **Trend indicators** showing risk direction
- **Breakdown metrics** for volatility and liquidity
- **Interactive time range** selection

### ML Model Management
Comprehensive ML model oversight:
- **One-click training** with progress tracking
- **Performance metrics** visualization
- **Model comparison** capabilities
- **Status monitoring** and alerts

### Portfolio Analyzer
Advanced portfolio risk assessment:
- **Multi-protocol selection** with chips
- **Weighted risk calculation** based on TVL
- **Risk distribution** analysis
- **Comprehensive comparison** table

## 🚀 Getting Started

1. **Ensure backend is running** on `http://127.0.0.1:8000`
2. **Start the frontend** with `npm run dev`
3. **Open browser** to `http://localhost:5173`
4. **Explore the dashboard** tabs and features

## 🔍 Usage Guide

### Using the Heatmap
1. Click on any protocol card to select it
2. Use the sort dropdown to organize by different metrics
3. Filter by risk level using the filter dropdown
4. Hover over cards to see detailed tooltips

### Analyzing Risk
1. Select a protocol from the heatmap
2. Switch to the "Risk Analysis" tab
3. Adjust the time range (7d/30d/90d)
4. Review the risk score timeline and breakdown

### Managing ML Models
1. Go to the "ML Models" tab
2. Click "Train Models" to start training
3. Monitor performance metrics
4. Compare different model versions

### Portfolio Analysis
1. Navigate to "Portfolio Analyzer"
2. Select protocols using the chip interface
3. View portfolio summary metrics
4. Analyze the protocol comparison table

## 🎨 Customization

### Theming
Modify the theme in `src/main.tsx`:
```typescript
const theme = createTheme({
  palette: {
    mode: 'light', // or 'dark'
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
})
```

### API Configuration
Update API base URL in `src/services/api.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
```

## 🐛 Troubleshooting

### Common Issues

1. **Module not found errors**: Run `npm install` to ensure all dependencies are installed
2. **API connection issues**: Verify backend is running and accessible
3. **Build errors**: Check TypeScript errors and fix any type issues
4. **Performance issues**: Check React Query cache settings and API response times

### Development Tips

- Use React DevTools for component debugging
- Check Network tab for API call issues
- Monitor console for error messages
- Use React Query DevTools for cache inspection

## 📈 Performance

- **Lazy loading** for large datasets
- **Optimistic updates** for better UX
- **Background refetching** for fresh data
- **Efficient re-renders** with React Query
- **Responsive images** and optimized assets

## 🔒 Security

- **Input validation** on all user inputs
- **XSS protection** with React's built-in escaping
- **CSRF protection** via API configuration
- **Secure API communication** (HTTPS in production)

## 📝 Contributing

1. Follow TypeScript best practices
2. Use Material-UI components consistently
3. Implement proper error handling
4. Add loading states for async operations
5. Write responsive, accessible components

## 🎯 Future Enhancements

- **Real-time WebSocket** connections for live updates
- **Advanced charting** with libraries like Chart.js or D3
- **Export functionality** for reports and data
- **User preferences** and customization options
- **Mobile app** with React Native
- **Advanced filtering** and search capabilities

---

**Built with ❤️ for DeFi risk assessment**




