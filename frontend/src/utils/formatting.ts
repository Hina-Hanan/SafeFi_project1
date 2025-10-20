export const formatPercent = (value: number, digits = 1) => `${(value * 100).toFixed(digits)}%`
export const formatScore = (value: number, digits = 3) => value.toFixed(digits)
export const riskColor = (level: 'low' | 'medium' | 'high') => {
  switch (level) {
    case 'low':
      return '#2e7d32'
    case 'medium':
      return '#ed6c02'
    case 'high':
      return '#d32f2f'
  }
}







