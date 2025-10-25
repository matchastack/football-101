# Football-101

A full-stack web application for displaying Premier League football data, including live standings, upcoming fixtures, and score predictions.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)

## Overview

Football-101 is a modern web application that provides Premier League football enthusiasts with up-to-date information about:
- Team standings and statistics
- Upcoming fixtures and match schedules
- Historical match data
- Score predictions (in development)

The application fetches data from RapidAPI Football API, caches it for performance, and serves it through a clean, responsive React interface.

## Features

- **Live Standings**: View current Premier League table with team statistics
- **Fixture List**: Browse upcoming matches with infinite scroll pagination
- **Team Information**: Team logos, venue details, and match times
- **Responsive Design**: Mobile-friendly Bootstrap UI
- **Data Caching**: Efficient data management with pickle serialization
- **Docker Support**: Easy deployment with Docker Compose

## Tech Stack

### Frontend
- React 18.2.0 with TypeScript
- React Router for navigation
- Bootstrap 5.3.2 for styling
- Vite for fast development and building

### Backend
- Flask 3.0.0 REST API
- pandas for data processing
- RapidAPI Football API integration
- PostgreSQL 15 database

### Infrastructure
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 9101)   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐      ┌──────────────┐
│  Flask Backend  │◄────►│  PostgreSQL  │
│   (Port 9102)   │      │  (Port 5432) │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│   RapidAPI      │
│ Football API    │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Pickle Cache   │
│   (data/)       │
└─────────────────┘
```

**Data Flow**:
1. Frontend requests data from Flask API
2. Backend checks cache (pickle files)
3. If cache miss, fetches from RapidAPI
4. Processes data with pandas
5. Caches result and returns to frontend
6. Frontend displays data in React components

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.9+ and Node.js 16+ (for local development)
- RapidAPI Football API key

### Using Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/football-101.git
cd football-101

# 2. Create data directory
mkdir data

# 3. Configure environment
cd backend
cp .env.example .env  # Create .env and add your API keys
cd ..

# 4. Start services
cd docker
docker compose up -d

# 5. Access application
# Frontend: http://localhost:9101
# Backend: http://localhost:9102
```

## Installation

### Local Development Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your credentials:
# - RAPIDAPI_KEY
# - RAPIDAPI_HOST
# - PostgreSQL credentials (if using database)

# Create data directory
mkdir -p ../data

# Run Flask server
python app.py
```

Backend will be available at `http://localhost:9102`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:9101`

### Environment Variables

Create `backend/.env` file:

```env
# RapidAPI Football API
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com
RAPIDAPI_KEY=your_api_key_here

# PostgreSQL (for Docker)
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=football_db

# Database Connection (optional)
HOST=localhost
DB_PORT=5432
DB_NAME=football_db
DB_USER=your_username
DB_PASSWORD=your_password
```

## Usage

### Viewing Standings

Navigate to `http://localhost:9101/premier-league` to view the current Premier League table with:
- Team rankings
- Points, wins, draws, losses
- Goals for/against
- Form indicators

### Browsing Fixtures

Navigate to `http://localhost:9101/premier-league/fixtures` to:
- View upcoming matches
- See match dates, times, and venues
- Infinite scroll to load more fixtures
- View team logos

### API Access

Access the REST API directly:

```bash
# Health check
curl http://localhost:9102/

# Get standings
curl http://localhost:9102/premier-league/table

# Get fixtures
curl http://localhost:9102/premier-league/fixtures
```

## Project Structure

```
football-101/
├── backend/                 # Flask REST API
│   ├── app.py              # Main application
│   ├── api_data.py         # RapidAPI integration
│   ├── utils.py            # Utility functions
│   ├── temp_data.py        # Data fetching script
│   ├── upload.py           # Database utilities
│   ├── score_pred_model.py # Prediction model
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/               # React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── App.tsx        # Root component
│   │   └── main.tsx       # Entry point
│   ├── package.json       # Node dependencies
│   └── README.md          # Frontend documentation
├── docker/                # Docker configuration
│   ├── docker-compose.yaml
│   └── frontend_dockerfile
├── data/                  # Cached data (gitignored)
└── README.md             # This file
```

## API Documentation

### Endpoints

#### `GET /`
Health check endpoint.

**Response**:
```json
{
  "message": "api is working"
}
```

#### `GET /premier-league/table`
Returns Premier League standings.

**Response**: JSON array of team standings with statistics

#### `GET /premier-league/fixtures`
Returns upcoming Premier League fixtures.

**Response**: JSON array of fixtures with match details

See [Backend README](backend/README.md) for detailed API documentation.

## Development

### Backend Development

```bash
cd backend

# Run development server with auto-reload
python app.py

# Fetch fresh data from API
python temp_data.py

# Run Jupyter notebook for model development
jupyter notebook build_pred_model.ipynb
```

See [Backend README](backend/README.md) for more details.

### Frontend Development

```bash
cd frontend

# Development server with HMR
npm run dev

# Type checking
npm run build

# Linting
npm run lint

# Production preview
npm run preview
```

See [Frontend README](frontend/README.md) for more details.

### Adding New Features

1. **New API Endpoint**:
   - Add function to `backend/api_data.py`
   - Add route to `backend/app.py`
   - Update frontend to consume endpoint

2. **New Frontend Page**:
   - Create component in `frontend/src/pages/`
   - Add route to `frontend/src/App.tsx`
   - Add navigation link to NavBar

3. **New Component**:
   - Create in `frontend/src/components/`
   - Define TypeScript interfaces
   - Import and use in pages

## Docker Deployment

### Build and Run

```bash
cd docker

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Rebuild after changes
docker compose up -d --build
```

### Services

- **db**: PostgreSQL 15 database (port 5432)
- **web**: React frontend (port 9101)

### Production Considerations

- Set `debug=False` in `backend/app.py`
- Configure proper CORS origins
- Use environment-specific `.env` files
- Set up reverse proxy (nginx/Apache)
- Enable HTTPS
- Configure database backups

## Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8
- **TypeScript**: Use ESLint configuration
- **Commits**: Use conventional commit messages

### Testing

```bash
# Backend (when tests are added)
cd backend
pytest

# Frontend (when tests are added)
cd frontend
npm test
```

## License

This project is a personal web development project. All rights reserved.

## Acknowledgments

- [RapidAPI Football API](https://rapidapi.com/api-sports/api/api-football) for data
- [API-Sports](https://www.api-football.com/) for team logos
- Bootstrap for UI components
- React and Flask communities

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.