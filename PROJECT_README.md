# Jay Asset Management

A modern web application for calculating asset allocation strategies with live market data.

## Features

- **Multiple Investment Strategies**
  - Static strategies (Conservative, Balanced, Aggressive)
  - Dynamic strategies with live market data (PAA - Protective Asset Allocation)

- **PAA Strategy**
  - Momentum-based allocation using real-time ETF data
  - Automatic defensive positioning based on market conditions
  - Historical data analysis with configurable lookback periods

- **User-Friendly Interface**
  - Modern Material-UI design
  - Real-time calculations
  - Visual breakdown of asset allocations
  - Responsive design for all devices

## Architecture

```
jay-asset/
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── pages/             # Page components
│   └── services/          # API service layer
│
└── backend/               # Python Flask backend
    ├── strategies/        # Investment strategy implementations
    ├── database/         # SQLite database
    └── app.py           # Flask application
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- npm or yarn

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the backend:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

## Usage

### Using Static Strategies

1. Select a strategy (Conservative, Balanced, or Aggressive)
2. Enter your investment amount
3. Click "Calculate"
4. View your asset allocation breakdown

### Using PAA Strategy (Requires Backend)

1. Start the backend server
2. Select "PAA (Protective Asset Allocation)" strategy
3. Enter your investment amount
4. Click "Calculate"
5. View real-time allocation based on current market momentum

The PAA strategy will:
- Download latest ETF price data
- Calculate 12-month momentum for each ETF
- Select top-performing ETFs
- Automatically allocate to defensive assets (IEF) based on market conditions

## Adding New Strategies

### Static Strategy (Frontend Only)

Edit `src/components/StrategySelector.js` and add to `staticStrategies`:

```javascript
myStrategy: {
  name: 'My Strategy',
  description: 'Description here',
  type: 'static',
  allocation: {
    'Asset1': 50,
    'Asset2': 30,
    'Asset3': 20,
  }
}
```

### Dynamic Strategy (Backend)

1. Create `backend/strategies/my_strategy.py`:

```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="My Strategy",
            description="Description here"
        )

    def calculate_allocation(self, total_money, **kwargs):
        # Your logic here
        return {
            'strategy': self.name,
            'allocation': {'SPY': 5000, 'BND': 5000},
            'total_amount': total_money
        }

    def get_parameters(self):
        return []
```

2. Register in `backend/strategies/__init__.py`:

```python
from .my_strategy import MyStrategy

STRATEGIES = {
    'paa': PAAStrategy(),
    'my_strategy': MyStrategy(),
}
```

## Technologies Used

### Frontend
- React 19
- Material-UI
- React Router

### Backend
- Flask
- yfinance (Yahoo Finance API)
- pandas
- SQLite

## API Endpoints

- `GET /api/strategies` - List all strategies
- `POST /api/calculate` - Calculate allocation
- `GET /api/history` - Get calculation history
- `GET /api/health` - Health check

## Database

The application stores calculation history in SQLite database at `backend/database/allocations.db`.

## Development

### Frontend
- Start development server: `npm start`
- Build for production: `npm run build`
- Run tests: `npm test`

### Backend
- Run in debug mode: Backend runs in debug mode by default
- Database is created automatically on first run

## Troubleshooting

### Frontend won't start
- Make sure Node.js is installed: `node --version`
- Delete `node_modules` and `package-lock.json`, then run `npm install` again

### Backend errors
- Make sure Python 3.8+ is installed: `python --version`
- Activate virtual environment before running
- Check if port 5000 is available

### "Backend not available" message
- Make sure backend server is running on port 5000
- Check CORS settings in `backend/app.py`
- Verify API_BASE_URL in `src/services/api.js`

## Future Enhancements

- [ ] Add more investment strategies
- [ ] Historical performance charts
- [ ] Portfolio rebalancing recommendations
- [ ] Export allocations to CSV/PDF
- [ ] User authentication and saved portfolios
- [ ] Real-time portfolio tracking
- [ ] Tax-loss harvesting suggestions

## Author

Jehyeon Lee
