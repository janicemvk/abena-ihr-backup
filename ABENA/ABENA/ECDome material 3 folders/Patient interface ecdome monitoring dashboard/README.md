# Patient eCDome Monitoring Dashboard

A patient-friendly interface for monitoring endocannabinoid system health using the ABENA SDK standard. This dashboard provides real-time health insights, goal tracking, and personalized wellness recommendations.

## Features

- **Real-time eCDome Monitoring**: Live tracking of endocannabinoid system metrics
- **Patient-Friendly Interface**: Simplified, intuitive dashboard design
- **Health Insights**: Personalized tips and recommendations
- **Goal Tracking**: Daily wellness goals with progress tracking
- **System Health Overview**: Multi-system health monitoring
- **Interactive Charts**: Visual data representation using Recharts
- **Responsive Design**: Mobile-friendly interface
- **ABENA SDK Compliant**: Follows ABENA healthcare standards

## Key Metrics Tracked

- **eCDome Overall Score**: Comprehensive endocannabinoid system health
- **Anandamide Levels**: "Bliss factor" neurotransmitter
- **2-AG Levels**: Balance and homeostasis indicator
- **CB1 Receptor Activity**: Brain receptor function
- **CB2 Receptor Activity**: Body receptor function
- **System Health**: Metabolism, immunity, sleep, stress, nutrition, activity

## Technology Stack

- **Frontend**: React 18 with Hooks
- **Styling**: Tailwind CSS
- **Charts**: Recharts library
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Package Manager**: npm

## Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd patient-ecdome-monitoring-dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
patient-ecdome-monitoring-dashboard/
├── src/
│   ├── components/
│   │   └── PatientDashboard.jsx    # Main dashboard component
│   ├── App.jsx                     # Root app component
│   ├── main.jsx                    # App entry point
│   └── index.css                   # Global styles
├── index.html                      # HTML template
├── package.json                    # Dependencies & scripts
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # Tailwind CSS config
├── postcss.config.js               # PostCSS config
└── README.md                       # This file
```

## Dashboard Components

### Main Score Card
- Overall eCDome score with trend indicators
- Individual metric breakdown (Anandamide, 2-AG, CB1, CB2)
- Real-time score updates

### Wellness Journey
- Daily energy, mood, and stress trends
- Interactive area charts
- Timeframe selection (today, week, month)

### System Health
- Six key body systems monitoring
- Visual progress bars with status indicators
- Color-coded health levels

### Goal Tracking
- Daily wellness goals with categories
- Interactive goal completion
- Progress tracking with visual indicators

### Insights & Tips
- Personalized health recommendations
- Progress celebrations
- Attention alerts for health optimization

### Quick Actions
- Access to wellness plans
- Provider communication
- Appointment scheduling

## ABENA SDK Integration

The dashboard is designed to integrate seamlessly with the ABENA SDK:

```javascript
// Production integration example
const patientData = await abena.getPatientData(patientId, 'patient-dashboard');
```

Current implementation uses mock data for demonstration purposes.

## Customization

### Styling
- Modify `tailwind.config.js` for custom colors and themes
- Update `src/index.css` for global style overrides

### Data Sources
- Replace mock data in `PatientDashboard.jsx` with ABENA SDK calls
- Implement real-time data fetching and WebSocket connections

### Features
- Add new metric cards by extending the `ecdomeMetrics` object
- Create additional chart types using Recharts components
- Implement new goal categories and tracking systems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For technical support or questions about the ABENA SDK integration, please contact:
- Email: support@abena-healthcare.com
- Documentation: https://docs.abena-healthcare.com

## Roadmap

- [ ] Advanced analytics and historical data views
- [ ] Provider dashboard integration
- [ ] Mobile app companion
- [ ] Wearable device integration
- [ ] AI-powered health insights
- [ ] Multi-language support 