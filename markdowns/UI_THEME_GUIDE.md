# Dark Theme UI Guide

## Overview
The DeFi Risk Assessment Dashboard has been transformed with an impressive cyberpunk-inspired dark theme featuring glassmorphism, gradients, and animated effects.

## Color Palette

### Primary Colors
- **Primary Blue**: `#6366f1` (Indigo)
- **Secondary Pink**: `#ec4899` (Hot Pink)
- **Background Dark**: `#0a0e27` (Deep Navy)
- **Paper Background**: `rgba(15, 23, 42, 0.8)` with blur

### Accent Colors
- **Success Green**: `#10b981`
- **Warning Orange**: `#f59e0b`
- **Error Red**: `#ef4444`
- **Info Cyan**: `#06b6d4`

## Button Styles

### 1. Gradient Contained Buttons
- **Style**: Linear gradient from indigo to pink
- **Effect**: Shine animation on hover
- **Shadow**: Glowing box-shadow
- **Use Case**: Primary actions

```tsx
<Button variant="contained">
  Primary Action
</Button>
```

### 2. Outlined Neon Buttons
- **Style**: 2px border with transparent background
- **Effect**: Glow effect on hover
- **Shadow**: Neon glow
- **Use Case**: Secondary actions

```tsx
<Button variant="outlined">
  Secondary Action
</Button>
```

### 3. Icon Buttons
- **Style**: Glassmorphism with backdrop blur
- **Effect**: Rotate 180° on hover with glow
- **Background**: Semi-transparent with border
- **Use Case**: Actions in header/cards

```tsx
<IconButton>
  <RefreshIcon />
</IconButton>
```

### 4. Custom Gradient Buttons (in components)
Each icon button can have custom colors:
- **Notifications**: Pink gradient with pink glow
- **Settings**: Blue gradient with blue glow
- **Refresh**: Cyan gradient with cyan glow

## Card Styles

### Standard Cards
- **Background**: Linear gradient overlay on semi-transparent dark
- **Border**: 1px solid with primary color at 10% opacity
- **Blur**: 20px backdrop filter
- **Shadow**: Multi-layer shadows with glow
- **Hover**: Lift effect with enhanced glow

### Protocol Cards (Heatmap)
- **Background**: Dynamic gradient based on risk level
- **Border**: Risk color at 50% opacity
- **Effect**: Shimmer animation on hover
- **Scale**: 1.05 scale with translateY on hover
- **Shadow**: Risk-colored glow shadow

### Metric Cards
- **Top Border**: 4px gradient bar with glow
- **Icon Box**: Gradient background with shadow
- **Text**: Gradient text for values
- **Background**: Subtle gradient matching card color

## Typography

### Font Family
- Primary: "Inter" (Google Fonts)
- Fallback: Roboto, Helvetica, Arial, sans-serif

### Heading Styles
- **Gradient Text**: Background clip text with gradient
- **Font Weight**: 600-700 for headings
- **Letter Spacing**: -0.02em for tight headings

### Button Text
- **Font Weight**: 600
- **Text Transform**: none (no uppercase)
- **Letter Spacing**: 0.02em

## Effects & Animations

### Glassmorphism
- Backdrop filter with 10-20px blur
- Semi-transparent backgrounds (rgba with low alpha)
- Border with subtle color

### Gradient Animations
```css
background: linear-gradient(135deg, #6366f1 0%, #ec4899 100%)
```

### Hover Animations
1. **Scale & Translate**: `transform: scale(1.05) translateY(-4px)`
2. **Rotate**: `transform: rotate(180deg)` for icons
3. **Glow**: Enhanced box-shadow with color
4. **Shimmer**: Sliding gradient overlay

### Pulse Animation
Used for the logo in header:
```css
@keyframes pulse {
  0%, 100%: { boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)' }
  50%: { boxShadow: '0 0 30px rgba(99, 102, 241, 0.8)' }
}
```

## Component-Specific Styling

### Header (AppBar)
- Semi-transparent dark background
- Blur effect
- Gradient border bottom
- Logo with pulse animation
- Gradient text for title

### Tabs
- Selected tab with gradient text and text-shadow
- Gradient indicator bar with glow
- Hover effects with color transitions

### Alerts
- Gradient background matching severity
- Border with matching color
- Backdrop blur

### Form Controls (Select/Input)
- Glassmorphism background
- Colored borders matching context
- Hover effect with enhanced border

### Footer
- Gradient background
- Colored chips for metrics
- Border top with glow

## Accessibility
- High contrast ratios maintained
- Focus states preserved
- ARIA labels in place
- Keyboard navigation supported

## Performance
- CSS transitions instead of JavaScript animations
- Hardware-accelerated transforms
- Efficient backdrop-filter usage
- Optimized gradient rendering

## Browser Support
- Modern browsers with backdrop-filter support
- Fallbacks for older browsers (gradients still work)
- Progressive enhancement approach





