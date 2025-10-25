# Frontend - Football-101

React/TypeScript frontend for displaying Premier League football data including standings and fixtures.

## Tech Stack

- **React** 18.2.0 - UI library
- **TypeScript** 5.2.2 - Type safety
- **Vite** 5.0.0 - Build tool and dev server
- **React Router** 6.21.1 - Client-side routing
- **Bootstrap** 5.3.2 - CSS framework
- **ESLint** - Code linting with TypeScript support

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Header.tsx       # Site header
│   │   ├── NavBar.tsx       # Navigation bar
│   │   ├── Footer.tsx       # Site footer
│   │   ├── StandingTable.tsx # League standings table
│   │   └── FixtureList.tsx  # Fixtures list with infinite scroll
│   ├── pages/               # Route-level page components
│   │   ├── Home.tsx         # Landing page
│   │   ├── Table.tsx        # Standings page
│   │   └── Fixtures.tsx     # Fixtures page
│   ├── App.tsx              # Root component with routes
│   └── main.tsx             # Application entry point
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript configuration
└── package.json             # Dependencies and scripts
```

## Getting Started

### Prerequisites

- Node.js (v16+)
- npm or yarn
- Backend API running on `http://localhost:9102`

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server (http://localhost:9101)
npm run dev
```

The dev server runs with:
- Hot Module Replacement (HMR)
- TypeScript type checking
- Port 9101 (configured in vite.config.ts)

### Build

```bash
# Type check and build for production
npm run build
```

Outputs to `dist/` directory.

### Linting

```bash
# Run ESLint on TypeScript/TSX files
npm run lint
```

### Preview Production Build

```bash
# Preview production build locally
npm run preview
```

## Configuration

### Vite Config (`vite.config.ts`)

- **Dev Server**: Port 9101, exposed to all network interfaces
- **Preview Server**: Port 9101
- **Plugins**: @vitejs/plugin-react for Fast Refresh

### TypeScript Config (`tsconfig.json`)

- **Target**: ES2020
- **JSX**: react-jsx (React 17+ transform)
- **Strict Mode**: Enabled
- **Module Resolution**: Bundler mode
- Unused locals and parameters enforcement

## Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | Home | Landing page |
| `/home` | Home | Landing page (alias) |
| `/premier-league` | Table | League standings |
| `/premier-league/teams` | Table | League standings (alias) |
| `/premier-league/fixtures` | Fixtures | Upcoming fixtures |
| `*` | 404 | Not found page |

## Components

### StandingTable

Fetches and displays Premier League standings from the backend API.

**API Endpoint**: `GET http://localhost:9102/premier-league/table`

**Features**:
- Fetches standings data on mount
- Displays team rankings, stats, and points
- Error handling for failed API requests

### FixtureList

Displays upcoming Premier League fixtures with infinite scroll pagination.

**API Endpoint**: `GET http://localhost:9102/premier-league/fixtures`

**Features**:
- Infinite scroll using Intersection Observer API
- Pagination with 1-second delay between loads
- Loading indicators
- Team logos from API-Sports CDN
- Time formatting in local timezone
- 100px root margin for preloading next page

**Data Interface**:
```typescript
interface FixtureData {
    id: number;
    date: string;          // ISO 8601 date string
    venue: string;
    city: string;
    season: number;
    round: string;
    "home.id": number;
    "home.name": string;
    "away.id": number;
    "away.name": string;
}
```

**TODO Features**:
- Add filtering by team/date
- Add team/match detail views

## API Integration

The frontend communicates with the Flask backend running on port 9102:

```typescript
// Example fetch call
fetch('http://localhost:9102/premier-league/table')
    .then(res => res.json())
    .then(data => JSON.parse(data))
    .catch(err => console.error(err.message));
```

All API responses are JSON strings that need to be parsed twice (backend returns serialized JSON).

## Styling

- **Framework**: Bootstrap 5.3.2
- **Custom CSS**: Component-specific styles (e.g., `FixtureList.css`)
- **Responsive Design**: Bootstrap grid system and utilities

## Development Tips

### Adding New Routes

1. Create page component in `src/pages/`
2. Add route to `App.tsx`:
   ```tsx
   <Route path="/your-path" element={<YourComponent />} />
   ```

### Adding New Components

1. Create component in `src/components/`
2. Export as default
3. Import and use in page components

### Type Safety

- Always define interfaces for API response data
- Use TypeScript strict mode features
- Run `npm run lint` to catch type errors

### Working with API Data

The backend returns double-serialized JSON:
```typescript
fetch(url)
    .then(res => res.json())  // First parse
    .then(data => JSON.parse(data))  // Second parse
```

## Docker

The frontend can be run in a Docker container:

```bash
# From project root
cd docker
docker compose up web
```

Container configuration in `docker/docker-compose.yaml` and `docker/frontend_dockerfile`.

## Troubleshooting

### Port Already in Use

If port 9101 is in use, either:
- Kill the process using the port
- Change port in `vite.config.ts` (both server and preview sections)

### API Connection Issues

Ensure:
- Backend is running on `http://localhost:9102`
- CORS is enabled on backend (Flask-CORS)
- No firewall blocking local connections

### Build Errors

- Run `npm install` to ensure dependencies are up to date
- Check TypeScript errors: `npm run build`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
