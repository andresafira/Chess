import pygame
from pygame.transform import scale, rotate
from pygame.image import load
from pygame.locals import *
from pygame import display

BOARD_PIXEL_W, BOARD_PIXEL_H = (1360, 1372)
OFFSET_PIXEL_X, OFFSET_PIXEL_Y = (48, 18)
FINAL_OFFSET_PIXEL_X, FINAL_OFFSET_PIXEL_Y = (1343, 1313)
board_contract_fac = 1/2

OFFSET_X, OFFSET_Y = OFFSET_PIXEL_X * board_contract_fac, OFFSET_PIXEL_Y * board_contract_fac
FINAL_OFFSET_X, FINAL_OFFSET_Y = FINAL_OFFSET_PIXEL_X * board_contract_fac, FINAL_OFFSET_PIXEL_Y * board_contract_fac
SIZE_W, SIZE_H = BOARD_PIXEL_W * board_contract_fac, BOARD_PIXEL_H * board_contract_fac
BLOCK_W, BLOCK_H = ((FINAL_OFFSET_X - OFFSET_X)/8,
                    (FINAL_OFFSET_Y - OFFSET_Y)/8)
background = scale(load('Images/board.png'), (SIZE_W, SIZE_H))

PIECES_PIXEL_W, PIECES_PIXEL_H = (800, 267)
piece_factor = 0.6
pieces_sprite = scale(load('Images/800px-Chess_Pieces_Sprite.svg.png'),
                      (PIECES_PIXEL_W*piece_factor, PIECES_PIXEL_H*piece_factor))
PIECE_BOX_W = piece_factor * PIECES_PIXEL_W / 6
PIECE_BOX_H = piece_factor * PIECES_PIXEL_H / 2
KING_X = 0
QUEEN_X = PIECE_BOX_W
BISHOP_X = 2 * PIECE_BOX_W
KNIGHT_X = 3 * PIECE_BOX_W
ROOK_X = 4 * PIECE_BOX_W
PAWN_X = 5 * PIECE_BOX_W

PRO_LIGHT_BOX = ((SIZE_W - 4*PIECE_BOX_W) / 2, (SIZE_H - PIECE_BOX_H) / 2, 4*PIECE_BOX_W, PIECE_BOX_H)
PRO_LIGHT_COLOR = (243, 221, 176)
PRO_DARK_BOX = (PRO_LIGHT_BOX[0] - 5, PRO_LIGHT_BOX[1] - 5, PRO_LIGHT_BOX[2] + 10, PRO_LIGHT_BOX[3] + 10)
PRO_DARK_COLOR = (0, 0, 0)
