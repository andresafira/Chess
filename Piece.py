from utils import isvalid
from constants import *
from typing import *


def go_til_hit(board, position, direction):
    moves = []
    capture = None
    px = position[0] + direction[0]
    py = position[1] + direction[1]
    while isvalid((px, py)) and board[py][px] is None:
        moves.append((px, py))
        px += direction[0]
        py += direction[1]
    if isvalid((px, py)) and (board[py][px].color != board[position[1]][position[0]].color):
        capture = (px, py)
    return moves, capture


def draw_piece(screen: display, position: Union[Tuple[int, int], None], piece_x: float, color: str,
               final_position: Union[None, Tuple[int, int]] = None):
    if final_position is None:
        x = position[0] * BLOCK_W + OFFSET_X
        y = position[1] * BLOCK_H + OFFSET_Y
    else:
        x, y = final_position

    if color == 'white':
        area = (piece_x, 0, PIECE_BOX_H, PIECE_BOX_W)
    elif color == 'black':
        area = (piece_x, PIECE_BOX_H, PIECE_BOX_H, PIECE_BOX_W)
    else:
        raise ValueError('Invalid color: ', color)
    screen.blit(pieces_sprite, (x, y), area)


def opposite_color(color):
    if color == 'white':
        return 'black'
    return 'white'


class Piece:
    def __init__(self, color):
        self.color = color

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        raise NotImplementedError()

    def draw(self, screen: display, position: Union[None, Tuple[int, int]],
             final_position: Union[None, Tuple[int, int]] = None):
        raise NotImplementedError()

    def copy(self):
        raise NotImplementedError()


class Pawn(Piece):
    def __init__(self, color, direction: Union[str, int], two: bool = True):
        self.two = two
        super().__init__(color)
        if direction == 'down' or direction == 1:
            self.direction = 1
        else:
            self.direction = -1

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        move = (position[0], position[1] + self.direction)
        moves = []

        if not isvalid(move):
            return [], []
        if board[move[1]][move[0]] is None:
            moves = [move]

        two_move = (move[0], move[1] + self.direction)
        if self.two and isvalid(two_move) and board[two_move[1]][two_move[0]] is None and board[move[1]][move[0]] is None:
            moves.append(two_move)
        c1 = (move[0] - 1, move[1])
        c2 = (move[0] + 1, move[1])
        captures = []

        if isvalid(c1):
            pc1 = board[c1[1]][c1[0]]
            if pc1 is not None and pc1.color != self.color:
                captures.append(c1)
        if isvalid(c2):
            pc2 = board[c2[1]][c2[0]]
            if pc2 is not None and pc2.color != self.color:
                captures.append(c2)
        return moves, captures

    def draw(self, screen, position, final_position=None):
        draw_piece(screen, position, PAWN_X, self.color, final_position)

    def copy(self):
        return Pawn(color=self.color, direction=self.direction, two=self.two)


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        moves = []
        captures = []
        for x in [-2, -1, 1, 2]:
            for y in [-1, 1]:
                move = (position[0] + x, position[1] + (3 - abs(x))*y)
                if isvalid(move):
                    value = board[move[1]][move[0]]
                    if value is not None and value.color != self.color:
                        captures.append(move)
                    elif value is None:
                        moves.append(move)
        return moves, captures

    def draw(self, screen, position, final_position=None):
        draw_piece(screen, position, KNIGHT_X, self.color, final_position)

    def copy(self):
        return Knight(self.color)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        moves = []
        captures = []

        for x in (-1, 1):
            for y in (-1, 1):
                m, c = go_til_hit(board, position, (x, y))
                moves += m
                if c is not None:
                    captures.append(c)
        return moves, captures

    def draw(self, screen, position, final_position=None):
        draw_piece(screen, position, BISHOP_X, self.color, final_position)

    def copy(self):
        return Bishop(self.color)


class Rook(Piece):
    def __init__(self, color, moved=False):
        super().__init__(color)
        self.moved = moved

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        moves = []
        captures = []

        for x in (-1, 1):
            m, c = go_til_hit(board, position, (x, 0))
            moves += m
            if c is not None:
                captures.append(c)
        for y in (-1, 1):
            m, c = go_til_hit(board, position, (0, y))
            moves += m
            if c is not None:
                captures.append(c)
        return moves, captures

    def draw(self, screen, position, final_position=None):
        draw_piece(screen, position, ROOK_X, self.color, final_position)

    def copy(self):
        return Rook(self.color, self.moved)


class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        moves = []
        captures = []

        # Diagonal also horizontal movements
        for x in (-1, 1):
            for y in range(-1, 2):
                m, c = go_til_hit(board, position, (x, y))
                moves += m
                if c is not None:
                    captures.append(c)

        # Vertical movements
        for y in (-1, 1):
            m, c = go_til_hit(board, position, (0, y))
            moves += m
            if c is not None:
                captures.append(c)
        return moves, captures

    def draw(self, screen, position, final_position=None):
        draw_piece(screen, position, QUEEN_X, self.color, final_position)

    def copy(self):
        return Queen(self.color)


class King(Piece):
    def __init__(self, color, moved=False):
        super().__init__(color)
        self.moved = moved

    def check_castle_mvs(self, board, position):
        if self.moved:
            return []
        castles = []
        # Check right
        if board[position[1]][position[0] + 1] is None and \
                board[position[1]][position[0] + 2] is None and \
                isinstance(board[position[1]][7], Rook) and \
                not board[position[1]][7].moved:

            castles.append((position[0] + 2, position[1]))

        # Check left
        if board[position[1]][position[0] - 1] is None and \
                board[position[1]][position[0] - 2] is None and \
                board[position[1]][position[0] - 3] is None and \
                isinstance(board[position[1]][0], Rook) and \
                not board[position[1]][0].moved:
            castles.append((position[0] - 2, position[1]))

        return castles

    def get_mvs_and_caps(self, board: List[List], position: tuple) -> tuple:
        moves = []
        captures = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                move = (position[0] + x, position[1] + y)
                if isvalid(move) and (x != 0 or y != 0):
                    pc = board[move[1]][move[0]]
                    if pc is not None and pc.color != self.color:
                        captures.append(move)
                    elif pc is None:
                        moves.append(move)

        moves += self.check_castle_mvs(board, position)
        return moves, captures

    def draw(self, screen, position, final_position=None):
        draw_piece(screen, position, KING_X, self.color, final_position)

    def copy(self):
        return King(self.color, self.moved)
