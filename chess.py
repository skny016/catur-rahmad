import pygame
import sys

# Inisialisasi Pygame
pygame.init()

# Konstanta
WIDTH, HEIGHT = 1000, 700  # Lebih lebar untuk ruang kosong di kiri dan kanan
TILE_SIZE = 700 // 8  # Ukuran kotak pada papan catur
PADDING_VERTICAL = 0  # Ruang kosong atas dan bawah
PADDING_HORIZONTAL = 150  # Ruang kosong kiri dan kanan


# Warna
LIGHT_BROWN = (222, 184, 135)
DARK_BROWN = (139, 69, 19)


# Warna Tombol
BUTTON_COLOR = (0, 122, 255)  # Warna tombol normal (biru)
BUTTON_HOVER_COLOR = (0, 150, 255)  # Warna tombol saat hover (lebih terang)
BUTTON_TEXT_COLOR = (255, 255, 255)  # Warna teks tombol (putih)

# Muat gambar bidak catur
def load_images():
    pieces = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
    images = {}
    for piece in pieces:
        images[f'white_{piece}'] = pygame.image.load(f'Asset/img/white-{piece}.png')
        images[f'black_{piece}'] = pygame.image.load(f'Asset/img/black-{piece}.png')

    # Mengubah ukuran semua gambar bidak 
    new_size = (100, 100)  # Ukuran bidak
    for key in images:
        images[key] = pygame.transform.scale(images[key], new_size)
    return images

# Bidak Catur
class ChessPiece:
    def __init__(self, color, piece_type, image):
        self.color = color
        self.piece_type = piece_type
        self.image = image

# Buat papan catur
def create_board(images):
    board = [[None] * 8 for _ in range(8)]
    # Set up pawns
    for i in range(8):
        board[1][i] = ChessPiece('white', 'pawn', images['white_pawn'])
        board[6][i] = ChessPiece('black', 'pawn', images['black_pawn'])
    # Set up other pieces
    pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
    for i, piece in enumerate(pieces):
        board[0][i] = ChessPiece('white', piece, images[f'white_{piece}'])
        board[7][i] = ChessPiece('black', piece, images[f'black_{piece}'])
    return board

# Gambar papan catur
def draw_board(screen, board):
    # Menempatkan papan catur di tengah layar dengan padding
    for row in range(8):
        for col in range(8):
            # Tentukan warna kotak papan
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            # Menggambar kotak papan catur dengan padding horizontal dan vertikal
            pygame.draw.rect(screen, color, 
                             (col * TILE_SIZE + PADDING_HORIZONTAL, row * TILE_SIZE + PADDING_VERTICAL, TILE_SIZE, TILE_SIZE))
            piece = board[row][col]
            if piece is not None:
                # Menggambar bidak catur
                piece_rect = piece.image.get_rect()
                piece_rect.center = (col * TILE_SIZE + TILE_SIZE // 2 + PADDING_HORIZONTAL, 
                                     row * TILE_SIZE + TILE_SIZE // 2 + PADDING_VERTICAL)
                screen.blit(piece.image, piece_rect)


# Cek apakah pergerakan pion valid
def is_valid_pawn_move(piece, start_pos, end_pos, board):
    direction = 1 if piece.color == 'white' else -1
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    # Pion bergerak satu langkah maju
    if start_col == end_col and end_row == start_row + direction:
        return board[end_row][end_col] is None  # Tidak ada bidak di kotak tujuan
    
    # Pion bergerak dua langkah maju dari posisi awal
    if start_col == end_col and end_row == start_row + 2 * direction and (piece.color == 'white' and start_row == 1 or piece.color == 'black' and start_row == 6):
        # Pastikan tidak ada bidak di kotak yang dilewati
        if board[start_row + direction][start_col] is None and board[end_row][end_col] is None:
            return True

    # Pion menangkap bidak secara diagonal
    if abs(start_col - end_col) == 1 and end_row == start_row + direction and board[end_row][end_col] is not None and board[end_row][end_col].color != piece.color:
        return True
    
    return False

# Cek apakah pergerakan kuda valid
def is_valid_knight_move(piece, start_pos, end_pos, board):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    if (abs(start_row - end_row) == 2 and abs(start_col - end_col) == 1) or (abs(start_row - end_row) == 1 and abs(start_col - end_col) == 2):
        # Kuda bisa lompat jadi tidak perlu khawatir tentang bidak yang ada di antara
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    return False

# Cek apakah pergerakan benteng (rook) valid
def is_valid_rook_move(piece, start_pos, end_pos, board):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    
    # Rook hanya bisa bergerak horizontal (baris yang sama) atau vertikal (kolom yang sama)
    if start_row == end_row:  # Gerakan horizontal
        # Periksa apakah ada bidak yang menghalangi di antara posisi awal dan posisi akhir
        step = 1 if end_col > start_col else -1  # Tentukan arah gerakan kolom
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] is not None:
                return False
        # Jika kotak tujuan kosong atau ada bidak lawan, pergerakan sah
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    
    elif start_col == end_col:  # Gerakan vertikal
        # Periksa apakah ada bidak yang menghalangi di antara posisi awal dan posisi akhir
        step = 1 if end_row > start_row else -1  # Tentukan arah gerakan baris
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] is not None:
                return False
        # Jika kotak tujuan kosong atau ada bidak lawan, pergerakan sah
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    
    return False  # Jika bukan gerakan horizontal atau vertikal, tidak sah

