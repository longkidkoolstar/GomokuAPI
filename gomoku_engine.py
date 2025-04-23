import numpy as np
from typing import Tuple, List, Optional, Dict
import time

class GomokuEngine:
    """
    A lightweight Gomoku (Five in a Row) engine optimized for low resource usage.
    Uses heuristic-based approach with opening book strategies to suggest moves.
    Inspired by the winning strategy from https://github.com/fucusy/gomoku-first-move-always-win
    """

    def __init__(self, board_size: int = 15):
        """Initialize the Gomoku engine with an empty board."""
        self.board_size = board_size
        self.empty = 0
        self.black = 1  # Player 1
        self.white = 2  # Player 2

        # Opening book for black (first player)
        # Key: board state as string, Value: best move as (row, col)
        self.opening_book = self._initialize_opening_book()

        # Threat patterns and their scores
        self.threat_patterns = {
            # Five in a row (win)
            'five': 100000,
            # Open four (one move away from winning)
            'open_four': 10000,
            # Closed four (can be blocked)
            'closed_four': 5000,
            # Open three (can lead to open four)
            'open_three': 1000,
            # Closed three (can be blocked)
            'closed_three': 500,
            # Open two
            'open_two': 100,
            # Closed two
            'closed_two': 50
        }

    @property
    def board_size(self) -> int:
        """Get the current board size."""
        return self._board_size

    @board_size.setter
    def board_size(self, size: int):
        """Set the board size."""
        self._board_size = size

    def _initialize_opening_book(self) -> Dict[str, Tuple[int, int]]:
        """
        Initialize the opening book with known good first moves and responses.
        This is a simplified version of the opening book from the winning strategy.
        """
        book = {}

        # Empty board - start in the center
        book[self._board_to_string(np.zeros((15, 15), dtype=np.int8))] = (7, 7)

        # Common opening patterns and responses
        # These are based on proven winning strategies for black

        # If white plays adjacent to center, black should play on the opposite side
        center = 7
        for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            board = np.zeros((15, 15), dtype=np.int8)
            board[center, center] = self.black  # Black plays center
            board[center + dr, center + dc] = self.white  # White plays adjacent
            book[self._board_to_string(board)] = (center - dr, center - dc)  # Black plays opposite

        # If white plays two steps away, black should play between
        for dr, dc in [(0, 2), (2, 0), (2, 2), (2, -2)]:
            board = np.zeros((15, 15), dtype=np.int8)
            board[center, center] = self.black  # Black plays center
            board[center + dr, center + dc] = self.white  # White plays two steps away
            book[self._board_to_string(board)] = (center + dr//2, center + dc//2)  # Black plays between

        return book

    def _board_to_string(self, board: np.ndarray) -> str:
        """
        Convert a board state to a string representation for the opening book.
        Only includes positions that have stones to keep the representation compact.
        """
        positions = []
        black_positions = np.where(board == self.black)
        white_positions = np.where(board == self.white)

        for r, c in zip(black_positions[0], black_positions[1]):
            positions.append(f"B{r},{c}")

        for r, c in zip(white_positions[0], white_positions[1]):
            positions.append(f"W{r},{c}")

        return "_".join(sorted(positions))

    def get_best_move(self, board: List[List[int]], player: int) -> Tuple[int, int]:
        """
        Find the best move for the given player on the current board.

        Args:
            board: 2D list representing the board state (0=empty, 1=black, 2=white)
            player: Which player to find the best move for (1=black, 2=white)

        Returns:
            Tuple of (row, col) for the best move
        """
        start_time = time.time()

        # Convert board to numpy array for efficiency
        board_array = np.array(board, dtype=np.int8)

        # Check opening book first
        board_str = self._board_to_string(board_array)
        if board_str in self.opening_book:
            return self.opening_book[board_str]

        # If board is empty or nearly empty, play near the center
        stone_count = np.count_nonzero(board_array)
        if stone_count == 0:
            center = self.board_size // 2
            return (center, center)

        # Check for immediate winning moves or blocking opponent's winning moves
        immediate_move = self._check_immediate_threats(board_array, player)
        if immediate_move:
            return immediate_move

        # Get all valid moves (empty cells)
        valid_moves = self._get_valid_moves(board_array)

        # If there's only one valid move, return it
        if len(valid_moves) == 1:
            return valid_moves[0]

        # Score each valid move
        move_scores = {}
        for move in valid_moves:
            score = self._evaluate_move(board_array, move, player)
            move_scores[move] = score

        # Return the move with the highest score
        best_move = max(move_scores.items(), key=lambda x: x[1])[0]

        # Print time taken for debugging (can be removed in production)
        elapsed = time.time() - start_time
        print(f"Move calculation took {elapsed:.3f} seconds")

        return best_move

    def _check_immediate_threats(self, board: np.ndarray, player: int) -> Optional[Tuple[int, int]]:
        """
        Check for immediate winning moves or blocking opponent's winning moves.
        """
        opponent = 3 - player  # Switch between 1 and 2

        # Get all valid moves
        valid_moves = self._get_valid_moves(board)

        # First check if we can win in one move
        for move in valid_moves:
            row, col = move
            test_board = board.copy()
            test_board[row, col] = player

            # Check if this move creates a winning line
            for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                if self._check_line(test_board, row, col, dr, dc, player, 5):
                    return move

        # Then check if we need to block opponent's winning move
        for move in valid_moves:
            row, col = move
            test_board = board.copy()
            test_board[row, col] = opponent

            # Check if opponent would win with this move
            for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                if self._check_line(test_board, row, col, dr, dc, opponent, 5):
                    return move

        return None

    def _get_valid_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """Get all valid moves (empty cells) on the board."""
        valid_moves = []

        # Only consider cells that are near existing stones to reduce search space
        rows, cols = np.where(board > 0)
        if len(rows) == 0:
            # If board is empty, return center position
            center = self.board_size // 2
            return [(center, center)]

        # Consider cells within 2 spaces of existing stones
        for r, c in zip(rows, cols):
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nr, nc = r + dr, c + dc
                    if (0 <= nr < self.board_size and
                        0 <= nc < self.board_size and
                        board[nr, nc] == 0 and
                        (nr, nc) not in valid_moves):
                        valid_moves.append((nr, nc))

        return valid_moves

    def _evaluate_move(self, board: np.ndarray, move: Tuple[int, int], player: int) -> float:
        """
        Evaluate a potential move and return a score.
        Higher scores indicate better moves.
        """
        opponent = 3 - player  # Switch between 1 and 2
        row, col = move

        # Make a copy of the board and apply the move
        test_board = board.copy()
        test_board[row, col] = player

        # Initialize score
        score = 0.0

        # Check all 4 directions
        directions = [
            (1, 0),   # Vertical
            (0, 1),   # Horizontal
            (1, 1),   # Diagonal down-right
            (1, -1),  # Diagonal down-left
        ]

        # Check for winning move
        for dr, dc in directions:
            # Check if this move creates a winning line
            if self._check_line(test_board, row, col, dr, dc, player, 5):
                return self.threat_patterns['five']  # Immediate win

        # Check for blocking opponent's winning move
        test_board[row, col] = opponent
        for dr, dc in directions:
            if self._check_line(test_board, row, col, dr, dc, opponent, 5):
                score += self.threat_patterns['five'] * 0.9  # High priority to block

        # Reset the test board
        test_board[row, col] = player

        # Check for creating open fours (four in a row with empty spaces at both ends)
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, player, 4):
                score += self.threat_patterns['open_four']
            elif self._check_line(test_board, row, col, dr, dc, player, 4):
                score += self.threat_patterns['closed_four']

        # Check for creating open threes
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, player, 3):
                score += self.threat_patterns['open_three']
            elif self._check_line(test_board, row, col, dr, dc, player, 3):
                score += self.threat_patterns['closed_three']

        # Check for creating open twos
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, player, 2):
                score += self.threat_patterns['open_two']
            elif self._check_line(test_board, row, col, dr, dc, player, 2):
                score += self.threat_patterns['closed_two']

        # Check for blocking opponent's threats
        test_board[row, col] = opponent

        # Block opponent's open fours
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, opponent, 4):
                score += self.threat_patterns['open_four'] * 0.8
            elif self._check_line(test_board, row, col, dr, dc, opponent, 4):
                score += self.threat_patterns['closed_four'] * 0.8

        # Block opponent's open threes
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, opponent, 3):
                score += self.threat_patterns['open_three'] * 0.7

        # Prefer center and central areas
        center = self.board_size // 2
        distance_to_center = abs(row - center) + abs(col - center)
        centrality_score = max(0, 10 - distance_to_center) * 10
        score += centrality_score

        # Add a small random factor to break ties
        score += np.random.random() * 0.1

        return score

    def _check_line(self, board: np.ndarray, row: int, col: int, dr: int, dc: int,
                   player: int, length: int) -> bool:
        """
        Check if there are 'length' stones of 'player' in a line in direction (dr, dc)
        starting from (row, col).
        """
        count = 0

        # Check in positive direction
        r, c = row, col
        while (0 <= r < self.board_size and
               0 <= c < self.board_size and
               board[r, c] == player and
               count < length):
            count += 1
            r += dr
            c += dc

        # Check in negative direction
        r, c = row - dr, col - dc
        while (0 <= r < self.board_size and
               0 <= c < self.board_size and
               board[r, c] == player and
               count < length):
            count += 1
            r -= dr
            c -= dc

        return count >= length

    def _check_open_line(self, board: np.ndarray, row: int, col: int, dr: int, dc: int,
                        player: int, length: int) -> bool:
        """
        Check if placing a stone at (row, col) creates an open line of 'length'
        in direction (dr, dc). An open line has empty spaces at both ends.
        """
        # First, check if there's a line of required length
        if not self._check_line(board, row, col, dr, dc, player, length):
            return False

        # Now check if at least one end is open
        # Check positive direction
        r, c = row, col
        for _ in range(length):
            r += dr
            c += dc

        pos_open = (0 <= r < self.board_size and
                   0 <= c < self.board_size and
                   board[r, c] == 0)

        # Check negative direction
        r, c = row, col
        for _ in range(length):
            r -= dr
            c -= dc

        neg_open = (0 <= r < self.board_size and
                   0 <= c < self.board_size and
                   board[r, c] == 0)

        return pos_open or neg_open
