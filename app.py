from flask import Flask, request, jsonify
from gomoku_engine import GomokuEngine
import numpy as np
import json
import traceback

app = Flask(__name__)
# Initialize with default board size, will be updated based on input
engine = GomokuEngine()

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"})

@app.route('/api/best-move', methods=['POST'])
def get_best_move():
    """
    API endpoint to get the best move for a given board state and player.

    Expected JSON payload:
    {
        "board": [[0, 0, 0, ...], [0, 1, 0, ...], ...],  # 2D array representing the board
        "player": 1  # 1 for black, 2 for white
    }

    Returns:
    {
        "move": [row, col],  # The suggested best move
        "message": "Success"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate input
        if 'board' not in data or 'player' not in data:
            return jsonify({"error": "Missing required fields: board and player"}), 400

        board = data['board']
        player = data['player']

        # Validate board
        if not isinstance(board, list) or not all(isinstance(row, list) for row in board):
            return jsonify({"error": "Board must be a 2D array"}), 400

        # Check if all rows have the same length
        if len(set(len(row) for row in board)) != 1:
            return jsonify({"error": "All rows in the board must have the same length"}), 400

        # Get board dimensions
        board_size = len(board)

        # Update engine board size if needed
        if engine.board_size != board_size:
            engine.board_size = board_size

        # Validate player
        if player not in [1, 2]:
            return jsonify({"error": "Player must be 1 (black) or 2 (white)"}), 400

        # Get the best move
        row, col = engine.get_best_move(board, player)

        return jsonify({
            "move": [int(row), int(col)],
            "message": "Success"
        })

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Simple welcome page."""
    return """
    <html>
        <head>
            <title>Gomoku API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { color: #333; }
                code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Gomoku API</h1>
            <p>Welcome to the Gomoku API. Use the following endpoint to get the best move:</p>
            <pre><code>POST /api/best-move</code></pre>
            <p>Example request body:</p>
            <pre><code>
{
    "board": [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 2, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ],
    "player": 1
}
            </code></pre>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Use a single worker to minimize resource usage
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)
