import numpy as np
from typing import Tuple, List, Optional

class GomokuEngine:
    """
    A lightweight Gomoku (Five in a Row) engine optimized for low resource usage.
    Uses heuristic-based approach instead of deep tree search to suggest moves.
    """

    def __init__(self, board_size: int = 15):
        """Initialize the Gomoku engine with an empty board."""
        self.board_size = board_size
        self.empty = 0
        self.black = 1  # Player 1
        self.white = 2  # Player 2

    @property
    def board_size(self) -> int:
        """Get the current board size."""
        return self._board_size

    @board_size.setter
    def board_size(self, size: int):
        """Set the board size."""
        self._board_size = size

    def get_best_move(self, board: List[List[int]], player: int) -> Tuple[int, int]:
        """
        Find the best move for the given player on the current board.

        Args:
            board: 2D list representing the board state (0=empty, 1=black, 2=white)
            player: Which player to find the best move for (1=black, 2=white)

        Returns:
            Tuple of (row, col) for the best move
        """
        # Convert board to numpy array for efficiency
        board_array = np.array(board, dtype=np.int8)

        # If board is empty or nearly empty, play near the center
        stone_count = np.count_nonzero(board_array)
        if stone_count <= 1:
            center = self.board_size // 2
            return (center, center)

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
        return best_move

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

        # Check all 8 directions
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
                return 10000  # Immediate win

        # Check for blocking opponent's winning move
        test_board[row, col] = opponent
        for dr, dc in directions:
            if self._check_line(test_board, row, col, dr, dc, opponent, 5):
                score += 5000  # High priority to block

        # Reset the test board
        test_board[row, col] = player

        # Check for creating open fours (four in a row with empty spaces at both ends)
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, player, 4):
                score += 1000

        # Check for creating open threes
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, player, 3):
                score += 100

        # Check for creating open twos
        for dr, dc in directions:
            if self._check_open_line(test_board, row, col, dr, dc, player, 2):
                score += 10

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
