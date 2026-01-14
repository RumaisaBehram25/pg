# PharmAudit Dashboard - Frontend

A modern React dashboard for the pharmacy audit platform.

## Features

- 📊 Real-time metrics and analytics
- 📈 Interactive charts and visualizations
- 📋 Claims management and processing
- 🔍 Rule-based fraud detection
- 👥 User management
- 📤 CSV file upload and processing

## Tech Stack

- **React** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Charting library
- **Lucide React** - Icon library
- **React Router** - Client-side routing
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Update the API URL in .env if needed
```

### Development

```bash
# Start the development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Sidebar.jsx
│   │   ├── MetricCard.jsx
│   │   ├── ProcessingStatusChart.jsx
│   │   ├── RecentActivity.jsx
│   │   └── RecentOrdersTable.jsx
│   ├── pages/            # Page components
│   │   └── Dashboard.jsx
│   ├── utils/            # Utility functions and API calls
│   │   └── api.js
│   ├── App.jsx           # Main app component with routing
│   ├── main.jsx          # Application entry point
│   └── index.css         # Global styles with Tailwind
├── public/               # Static assets
└── package.json          # Dependencies and scripts
```

## API Integration

The frontend is configured to connect to the FastAPI backend. Update the `VITE_API_URL` in your `.env` file to point to your backend server.

## Available Routes

- `/` - Dashboard (main view)
- `/upload` - Upload CSV files
- `/rules/new` - Create new audit rules
- `/reports` - View reports
- `/users` - Manage users
- `/support` - Support page
- `/settings` - Application settings

## Styling

This project uses Tailwind CSS for styling. The configuration can be found in `tailwind.config.js`.

Primary colors:
- Primary: `#5B5FF9`
- Primary Hover: `#4B4FE9`

## Contributing

1. Make sure to follow the existing code style
2. Test your changes thoroughly
3. Update documentation as needed