# Cek apakah pergerakan bishop valid
def is_valid_bishop_move(piece, start_pos, end_pos, board):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    
    # Bishop bergerak diagonal, sehingga selisih baris dan kolom harus sama
    if abs(start_row - end_row) == abs(start_col - end_col):
        # Tentukan arah pergerakan
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        # Periksa apakah ada bidak yang menghalangi di jalur diagonal
        row, col = start_row + row_step, start_col + col_step
        while row != end_row and col != end_col:
            if board[row][col] is not None:
                return False
            row += row_step
            col += col_step
        
        # Jika kotak tujuan kosong atau ada bidak lawan, pergerakan sah
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    
    return False  # Jika bukan gerakan diagonal, tidak sah

    
# Cek apakah pergerakan queen valid
def is_valid_queen_move(piece, start_pos, end_pos, board):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    
    # Queen bergerak baik horizontal, vertikal, maupun diagonal
    if start_row == end_row:  # Gerakan horizontal
        # Periksa apakah ada bidak yang menghalangi di antara posisi awal dan posisi akhir
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] is not None:
                return False
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    
    elif start_col == end_col:  # Gerakan vertikal
        # Periksa apakah ada bidak yang menghalangi di antara posisi awal dan posisi akhir
        step = 1 if end_row > start_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] is not None:
                return False
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    
    elif abs(start_row - end_row) == abs(start_col - end_col):  # Gerakan diagonal
        # Tentukan arah pergerakan
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        # Periksa apakah ada bidak yang menghalangi di jalur diagonal
        row, col = start_row + row_step, start_col + col_step
        while row != end_row and col != end_col:
            if board[row][col] is not None:
                return False
            row += row_step
            col += col_step
        
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color

    return False  # Jika bukan gerakan horizontal, vertikal, atau diagonal, tidak sah


# Cek apakah pergerakan king valid
def is_valid_king_move(piece, start_pos, end_pos, board):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    
    # King hanya bisa bergerak satu langkah ke segala arah
    if abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1:
        # Jika kotak tujuan kosong atau ada bidak lawan, pergerakan sah
        return board[end_row][end_col] is None or board[end_row][end_col].color != piece.color
    
    return False  # Jika lebih dari satu langkah, tidak 


def get_valid_moves(piece, start_pos, board):
    valid_moves = []
    for row in range(8):
        for col in range(8):
            end_pos = (row, col)
            if piece.piece_type == 'pawn' and is_valid_pawn_move(piece, start_pos, end_pos, board):
                valid_moves.append(end_pos)
            elif piece.piece_type == 'knight' and is_valid_knight_move(piece, start_pos, end_pos, board):
                valid_moves.append(end_pos)
            elif piece.piece_type == 'rook' and is_valid_rook_move(piece, start_pos, end_pos, board):
                valid_moves.append(end_pos)
            elif piece.piece_type == 'bishop' and is_valid_bishop_move(piece, start_pos, end_pos, board):
                valid_moves.append(end_pos)
            elif piece.piece_type == 'queen' and is_valid_queen_move(piece, start_pos, end_pos, board):
                valid_moves.append(end_pos)
            elif piece.piece_type == 'king' and is_valid_king_move(piece, start_pos, end_pos, board):
                valid_moves.append(end_pos)
    return valid_moves

def draw_valid_moves(screen, valid_moves):
    # Gambar path yang valid dengan warna hijau
    for move in valid_moves:
        row, col = move
        pygame.draw.rect(screen, (0, 255, 0), (col * TILE_SIZE + PADDING_HORIZONTAL, row * TILE_SIZE + PADDING_VERTICAL, TILE_SIZE, TILE_SIZE), 5)  # Border hijau untuk valid moves

