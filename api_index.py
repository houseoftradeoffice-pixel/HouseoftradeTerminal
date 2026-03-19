"""
Nivarya Setu - Serverless Flask Application for Vercel
This file serves as the entry point for Vercel's serverless functions
"""

import os
import sys
from datetime import datetime
import random
import json

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask, jsonify, request, send_from_directory
from functools import lru_cache

# Initialize Flask app
app = Flask(__name__, static_folder='../src/platform', static_url_path='')

# Mock data
mock_defaults = {
    # Equities
    'RELIANCE.NS': 2450.00, 'TCS.NS': 3240.00, 'HDFCBANK.NS': 1650.00,
    'INFY.NS': 1420.00, 'SBIN.NS': 580.00, 'TATAMOTORS.NS': 980.00,
    'ITC.NS': 430.00, 'ICICIBANK.NS': 950.00,
    
    # F&O - Futures
    'NIFTY 25OCT FUT': 19650.00,
    'BANKNIFTY 25OCT FUT': 44500.00,
    
    # F&O - Options
    'NIFTY 19500 CE': 145.50, 'NIFTY 19500 PE': 85.20,
    'NIFTY 19600 CE': 88.00, 'NIFTY 19600 PE': 120.50,
    'BANKNIFTY 44000 CE': 320.00, 'BANKNIFTY 44000 PE': 180.00,
    
    # COMMODITIES
    'GOLD 05OCT FUT': 59500.00, 'SILVER 05SEP FUT': 74200.00,
    'CRUDEOIL 19SEP FUT': 7150.00,
    
    # CURRENCY
    'USDINR 27SEP FUT': 83.15, 'EURINR 27SEP FUT': 89.40,
    'GBPINR 27SEP FUT': 104.50,
}

# In-memory state
PAPER_STATE = {
    "funds": 1000000.00,
    "holdings": [
        {"symbol": "TCS.NS", "qty": 10, "avg": 3200.00, "ltp": 3250.00, "type": "CNC", "value": 32500, "pnl": 500, "pnl_pct": 1.5},
    ],
    "positions": {},
    "orders": [],
    "transactions": [
        {"id": 1, "time": "2023-10-01 10:00:23", "desc": "Account Opened", "type": "SYSTEM", "amount": 0, "bal": 0},
        {"id": 2, "time": "2023-10-01 10:05:45", "desc": "Welcome Bonus Funds", "type": "DEPOSIT", "amount": 1000000.00, "bal": 1000000.00}
    ]
}

# Investment data
MOCK_BASKETS = [
    {"id": "b1", "name": "IT Giants", "desc": "Top 3 Indian IT companies", "min_amt": 5000, 
     "stocks": [{"symbol": "TCS.NS", "weight": "40%"}, {"symbol": "INFY.NS", "weight": "35%"}, {"symbol": "WIPRO.NS", "weight": "25%"}]},
    {"id": "b2", "name": "Banking Titans", "desc": "Leading private sector banks", "min_amt": 8000,
     "stocks": [{"symbol": "HDFCBANK.NS", "weight": "50%"}, {"symbol": "ICICIBANK.NS", "weight": "50%"}]},
    {"id": "b3", "name": "EV Future", "desc": "Companies driving the EV revolution", "min_amt": 3500,
     "stocks": [{"symbol": "TATAMOTORS.NS", "weight": "60%"}, {"symbol": "RELIANCE.NS", "weight": "40%"}]}
]

MOCK_IPOS = [
    {"name": "Tata Technologies", "price_band": "475-500", "status": "OPEN", "close_date": "18 Sep"},
    {"name": "Mamaearth", "price_band": "308-324", "status": "UPCOMING", "close_date": "25 Sep"},
    {"name": "IdeaForge", "price_band": "638-672", "status": "CLOSED", "close_date": "10 Aug"}
]

MOCK_MFS = [
    {"name": "HDFC Mid-Cap Opportunities", "nav": 124.5, "cagr_3y": "28.5%", "min_sip": 500},
    {"name": "SBI Small Cap Fund", "nav": 156.8, "cagr_3y": "32.1%", "min_sip": 500},
    {"name": "Parag Parikh Flexi Cap", "nav": 65.4, "cagr_3y": "22.4%", "min_sip": 1000},
    {"name": "Axis Bluechip Fund", "nav": 52.1, "cagr_3y": "14.2%", "min_sip": 500}
]

