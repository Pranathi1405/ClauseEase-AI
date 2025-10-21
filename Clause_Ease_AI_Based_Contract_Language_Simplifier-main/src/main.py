from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import json
import os
import sys
from pathlib import Path
import jwt
from datetime import datetime, timedelta
from functools import wraps

# Add components to path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from components.module1_document_ingestion import extract_text
from components.module2_text_preprocessing import preprocess_contract_text
from components.module3_clause_detection import detect_clause_type, ensure_model_loaded
from components.module5_language_simplification import simplify_text, ensure_simplifier_loaded
from components.module4_legal_terms import extract_legal_terms
from components.readability_metrics import calculate_all_metrics, generate_clause_type_chart, generate_stats_chart

# Flask app setup
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'clauseease-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Paths
ROOT = CURRENT_DIR.parent
USERS_FILE = ROOT / 'data' / 'users.json'
SESSIONS_FILE = ROOT / 'data' / 'sessions.json'

# Helper functions
def load_users():
    """Load users from JSON file"""
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    USERS_FILE.parent.mkdir(exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def token_required(f):
    """Decorator to protect routes with JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        print(f"\n🔐 TOKEN CHECK")
        print(f"Token present: {bool(token)}")
        
        if not token:
            print("❌ Token missing")
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
            print(f"✅ Token valid for user: {current_user}\n")
        except Exception as e:
            print(f"❌ Token invalid: {str(e)}\n")
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Flask API Routes
@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        print(f"[REGISTER] Received data: {data}")  # Debug logging
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'message': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'message': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        
        users = load_users()
        
        if email in users:
            return jsonify({'message': 'Email already registered'}), 400
        
        for user_email, user_data in users.items():
            # Handle case where user_data might be a string (legacy data)
            if isinstance(user_data, dict) and user_data.get('username') == username:
                return jsonify({'message': 'Username already taken'}), 400
        
        users[email] = {
            'username': username,
            'password': hash_password(password),
            'created_at': datetime.utcnow().isoformat()
        }
        
        save_users(users)
        
        print(f"[REGISTER] User {username} registered successfully")  # Debug logging
        return jsonify({
            'message': 'Registration successful',
            'username': username
        }), 201
        
    except Exception as e:
        print(f"[REGISTER ERROR] {str(e)}")  # Debug logging
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """Login user and return JWT token"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        print(f"[LOGIN] Email: {email}, Password entered: {password}")  # Debug
        
        if not email or not password:
            return jsonify({'message': 'Email and password required'}), 400
        
        users = load_users()
        
        if email not in users:
            print(f"[LOGIN ERROR] Email {email} not found in database")  # Debug
            return jsonify({'message': 'Invalid credentials'}), 401
        
        user = users[email]
        input_hash = hash_password(password)
        stored_hash = user['password']
        
        print(f"[LOGIN DEBUG] Input hash: {input_hash}")  # Debug
        print(f"[LOGIN DEBUG] Stored hash: {stored_hash}")  # Debug
        print(f"[LOGIN DEBUG] Match: {input_hash == stored_hash}")  # Debug
        
        if stored_hash != input_hash:
            print(f"[LOGIN ERROR] Password mismatch for {email}")  # Debug
            return jsonify({'message': 'Invalid credentials'}), 401
        
        token = jwt.encode({
            'username': user['username'],
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        print(f"[LOGIN] User {user['username']} logged in successfully")  # Debug
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'username': user['username']
        }), 200
        
    except Exception as e:
        print(f"[LOGIN ERROR] {str(e)}")  # Debug
        return jsonify({'message': f'Server error: {str(e)}'}), 500

@app.route('/api/process', methods=['POST'])
@token_required
def process_document(current_user):
    """Process uploaded document through all 5 modules"""
    print(f"\n{'='*60}")
    print(f"📥 PROCESSING REQUEST RECEIVED")
    print(f"User: {current_user}")
    print(f"Files in request: {list(request.files.keys())}")
    print(f"{'='*60}\n")
    step = 'initial'
    if 'file' not in request.files:
        print("❌ ERROR: No file in request.files")
        return jsonify({'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("❌ ERROR: Empty filename")
        return jsonify({'message': 'No file selected'}), 400
    
    print(f"✅ File received: {file.filename}")
    
    temp_dir = ROOT / 'temp_uploads'
    temp_dir.mkdir(exist_ok=True)
    
    temp_path = temp_dir / file.filename
    file.save(str(temp_path))
    
    try:
        step = 'save_upload'
        # Module 1: Document Ingestion
        step = 'extract_text'
        raw_text = extract_text(str(temp_path))
        
        if raw_text.startswith('[ERROR]'):
            return jsonify({'message': raw_text}), 400
        
        # Module 2: Text Preprocessing
        step = 'preprocess_contract_text'
        clauses = preprocess_contract_text(raw_text)
        
        # Calculate readability metrics for original text
        step = 'calculate_original_metrics'
        original_metrics = calculate_all_metrics(raw_text)
        
        # Module 3: Clause Detection
        step = 'detect_clause_type'
        clause_types = []
        for clause in clauses:
            clause_type = detect_clause_type(clause['cleaned_text'])
            clause_types.append(clause_type)
        
        # Module 4: Legal Terms Extraction
        step = 'extract_legal_terms'
        legal_terms = extract_legal_terms(raw_text)
        
        # Module 5: Language Simplification
        step = 'simplify_text'
        simplified_texts = []
        for clause in clauses:
            simplified = simplify_text(clause['cleaned_text'])
            simplified_texts.append(simplified)
        
        # Combine all simplified text
        step = 'simplified_metrics'
        combined_simplified = " ".join(simplified_texts)
        simplified_metrics = calculate_all_metrics(combined_simplified)
        
        # Save session
        step = 'save_session'
        save_session(current_user, file.filename, len(clauses))
        
        # Prepare results
        step = 'prepare_response'
        results = {
            'filename': file.filename,
            'raw_text': raw_text,
            'word_count': len(raw_text.split()),
            'clause_count': len(clauses),
            'original_readability': original_metrics,
            'simplified_readability': simplified_metrics,
            'clauses': [
                {
                    'index': i + 1,
                    'raw_text': c['raw_text'],
                    'cleaned_text': c['cleaned_text'],
                    'sentences': c['sentences'],
                    'entities': c['entities'],
                    'type': clause_types[i],
                    'simplified': simplified_texts[i]
                }
                for i, c in enumerate(clauses)
            ],
            'legal_terms': [
                {
                    'term': t['term'] if isinstance(t, dict) else t[0],
                    'category': t.get('category') if isinstance(t, dict) else (t[1] if len(t) > 1 else ''),
                    'definition': t.get('definition') if isinstance(t, dict) else (t[2] if len(t) > 2 else None)
                }
                for t in legal_terms
            ],
            'clause_type_summary': {}
        }
        
        from collections import Counter
        type_counts = Counter(clause_types)
        results['clause_type_summary'] = dict(type_counts)
        
        # Generate charts using matplotlib/seaborn
        step = 'generate_charts'
        results['clause_type_chart'] = generate_clause_type_chart(results['clause_type_summary'])
        results['stats_chart'] = generate_stats_chart(original_metrics, simplified_metrics)
        
        return jsonify(results), 200
        
    except Exception as e:
        import traceback
        error_message = f"Processing error at {step}: {str(e)}"
        print(error_message)
        print(traceback.format_exc())
        return jsonify({'message': error_message}), 500
    
    finally:
        if temp_path.exists():
            temp_path.unlink()

def save_session(username, filename, clause_count):
    """Save session info to data/sessions.json"""
    SESSIONS_FILE.parent.mkdir(exist_ok=True)
    
    sessions = []
    if SESSIONS_FILE.exists():
        try:
            with open(SESSIONS_FILE, 'r') as f:
                sessions = json.load(f)
        except:
            sessions = []
    
    sessions.append({
        'username': username,
        'filename': filename,
        'clause_count': clause_count,
        'timestamp': datetime.now().isoformat()
    })
    
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=4)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'ClauseEase API is running'}), 200

if __name__ == '__main__':
    print("\n" + "="*80)
    print("CLAUSEEASE AI - CONTRACT LANGUAGE SIMPLIFIER")
    print("="*80)
    print("Starting Flask API Server...")
    print("API available at: http://localhost:5000")
    print("Frontend should connect to: http://localhost:5000/api")
    print("="*80 + "\n")
    
    # Load models on startup
    ensure_model_loaded()
    ensure_simplifier_loaded()
    
    app.run(debug=False, port=5000, host='0.0.0.0', use_reloader=False)