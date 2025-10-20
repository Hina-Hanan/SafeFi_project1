// Dark theme color utility - minimal colors
// Black & White theme with only Green/Orange/Red for risks

export const getRiskColor = (riskLevel: string, variant: 'background' | 'border' | 'text' = 'background') => {
  const colors = {
    low: {
      background: '#001A00',  // Very dark green
      border: '#00CC00',      // Green
      text: '#00CC00',        // Green
    },
    medium: {
      background: '#1A0A00',  // Very dark orange
      border: '#FF6600',      // Orange
      text: '#FF6600',        // Orange
    },
    high: {
      background: '#1A0000',  // Very dark red
      border: '#FF0000',      // Red
      text: '#FF0000',        // Red
    },
    unknown: {
      background: '#0A0A0A',  // Very dark gray
      border: '#333333',      // Dark gray
      text: '#666666',        // Gray
    },
  };

  const level = riskLevel.toLowerCase();
  const colorSet = colors[level as keyof typeof colors] || colors.unknown;
  return colorSet[variant];
};

export const getRiskColorByScore = (score: number, variant: 'background' | 'border' | 'text' = 'background') => {
  if (score < 40) return getRiskColor('low', variant);
  if (score < 70) return getRiskColor('medium', variant);
  return getRiskColor('high', variant);
};

export const getStatusColor = (isHealthy: boolean, variant: 'background' | 'border' | 'text' = 'background') => {
  if (isHealthy) {
    return {
      background: '#001A00',
      border: '#00CC00',
      text: '#00CC00',
    }[variant];
  }
  return {
    background: '#1A0000',
    border: '#FF0000',
    text: '#FF0000',
  }[variant];
};

// Dark theme colors - minimal palette
export const colors = {
  white: '#FFFFFF',
  black: '#000000',
  darkGray: '#0A0A0A',
  gray: '#333333',
  lightGray: '#666666',
  textGray: '#AAAAAA',
  // Only colors for risks:
  green: '#00CC00',
  greenDark: '#001A00',
  orange: '#FF6600',
  orangeDark: '#1A0A00',
  red: '#FF0000',
  redDark: '#1A0000',
  // Remove all other colors
  blueLight: '#0A0A0A',  // No blue, use dark gray
  blueDark: '#0A0A0A',
  grayBorder: '#222222',
  grayText: '#AAAAAA',
};

