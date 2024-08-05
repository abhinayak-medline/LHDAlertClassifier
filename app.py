from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import subprocess
import html

app = Flask(__name__)

# Define the path to the database file
DATABASE = os.path.join('data', 'alerts.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def run_start_process():
    if not os.path.exists('data/process_complete.txt'):
        subprocess.run(['python', 'startProcess.py'], check=True)

run_start_process()

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/chart_data')
def chart_data():
    try:
        if not os.path.exists('data/process_complete.txt'):
            return jsonify({'error': 'Process not complete'}), 503

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get count of alerts per category
        query = '''
        SELECT category, COUNT(*) AS count
        FROM alerts
        GROUP BY category
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to a dictionary
        data = {row['category']: row['count'] for row in rows}
        
        return jsonify(data)
    
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Table not found'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'Failed to load data'}), 500


@app.route('/data')
def get_data():
    column = request.args.get('column', '')
    operator = request.args.get('operator', '')
    value = request.args.get('value', '')
    
    # Construct SQL query based on parameters
    query = 'SELECT * FROM alerts'
    params = []
    total_query = 'SELECT COUNT(*) FROM alerts'
    total_params = []

    if column and operator:
        if operator == "STARTS WITH":
            query += f" WHERE {column} LIKE ?"
            params.append(f'{value}%')
            total_query += f" WHERE {column} LIKE ?"
            total_params.append(f'{value}%')
        elif operator == "LIKE":
            query += f" WHERE {column} LIKE ?"
            params.append(f'%{value}%')
            total_query += f" WHERE {column} LIKE ?"
            total_params.append(f'%{value}%')
        elif operator == "NOT LIKE":
            query += f" WHERE {column} NOT LIKE ?"
            params.append(f'%{value}%')
            total_query += f" WHERE {column} NOT LIKE ?"
            total_params.append(f'%{value}%')
        elif operator == "=":
            query += f" WHERE {column} = ?"
            params.append(value)
            total_query += f" WHERE {column} = ?"
            total_params.append(value)
        elif operator == "!=":
            query += f" WHERE {column} != ?"
            params.append(value)
            total_query += f" WHERE {column} != ?"
            total_params.append(value)
        elif operator == "IS EMPTY":
            query += f" WHERE {column} IS NULL OR {column} = ''"
            total_query += f" WHERE {column} IS NULL OR {column} = ''"
        elif operator == "IS NOT EMPTY":
            query += f" WHERE {column} IS NOT NULL AND {column} != ''"
            total_query += f" WHERE {column} IS NOT NULL AND {column} != ''"

    try:
        if not os.path.exists('data/process_complete.txt'):
            return jsonify({'error': 'Process not complete'}), 503

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        cursor.execute(total_query, total_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Convert rows to a list of dictionaries
        data = [
            {
                'id': row['id'],
                'category': row['category'],
                'urgency': row['urgency'],
                'subject': row['subject'],
                'sender_name': row['sender_name'],
                'sender_email_address': row['sender_email_address'],
                'to_recipients': row['to_recipients'],
                'cc_recipients': row['cc_recipients'],
                'bcc_recipients': row['bcc_recipients'],
                'received_time': row['received_time'],
                'sent_on': row['sent_on'],
                'html_body': html.escape(row['html_body']),
                'text_body': row['text_body'],
                'attachments': row['attachments'],
                'size': row['size']
            }
            for row in rows
        ]
        
        # Add total count to the response
        return jsonify({
            'data': data,
            'total_count': total_count
        })
    
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Table not found'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'Failed to load data'}), 500

    
if __name__ == '__main__':
    app.run(debug=True)