# Fungsi untuk menggambar teks status giliran
def draw_turn_status(screen, turn):
    font = pygame.font.SysFont('Sans Serif', 30)
    text = f"Turn: {'White' if turn == 'white' else 'Black'}"
    text_surface = font.render(text, True, (0, 0, 0))
    screen.blit(text_surface, (PADDING_HORIZONTAL - 140, PADDING_VERTICAL // 2))  # Menggambar status giliran

def draw_background(screen):
    # Menggambar ruang kosong abu-abu di sekitar papan catur
    screen.fill((169, 169, 169))  # Warna abu-abu (gray) untuk ruang kosong

# Fungsi untuk menggambar tombol restart
def draw_restart_button(screen):
    button_width, button_height = 150, 50
    button_rect = pygame.Rect(PADDING_HORIZONTAL - 150, HEIGHT // 2 - 25, button_width, button_height)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Cek apakah mouse berada di atas tombol
    if button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)

    # Tulis teks pada tombol
    font = pygame.font.SysFont('Arial', 20)
    text_surface = font.render("Restart", True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    
    return button_rect  # Kembalikan rect tombol untuk menangani klik

# Fungsi untuk mereset permainan
def reset_game(images):
    board = create_board(images)  # Buat papan baru
    return board


def is_king_in_check(board, turn):
    # Temukan posisi raja sesuai giliran
    king_pos = None
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.piece_type == 'king' and piece.color == turn:
                king_pos = (row, col)
                break
    
    if king_pos is None:
        return False  # Tidak ada raja ditemukan (harusnya tidak terjadi)

    # Periksa apakah ada bidak lawan yang dapat menyerang raja
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color != turn:  # Hanya bidak lawan
                valid_moves = get_valid_moves(piece, (row, col), board)
                if king_pos in valid_moves:
                    return True  # Raja dalam skak
    
    return False  # Tidak ada ancaman terhadap raja

def is_checkmate(board, turn):
    # Periksa apakah raja dalam keadaan skak
    if not is_king_in_check(board, turn):
        return False  # Tidak ada skak, jadi tidak skakmat
    
    # Cek apakah ada langkah yang dapat menghindari skak
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == turn:  # Hanya bidak dari pemain yang sedang giliran
                valid_moves = get_valid_moves(piece, (row, col), board)
                for move in valid_moves:
                    # Simulasi langkah sementara
                    original_piece = board[move[0]][move[1]]
                    board[move[0]][move[1]] = piece
                    board[row][col] = None
                    
                    # Cek apakah setelah langkah tersebut raja tetap dalam skak
                    if not is_king_in_check(board, turn):
                        # Kembalikan papan seperti semula jika ada langkah yang menyelamatkan raja
                        board[row][col] = piece
                        board[move[0]][move[1]] = original_piece
                        return False  # Skak dapat dihindari

                    # Kembalikan papan jika langkah tidak menyelamatkan raja
                    board[row][col] = piece
                    board[move[0]][move[1]] = original_piece
    return True  # Tidak ada langkah yang bisa menghindari skak

def draw_checkmate_status(screen, is_checkmate, turn):
    font = pygame.font.SysFont('Arial', 30)
    if is_checkmate:
        text = f"Checkmate! {'White' if turn == 'black' else 'Black'} wins!"
    else:
        text = f"{'White' if turn == 'white' else 'Black'} is in check!"
    text_surface = font.render(text, True, (255, 0, 0))  # Merah untuk menandakan skak atau skakmat
    screen.blit(text_surface, (WIDTH // 4, HEIGHT // 1.5))  # Tampilkan di bagian bawah layar


# Main loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    images = load_images()
    board = create_board(images)
    selected_piece = None
    selected_pos = None
    valid_moves = []
    turn = 'white'  # Pemain putih mulai
    game_over = False  # Indikator game over

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Jika permainan sudah selesai, tidak memproses gerakan bidak
            if game_over:
                # Periksa jika pemain mengklik tombol restart setelah permainan selesai
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    restart_button_rect = draw_restart_button(screen)
                    if restart_button_rect.collidepoint(x, y):
                        board = reset_game(images)
                        turn = 'white'
                        game_over = False  # Reset status game over
                        continue  # Lewati sisa kode setelah tombol restart
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = (x - PADDING_HORIZONTAL) // TILE_SIZE
                row = (y - PADDING_VERTICAL) // TILE_SIZE

                if not (0 <= row < 8 and 0 <= col < 8):  # Klik di luar papan
                    continue  # Abaikan klik di luar papan

                piece_at_target = board[row][col]

                if selected_piece is None:
                    if piece_at_target and piece_at_target.color == turn:
                        selected_piece = piece_at_target
                        selected_pos = (row, col)
                        valid_moves = get_valid_moves(selected_piece, selected_pos, board)
                else:
                    if (row, col) in valid_moves:
                        board[row][col] = selected_piece
                        board[selected_pos[0]][selected_pos[1]] = None

                        # Ganti giliran setelah gerakan
                        turn = 'black' if turn == 'white' else 'white'

                    selected_piece = None
                    selected_pos = None
                    valid_moves = []

        # Menggambar ulang layar
        screen.fill((255, 255, 255))
        draw_background(screen)
        draw_board(screen, board)

        if selected_piece:
            draw_valid_moves(screen, valid_moves)

        draw_turn_status(screen, turn)  # Menampilkan giliran pemain

        # Cek apakah ada skak atau skakmat
        checkmate = is_checkmate(board, turn)
        if checkmate or is_king_in_check(board, turn):
            game_over = True  # Menghentikan permainan jika ada skakmat
            draw_checkmate_status(screen, checkmate, turn)  # Tampilkan status checkmate

        draw_restart_button(screen)  # Gambar tombol restart
        pygame.display.flip()
        clock.tick(60)
