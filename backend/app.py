from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
from strategies import get_strategy, list_strategies

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Database setup
DB_NAME = "database/allocations.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            strategy TEXT,
            total_amount REAL,
            allocation TEXT,
            parameters TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get list of all available strategies"""
    try:
        strategies = list_strategies()
        return jsonify({
            'success': True,
            'strategies': strategies
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/calculate', methods=['POST'])
def calculate_allocation():
    """Calculate allocation for a given strategy"""
    try:
        data = request.json
        strategy_id = data.get('strategy_id')
        total_money = float(data.get('total_money', 0))
        parameters = data.get('parameters', {})

        if not strategy_id:
            return jsonify({
                'success': False,
                'error': 'Strategy ID is required'
            }), 400

        if total_money <= 0:
            return jsonify({
                'success': False,
                'error': 'Total money must be greater than 0'
            }), 400

        # Get strategy and calculate
        strategy = get_strategy(strategy_id)
        if not strategy:
            return jsonify({
                'success': False,
                'error': f'Strategy {strategy_id} not found'
            }), 404

        result = strategy.calculate_allocation(total_money, **parameters)

        # Check for errors in result
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500

        # Save to database
        save_allocation(strategy_id, total_money, result, parameters)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get calculation history"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT id, date, strategy, total_amount, allocation, parameters
            FROM allocations
            ORDER BY date DESC
            LIMIT 50
        """)
        rows = c.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'date': row[1],
                'strategy': row[2],
                'total_amount': row[3],
                'allocation': row[4],
                'parameters': row[5]
            })

        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def save_allocation(strategy_id, total_amount, result, parameters):
    """Save allocation to database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            INSERT INTO allocations (date, strategy, total_amount, allocation, parameters)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.today().strftime("%Y-%m-%d"),
            strategy_id,
            total_amount,
            str(result.get('allocation', {})),
            str(parameters)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving allocation: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
