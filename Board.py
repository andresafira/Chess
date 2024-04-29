import pygame.mouse

from Piece import *
from constants import *
from utils import get_position
from random import randint


class Board:
    def __init__(self, board: Union[None, List[List]] = None):
        if board is None:
            self.board = list()
            self.initialize_board()
        else:
            self.board = board

        self.pawn_to_promote = None
        self.en_passant = None

    def initialize_board(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.board[0] = [Rook('black'), Knight('black'), Bishop('black'), Queen('black'), King('black'),
                         Bishop('black'), Knight('black'), Rook('black')]
        self.board[1] = [Pawn('black', 'down') for _ in range(8)]
        self.board[6] = [Pawn('white', 'up') for _ in range(8)]
        self.board[7] = [Rook('white'), Knight('white'), Bishop('white'), Queen('white'), King('white'),
                         Bishop('white'), Knight('white'), Rook('white')]

    def pop_piece(self, position) -> Piece:
        if not isvalid(position):
            raise ValueError('Position out of range')
        if position is None:
            return
        piece = self.board[position[1]][position[0]]
        self.board[position[1]][position[0]] = None
        return piece

    def put_piece(self, position, piece):
        if not isvalid(position):
            raise ValueError('Position out of range')
        self.board[position[1]][position[0]] = piece

    def is_check(self, color, position: Union[None, Tuple[int, int]] = None):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is None or piece.color == color:
                    continue
                _, caps = piece.get_mvs_and_caps(self.board, (j, i))
                for other in caps:
                    if position is None and isinstance(self.board[other[1]][other[0]], King):
                        return True
                    if position is not None and other == position:
                        return True
        return False

    def copy(self):
        new_board = [[None if self.board[i][j] is None else self.board[i][j].copy() for j in range(8)] for i in
                     range(8)]
        return Board(new_board)

    def move(self, original_coord, final_coord, color) -> tuple[str, str]:
        piece = self.pop_piece(original_coord)
        just_set_en_passant = False
        mv_type = 'move'
        flag = ''

        if isinstance(piece, Pawn):
            if self.en_passant is not None:
                other = self.board[self.en_passant[1]][self.en_passant[0]]
                if piece.color != other.color and final_coord == (self.en_passant[0], self.en_passant[1] - other.direction):
                    self.pop_piece(self.en_passant)
                    mv_type = 'capture'
            if piece.two:
                piece.two = False
                if abs(final_coord[1] - original_coord[1]) == 2:
                    just_set_en_passant = True
                    self.en_passant = final_coord

        if isinstance(piece, King) or isinstance(piece, Rook):
            piece.moved = True
            if isinstance(piece, King) and abs(final_coord[0] - original_coord[0]) == 2:
                mv_type = 'castle'
                if final_coord[0] > original_coord[0]:
                    rook = self.pop_piece((7, original_coord[1]))
                    rook.moved = True
                    self.put_piece((final_coord[0] - 1, final_coord[1]), rook)
                elif original_coord[0] > final_coord[0]:
                    rook = self.pop_piece((0, original_coord[1]))
                    rook.moved = True
                    self.put_piece((final_coord[0] + 1, final_coord[1]), rook)
        if self.board[final_coord[1]][final_coord[0]] is not None:
            mv_type = 'capture'
        self.put_piece(final_coord, piece)

        if self.is_check(opposite_color(color)):
            mv_type = 'check'

        if isinstance(piece, Pawn) and ((piece.color == 'white' and final_coord[1] == 0) or
                                        (piece.color == 'black' and final_coord[1] == 7)):
            flag = 'promotion'

        if not just_set_en_passant:
            self.en_passant = None

        return mv_type, flag


class Simulation:
    def __init__(self):
        self.board = Board()
        pygame.mixer.pre_init(44100, -16, 2, 1)
        pygame.init()
        pygame.display.set_caption("Chess")
        self.screen = pygame.display.set_mode((SIZE_W, SIZE_H))
        self.background = scale(load('Images/board.png'), (SIZE_W, SIZE_H))

        self.move_sound = pygame.mixer.Sound('Sounds/move_sound.wav')
        self.capture_sound = pygame.mixer.Sound('Sounds/capture_sound.wav')
        self.castle_sound = pygame.mixer.Sound('Sounds/castle_sound.wav')
        self.start_sound = pygame.mixer.Sound('Sounds/start_sound.wav')
        self.check_sound = pygame.mixer.Sound('Sounds/check_sound.wav')

        self.start_sound.play()

        self.down = False
        self.click_pos = None
        self.original_pos = None

        self.memory = [self.board.copy()]
        self.memory_max = 10
        self.memory_index = 0

        self.turn = 'white'

    def reset(self):
        self.board = Board()
        self.turn = 'white'

        self.down = None
        self.click_pos = None
        self.original_pos = None
        self.memory = [self.board.copy()]
        self.memory_index = 0

    def get_move_options(self, position):
        new_mvs = []
        new_caps = []
        piece = self.board.board[position[1]][position[0]]
        mvs, caps = piece.get_mvs_and_caps(self.board.board, position)

        if self.board.en_passant is not None and isinstance(piece, Pawn) and position[1] == self.board.en_passant[1] \
                and abs(position[0] - self.board.en_passant[0]) == 1:
            other = self.board.board[self.board.en_passant[1]][self.board.en_passant[0]]
            if piece.color != other.color:
                mvs.append((self.board.en_passant[0], self.board.en_passant[1] - other.direction))

        for mv in mvs:
            test = self.board.copy()
            x, _ = test.move(position, mv, opposite_color(piece.color))
            if isinstance(piece, King) and abs(mv[0] - position[0]) == 2 and not self.board.is_check(piece.color) and \
                    test.is_check(piece.color, ((mv[0] + position[0]) / 2, position[1])):
                continue
            if x != 'check':
                new_mvs.append(mv)
        for mv in caps:
            test = self.board.copy()
            x, _ = test.move(position, mv, opposite_color(piece.color))
            if x != 'check':
                new_caps.append(mv)
        return new_mvs, new_caps

    def draw_board(self):
        self.screen.blit(background, (0, 0))
        click_coord, original_coord = get_position(self.click_pos), get_position(self.original_pos)
        for i in range(8):
            for j in range(8):
                if self.board.board[i][j] is not None and (j, i) != original_coord:
                    self.board.board[i][j].draw(self.screen, (j, i))

        if self.down:
            piece = self.board.board[original_coord[1]][original_coord[0]]
            if piece is None:
                return
            mvs, caps = self.get_move_options(original_coord)

            for x, y in mvs:
                pygame.draw.circle(self.screen, (0, 100, 0),
                                   (OFFSET_X + (x + 0.5) * BLOCK_W, OFFSET_Y + (y + 0.5) * BLOCK_H), 10)
            for x, y in caps:
                pygame.draw.circle(self.screen, (100, 0, 0),
                                   (OFFSET_X + (x + 0.5) * BLOCK_W, OFFSET_Y + (y + 0.5) * BLOCK_H), 10)

            if piece.color == self.turn:
                offset_x = self.original_pos[0] - original_coord[0] * BLOCK_W - OFFSET_X
                offset_y = self.original_pos[1] - original_coord[1] * BLOCK_H - OFFSET_Y
                piece.draw(self.screen, None, (self.click_pos[0] - offset_x, self.click_pos[1] - offset_y))
            else:
                piece.draw(self.screen, original_coord)

    def update_memory(self):
        if self.memory_index == len(self.memory) - 1:
            self.memory.append(self.board.copy())
            if len(self.memory) > self.memory_max:
                self.memory.pop(0)
            else:
                self.memory_index += 1

    def promote(self):
        pygame.draw.rect(self.screen, PRO_DARK_COLOR, PRO_DARK_BOX)
        pygame.draw.rect(self.screen, PRO_LIGHT_COLOR, PRO_LIGHT_BOX)

        draw_piece(self.screen, None, QUEEN_X, self.turn, (PRO_LIGHT_BOX[0], PRO_LIGHT_BOX[1]))
        draw_piece(self.screen, None, ROOK_X, self.turn, (PRO_LIGHT_BOX[0] + PRO_LIGHT_BOX[2] / 4, PRO_LIGHT_BOX[1]))
        draw_piece(self.screen, None, BISHOP_X, self.turn,
                   (PRO_LIGHT_BOX[0] + 2 * PRO_LIGHT_BOX[2] / 4, PRO_LIGHT_BOX[1]))
        draw_piece(self.screen, None, KNIGHT_X, self.turn,
                   (PRO_LIGHT_BOX[0] + 3 * PRO_LIGHT_BOX[2] / 4, PRO_LIGHT_BOX[1]))
        pos = None
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

        if pos is not None and (pos[0] > PRO_LIGHT_BOX[0]) and (pos[0] < PRO_LIGHT_BOX[0] + PRO_LIGHT_BOX[2]) and \
                (pos[1] > PRO_LIGHT_BOX[1]) and (pos[1] < PRO_LIGHT_BOX[1] + PRO_LIGHT_BOX[3]):
            num = int((pos[0] - PRO_LIGHT_BOX[0]) // PIECE_BOX_W)
            self.board.pop_piece(self.board.pawn_to_promote)
            if num == 0:
                piece = Queen(self.turn)
            elif num == 1:
                piece = Rook(self.turn)
            elif num == 2:
                piece = Bishop(self.turn)
            elif num == 3:
                piece = Knight(self.turn)
            else:
                raise ValueError

            self.board.put_piece(self.board.pawn_to_promote, piece)
            self.board.pawn_to_promote = None
            self.update_memory()
            self.change_turn()

    def change_turn(self):
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

    def update_game(self, processed=False):
        if not processed:
            click_coord, original_coord = get_position(self.click_pos), get_position(self.original_pos)
        else:
            click_coord, original_coord = self.click_pos, self.original_pos

        if self.down or self.original_pos is None:
            return
        piece = self.board.board[original_coord[1]][original_coord[0]]
        if piece is None:
            return
        if piece.color != self.turn:
            return

        mvs, caps = self.get_move_options(original_coord)
        if click_coord != original_coord and (click_coord in mvs or click_coord in caps):
            mv_type, flag = self.board.move(original_coord, click_coord, self.turn)

            if mv_type == 'move':
                self.move_sound.play()
            elif mv_type == 'capture':
                self.capture_sound.play()
            elif mv_type == 'castle':
                self.castle_sound.play()
            elif mv_type == 'check':
                self.check_sound.play()

            if flag == 'promotion':
                self.board.pawn_to_promote = click_coord
            else:
                self.update_memory()
                self.change_turn()

    def run(self, play_against_AI: bool = False):
        run = True
        self.down = False
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == MOUSEBUTTONDOWN or self.down:
                    self.down = True
                    self.click_pos = pygame.mouse.get_pos()
                    if self.original_pos is None:
                        self.original_pos = self.click_pos
                if event.type == MOUSEBUTTONUP:
                    self.down = False
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reset()
                        break
                    if event.key == K_LEFT:
                        self.memory_index = max(self.memory_index - 1, 0)
                    elif event.key == K_RIGHT:
                        self.memory_index = min(self.memory_index + 1, len(self.memory) - 1)
                    self.change_turn()
                    self.board = self.memory[self.memory_index].copy()

            self.draw_board()

            if self.board.pawn_to_promote is not None:
                self.promote()
            elif self.turn == 'white' or not play_against_AI:
                self.update_game()
            elif self.turn == 'black' and self.memory_index == len(self.memory) - 1:
                mvs = []
                for i in range(8):
                    for j in range(8):
                        if self.board.board[i][j] is not None and self.board.board[i][j].color == 'black':
                            moves, caps = self.get_move_options((j, i))
                            moves = [((j, i), move) for move in moves]
                            caps = [((j, i), cap) for cap in caps]
                            mvs += moves
                            mvs += caps
                self.original_pos, self.click_pos = mvs[randint(0, len(mvs) - 1)]
                self.update_game(processed=True)

            if not self.down:
                self.original_pos = None
                self.click_pos = None

            pygame.display.update()

        pygame.quit()
