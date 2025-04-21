# Gomoku API

A lightweight Gomoku (Five in a Row) API that suggests the best move given a board position and player. Optimized to run with minimal resources (0.1 CPU and 512MB RAM).

## Features

- RESTful API to get the best move for a given board state
- Lightweight implementation using heuristic-based approach
- Optimized for low resource environments
- Docker support with resource constraints

## API Usage

### Get Best Move

```
POST /api/best-move
```

**Request Body:**

```json
{
    "board": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ],
    "player": 1
}
```

Where:
- `board` is a 2D array representing the current board state
  - `0` represents an empty cell
  - `1` represents a black stone (player 1)
  - `2` represents a white stone (player 2)
- `player` is the player for whom to find the best move (1 for black, 2 for white)

**Response:**

```json
{
    "move": [7, 6],
    "message": "Success"
}
```

Where `move` is an array of `[row, col]` coordinates for the suggested best move.

## Running Locally

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## Running with Docker

1. Build the Docker image:
   ```
   docker build -t gomoku-api .
   ```

2. Run the container with resource constraints:
   ```
   docker run -p 5000:5000 --cpus=0.1 --memory=512m gomoku-api
   ```

## Algorithm

The API uses a lightweight heuristic-based approach instead of traditional minimax with alpha-beta pruning to suggest moves. This approach is optimized for low resource environments and includes:

- Pattern recognition for attack and defense
- Scoring system for potential moves
- Prioritization of moves near existing stones
- Efficient board representation using NumPy

## License

MIT
