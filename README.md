# Delivery System Dashboard

A comprehensive delivery system dashboard that helps manage agents, orders, and warehouses efficiently.

## Features

### 1. Agent Check-in System
- Agents can check in at warehouses
- Daily metrics reset upon check-in
- Real-time tracking of check-in status
- Base pay of 500 INR for showing up

### 2. Order Allocation System
- **Automatic Allocation**: Runs daily at 9 AM
- **Manual Trigger**: Available for testing purposes
- **Optimization Parameters**:
  - Target: 50+ orders per agent
  - Working limit: 10 hours
  - Distance limit: 100km
  - Travel time calculation: 5 minutes per km

### 3. Payment Structure
- Base pay: 500 INR for showing up
- 35 INR per order for 25+ orders
- 42 INR per order for 50+ orders

### 4. Dashboard Features
- Real-time efficiency metrics
- Order status tracking (pending, assigned, delivered, postponed)
- Warehouse information display
- Agent statistics
- Visual representation of key metrics
- Allocation status messages

## Prerequisites

- Python 3.8 or higher
- Node.js 14.x or higher
- npm 6.x or higher

## Installation & Setup

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python run.py
```
The backend will start on http://localhost:8000

### Frontend Setup
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
npm start
```
The frontend will start on http://localhost:3000

## Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   └── utils/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── assets/
│   │   └── App.js
│   └── package.json
└── screenshots/
    └── dashboard.png
```

## API Endpoints

### Agent Endpoints
- `GET /api/agents` - Get all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `POST /api/agents/{id}/check-in` - Agent check-in

### Order Allocation
- `POST /api/allocate-orders` - Trigger manual allocation
- `GET /api/allocation-status` - Get allocation status

### Warehouse Endpoints
- `GET /api/warehouses` - Get all warehouses
- `GET /api/warehouses/{id}` - Get warehouse details

## Screenshots

You can find the application screenshots in the `/screenshots` directory.

## Implementation Details

### Backend
- Built with Python and Falcon framework
- SQLAlchemy for database management
- Implements efficient order allocation algorithm
- Real-time metric calculations

### Frontend
- Built with React.js
- Real-time dashboard updates
- Responsive design
- Modern UI/UX with CSS Grid and Flexbox

## Notes
- The automatic allocation runs at 9 AM daily
- Manual allocation is available for testing
- Agent metrics reset upon daily check-in
- Distance calculations use the Haversine formula
- Payment structure is automatically calculated based on order count
- Make sure both backend and frontend servers are running for full functionality