MOCK_BONDS = [
    {"name": "SGB 2023-24 Series II", "yield": "2.50% pa", "price": 5923, "maturity": "2031"},
    {"name": "7.54% GS 2036", "yield": "7.54%", "price": 100.25, "maturity": "2036"},
    {"name": "REC Ltd Tax Free Bond", "yield": "4.80%", "price": 1150, "maturity": "2027"}
]

SCREENER_DATA = [
    {"symbol": "RELIANCE.NS", "price": 2450.75, "change": 1.25, "rsi": 65.5, "ma_50": 2440.00, "ma_200": 2420.00},
    {"symbol": "TCS.NS", "price": 3245.50, "change": -0.85, "rsi": 45.2, "ma_50": 3250.00, "ma_200": 3200.00},
]

# ===== ROUTES =====

@app.route('/')
def home():
    try:
        return send_from_directory('../src/platform', 'index.html')
    except:
        return jsonify({"status": "error", "message": "Frontend not found"}), 404

@app.route('/api/config')
def get_config():
    return jsonify({
        "firebase": {
            "apiKey": os.environ.get("FIREBASE_API_KEY", "your_api_key"),
            "authDomain": "futurex-trading-bcd05.firebaseapp.com",
            "projectId": "futurex-trading-bcd05",
            "storageBucket": "futurex-trading-bcd05.firebasestorage.app",
            "messagingSenderId": "22335494160",
            "appId": "1:22335494160:web:c292b4f13736785aa9d295",
            "measurementId": "G-SBEMZN69SZ"
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if data.get('email') and data.get('password'):
        return jsonify({"status": "success", "user": {"name": "Madhav", "email": data['email']}})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    return jsonify({"status": "success", "message": "User registered"})

@app.route('/api/user/update', methods=['POST'])
def update_user():
    return jsonify({"status": "success", "message": "Profile updated successfully"})

@app.route('/api/invest/ipos')
def get_ipos():
    return jsonify(MOCK_IPOS)

@app.route('/api/invest/mutual_funds')
def get_mfs():
    return jsonify(MOCK_MFS)

@app.route('/api/invest/bonds')
def get_bonds():
    return jsonify(MOCK_BONDS)

@app.route('/api/baskets')
def get_baskets():
    return jsonify(MOCK_BASKETS)

@app.route('/api/place_basket', methods=['POST'])
def place_basket():
    data = request.json
    basket_id = data.get('basket_id')
    basket = next((b for b in MOCK_BASKETS if b['id'] == basket_id), None)
    
    if not basket:
        return jsonify({"status": "error", "message": "Basket not found"}), 404
    if PAPER_STATE['funds'] < basket['min_amt']:
        return jsonify({"status": "error", "message": "Insufficient funds"}), 400
    
    PAPER_STATE['funds'] -= basket['min_amt']
    PAPER_STATE['transactions'].append({
        "id": f"txn_{len(PAPER_STATE['transactions'])+1}",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "BASKET_BUY",
        "amount": -basket['min_amt'],
        "bal": PAPER_STATE['funds'],
        "desc": f"Bought Basket: {basket['name']}"
    })
    return jsonify({"status": "success", "message": f"Successfully invested in {basket['name']}!"})

@app.route('/api/invest/mf/sip', methods=['POST'])
def start_sip():
    data = request.json
    name = data.get('name')
    PAPER_STATE['transactions'].append({
        "id": f"txn_{len(PAPER_STATE['transactions'])+1}",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "SIP_START",
        "amount": 0,
        "bal": PAPER_STATE['funds'],
        "desc": f"SIP started for {name}"
    })
    return jsonify({"status": "success", "message": f"SIP for {name} started successfully"})

@app.route('/api/invest/ipo/apply', methods=['POST'])
def apply_ipo():
    data = request.json
    name = data.get('name')
    PAPER_STATE['transactions'].append({
        "id": f"txn_{len(PAPER_STATE['transactions'])+1}",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "IPO_APP",
        "amount": 0,
        "bal": PAPER_STATE['funds'],
        "desc": f"Applied for IPO: {name}"
    })
    return jsonify({"status": "success", "message": f"Application for {name} submitted"})

@app.route('/api/invest/bond/buy', methods=['POST'])
def buy_bond():
    data = request.json
    name = data.get('name')
    price = data.get('price', 0)
    if PAPER_STATE['funds'] < price:
        return jsonify({"status": "error", "message": "Insufficient funds"}), 400
    PAPER_STATE['funds'] -= price
    PAPER_STATE['transactions'].append({
        "id": f"txn_{len(PAPER_STATE['transactions'])+1}",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "BOND_BUY",
        "amount": -price,
        "bal": PAPER_STATE['funds'],
        "desc": f"Bought Bond: {name}"
    })
    return jsonify({"status": "success", "message": f"Bond purchase successful"})

@app.route('/api/screener')
def get_screener():
    filter_type = request.args.get('filter', 'ALL')
    data = SCREENER_DATA
    
    if filter_type == 'TOP_GAINERS':
        data = [s for s in SCREENER_DATA if s['change'] > 0]
    elif filter_type == 'TOP_LOSERS':
        data = [s for s in SCREENER_DATA if s['change'] < 0]
    elif filter_type == 'RSI_OVERBOUGHT':
        data = [s for s in SCREENER_DATA if s['rsi'] > 70]
    elif filter_type == 'RSI_OVERSOLD':
        data = [s for s in SCREENER_DATA if s['rsi'] < 30]
    
    return jsonify(data)

@app.route('/api/generate_key', methods=['POST'])
def generate_key():
    import uuid
    return jsonify({"key": f"ik_{str(uuid.uuid4())[:16]}", "secret": f"is_{str(uuid.uuid4())[:16]}"})

@app.route('/api/batch_quotes')
def get_batch_quotes():
    symbols = request.args.get('symbols', '').split(',')
    response_map = {}
    
    for sym in symbols:
        if sym:
            base = mock_defaults.get(sym, 500.0)
            change_pct = random.uniform(-1.5, 1.5)
            curr = base * (1 + change_pct/100)
            response_map[sym] = {"price": round(curr, 2), "change": round(change_pct, 2)}
    
    response_map['indices'] = {
        "NIFTY": {"price": round(19500 + random.uniform(-10, 10), 2), "chg": round(0.5 + random.uniform(-0.1, 0.1), 2)},
        "BANKNIFTY": {"price": round(44000 + random.uniform(-30, 30), 2), "chg": round(0.4 + random.uniform(-0.1, 0.1), 2)}
    }
    
    return jsonify(response_map)

@app.route('/api/market_depth')
def market_depth_api():
    sym = request.args.get('symbol', 'RELIANCE.NS')
    base = mock_defaults.get(sym, 2500)
    curr = base + random.uniform(-2, 2)
    
    bids = []
    asks = []
    for i in range(1, 6):
        spread = curr * 0.0005 * i
        qty_base = int(10000 / curr) if curr > 0 else 100
        bids.append({"price": round(curr - spread, 2), "qty": random.randint(1, 10) * qty_base, "orders": random.randint(1, 20)})
        asks.append({"price": round(curr + spread, 2), "qty": random.randint(1, 10) * qty_base, "orders": random.randint(1, 20)})
    
    return jsonify({
        "bids": bids,
        "asks": asks,
        "total_bid": sum(b['qty'] for b in bids),
        "total_ask": sum(a['qty'] for a in asks)
    })

@app.route('/api/funds/history')
def get_funds_history():
    return jsonify(PAPER_STATE['transactions'][::-1])

@app.route('/api/portfolio')
def get_portfolio():
    total_val = PAPER_STATE['funds']
    
    for h in PAPER_STATE['holdings']:
        mock_price = h['avg']
        if h['symbol'] in mock_defaults:
            mock_price = mock_defaults[h['symbol']] + (random.uniform(-1, 1) * (mock_defaults[h['symbol']]/100))
        h['ltp'] = round(mock_price, 2)
        h['value'] = round(h['ltp'] * h['qty'], 2)
        h['pnl'] = round(h['value'] - (h['avg'] * h['qty']), 2)
        h['pnl_pct'] = round((h['pnl'] / (h['avg'] * h['qty'])) * 100, 2)
        total_val += h['value']
    
    pos_list = []
    total_pnl = 0
    for sym, pos in PAPER_STATE['positions'].items():
        base = mock_defaults.get(sym, 1000)
        curr = base + (random.uniform(-0.5, 0.5) * base / 100)
        mtm = (curr - pos['avg']) * pos['qty']
        
        if pos['qty'] != 0:
            pos_list.append({
                "symbol": sym, "qty": pos['qty'], "avg": pos['avg'],
                "ltp": round(curr, 2), "pnl": round(mtm, 2), "product": "MIS"
            })
            total_pnl += mtm
    
    return jsonify({
        "funds": round(PAPER_STATE['funds'], 2),
        "holdings": PAPER_STATE['holdings'],
        "positions": pos_list,
        "orders": PAPER_STATE['orders'][::-1],
        "total_value": round(total_val, 2),
        "total_pnl": round(total_pnl + sum(h['pnl'] for h in PAPER_STATE['holdings']), 2)
    })

@app.route('/api/add_funds', methods=['POST'])
def add_funds():
    amt = float(request.json.get('amount', 0))
    PAPER_STATE['funds'] += amt
    PAPER_STATE['transactions'].append({
        "id": f"txn_{len(PAPER_STATE['transactions'])+1}",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "DEPOSIT",
        "amount": amt,
        "bal": PAPER_STATE['funds'],
        "desc": "Funds Added via UPI"
    })
    return jsonify({"status": "success", "new_balance": PAPER_STATE['funds']})

@app.route('/api/place_order', methods=['POST'])
def place_order():
    data = request.json
    symbol = data.get('symbol')
    side = data.get('side')
    qty = int(data.get('qty', 0))
    product = data.get('product', 'MIS')
    price = float(data.get('price', 0))
    
    order_value = qty * price
    
    if side == 'BUY':
        if PAPER_STATE['funds'] < order_value:
            return jsonify({"status": "error", "message": f"Insufficient Margin. Req: {order_value}"})
        PAPER_STATE['funds'] -= order_value
    elif side == 'SELL':
        if product == 'CNC':
            holding_item = next((h for h in PAPER_STATE['holdings'] if h['symbol'] == symbol), None)
            if not holding_item or holding_item['qty'] < qty:
                return jsonify({"status": "error", "message": "Insufficient Holdings"})
        PAPER_STATE['funds'] += order_value
    
    PAPER_STATE['orders'].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "symbol": symbol, "type": side, "product": product,
        "qty": qty, "price": price, "status": "COMPLETE"
    })
    
    if product == 'CNC':
        holding_item = next((h for h in PAPER_STATE['holdings'] if h['symbol'] == symbol), None)
        if side == 'BUY':
            if holding_item:
                old_val = holding_item['qty'] * holding_item['avg']
                new_val = qty * price
                holding_item['qty'] += qty
                holding_item['avg'] = round((old_val + new_val) / holding_item['qty'], 2)
            else:
                PAPER_STATE['holdings'].append({
                    "symbol": symbol, "qty": qty, "avg": price,
                    "ltp": price, "type": "CNC", "value": order_value, "pnl": 0, "pnl_pct": 0
                })
        else:
            if holding_item:
                holding_item['qty'] -= qty
                if holding_item['qty'] <= 0:
                    PAPER_STATE['holdings'].remove(holding_item)
    else:
        if symbol not in PAPER_STATE['positions']:
            PAPER_STATE['positions'][symbol] = {"qty": 0, "avg": 0}
        p = PAPER_STATE['positions'][symbol]
        if side == 'BUY':
            p['qty'] += qty
            p['avg'] = price
        else:
            p['qty'] -= qty
            p['avg'] = price
    
    return jsonify({"status": "success", "message": "Order Placed"})

@app.route('/api/square_off', methods=['POST'])
def square_off():
    data = request.json
    symbol = data.get('symbol')
    if symbol in PAPER_STATE['positions']:
        pos = PAPER_STATE['positions'][symbol]
        qty = pos['qty']
        if qty != 0:
            side = 'SELL' if qty > 0 else 'BUY'
            price = mock_defaults.get(symbol, 1000)
            PAPER_STATE['positions'][symbol] = {"qty": 0, "avg": 0}
            PAPER_STATE['funds'] += (abs(qty) * price)
            PAPER_STATE['orders'].append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "symbol": symbol, "type": side, "product": "MIS (Auto)",
                "qty": abs(qty), "price": price, "status": "COMPLETE"
            })
            return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Position not found"})

@app.route('/api/live/market_data')
def get_live_market_data():
    """Live market data endpoint"""
    try:
        response_map = {}
        for sym in list(mock_defaults.keys())[:10]:
            base = mock_defaults.get(sym, 500.0)
            change_pct = random.uniform(-2.5, 2.5)
            curr = base * (1 + change_pct/100)
            response_map[sym] = {
                "symbol": sym,
                "price": round(curr, 2),
                "change": round(change_pct, 2),
                "timestamp": datetime.now().isoformat(),
                "volume": random.randint(10000, 1000000)
            }
        return jsonify({"status": "success", "data": response_map, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/live/portfolio_update')
def get_live_portfolio_update():
    """Live portfolio update endpoint"""
    try:
        return jsonify({
            "status": "success",
            "portfolio": PAPER_STATE,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Error handling
@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# Health check
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "Server is running", "timestamp": datetime.now().isoformat()})

# Export app for Vercel
if __name__ == '__main__':
    app.run(debug=False)
