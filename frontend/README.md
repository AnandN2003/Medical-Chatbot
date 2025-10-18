# Medical Chatbot Frontend

A beautiful, modern React frontend for the Medical Chatbot application with a sleek black and blue theme.

## Features

### 🎨 Landing Page
- Stylish loading animation with smooth motion effects
- Dark gradient background (black/blue) with futuristic medical vibe
- 3-second loading animation with automatic transition
- Floating particles and glowing effects
- Welcome message: "Welcome to MediChat – Your AI Health Companion"

### 🏠 Main Page
- Modern dark theme with neon blue highlights
- Two prominent action buttons:
  - "Try it out for free" - Primary CTA button
  - "Login / Signup" - Opens authentication modal
- Animated chatbot illustration that:
  - **Floats up and down** continuously (smooth 3-second cycle)
  - **Rotates 360°** on click (not hover)
- Floating info cards showing features
- Fully responsive design using CSS Grid and Flexbox
- Animated header with navigation
- **Unified medical cross cursor** throughout the app

### 🔐 Authentication Modal
- **Glassmorphic design** with translucent background
- Blurred backdrop effect showing main page behind
- **Side-by-side tab switcher** for Login/Signup
- **Glass effect on hover** for all input fields
- Smooth animations and transitions
- Social login options (Google, GitHub)
- Responsive and mobile-friendly
- Click outside or close button to dismiss

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool for fast development
- **Framer Motion** - Animation library for smooth transitions
- **CSS3** - Custom animations and modern styling
- **Google Fonts** - Inter & Orbitron fonts

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and visit: `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The production-ready files will be in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/
│   │   ├── LandingPage.jsx    # Landing page with loading animation
│   │   ├── LandingPage.css    # Landing page styles
│   │   ├── MainPage.jsx       # Main page with chatbot interface
│   │   └── MainPage.css       # Main page styles
│   ├── App.jsx          # Main app component
│   ├── App.css          # App styles
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies
└── vite.config.js       # Vite configuration
```

## Customization

### Colors
The theme uses a black and blue color palette. Main colors:
- Primary Blue: `#00d4ff`
- Secondary Blue: `#0099ff`
- Light Blue: `#7dd3fc`
- Background: `#000000`
- Dark Blue: `#0a1929`

### Animations
- **Landing Page**: 3-second loading animation with particle effects
- **Main Page**: Floating chatbot (3s up/down cycle)
- **Hover Effect**: 360° rotation on chatbot (0.8s duration)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT
