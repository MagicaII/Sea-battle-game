from random import choice, randint


class OutOfBorders(Exception):
    pass


class ShotDot(Exception):
    pass


class UsedDot(Exception):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, bow, size, orientation):
        self.bow = bow
        self.size = size
        self.orientation = orientation
        self.life = size

    @property
    def dots(self):
        dots_list = []
        if self.orientation == 'Horizontal':
            for i in range(self.size):
                dots_list.append(Dot(self.bow.x + i, self.bow.y))
                i += 1
        elif self.orientation == 'Vertical':
            for i in range(self.size):
                dots_list.append(Dot(self.bow.x, self.bow.y + i))
                i += 1
        return dots_list


class Board:
    def __init__(self):
        self.matrix = [
            ['О', 'О', 'О', 'О', 'О', 'О'],
            ['О', 'О', 'О', 'О', 'О', 'О'],
            ['О', 'О', 'О', 'О', 'О', 'О'],
            ['О', 'О', 'О', 'О', 'О', 'О'],
            ['О', 'О', 'О', 'О', 'О', 'О'],
            ['О', 'О', 'О', 'О', 'О', 'О'],
        ]
        self.ships_alive = 0
        self.hid = False

    def add_ship(self, ship: Ship):
        # исключения в появление корабля в неправильном месте
        for dot in ship.dots:
            if self.out(dot):
                raise OutOfBorders
            if self.matrix[dot.y - 1][dot.x - 1] == '■' or self.matrix[dot.y - 1][dot.x - 1] == '•':
                raise UsedDot
                
        for dot in ship.dots:
            self.matrix[dot.y - 1][dot.x - 1] = '■'
        self.ships_alive += ship.size
        
    #  Окружает каждую позицию корабля точками
    def contour(self, ship: Ship):
        for dot in ship.dots:
            for row in range(dot.y - 2, dot.y + 1):
                for col in range(dot.x - 2, dot.x + 1):
                    if not self.out(Dot(row + 1, col + 1)) and self.matrix[row][col] != '■':
                        self.matrix[row][col] = '•'

    def out(self, pos: Dot):
        return not (0 < pos.x < len(self.matrix) + 1 and 0 < pos.y < len(self.matrix[0]) + 1)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.matrix):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        res = res.replace("•", "O")
        return res

    def shot(self, cur: Dot):
        if self.out(cur):
            raise OutOfBorders
        if self.matrix[cur.y - 1][cur.x - 1] == 'T' or self.matrix[cur.y - 1][cur.x - 1] == 'X':
            raise UsedDot

        if self.matrix[cur.y - 1][cur.x - 1] == 'O' or self.matrix[cur.y - 1][cur.x - 1] == '•':
            self.matrix[cur.y - 1][cur.x - 1] = 'T'
            print('Miss!')
            return False
        if self.matrix[cur.y - 1][cur.x - 1] == '■':
            self.matrix[cur.y - 1][cur.x - 1] = 'X'
            print('Damaged!')
            self.ships_alive -= 1
            return True
class Player:
    def __init__(self, ally_board, enemy_board):
        self.ally_board = ally_board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                if self.enemy_board.shot(target):   #  В случае попадания делает повторный выстрел
                    continue
            except OutOfBorders:
                print('You shot outside of game field!')
            except UsedDot:
                print('you shot there before!')
            else:
                break

class User(Player):
    def ask(self):
        # просит пользователя ввести координаты до тех пор пока они не будут введены корректно
        while True:
            enter = input('Enter coordinates to shoot: ').split(',')
            if len(enter) != 2:
                print('Enter coordinated in given format: x,y ')
                continue
            if not (enter[0].isdigit() and enter[1].isdigit()):
                print('Use numbers')
                continue
                
            x, y = enter
            break
            
        return Dot(int(x), int(y))


class AI(Player):
    def ask(self):
        act = Dot(randint(1, 6), randint(1, 6))
        print(f"Computer move: ({act.x}, {act.y})")
        return act


class Game:
    def __init__(self):
        user_board = self.generate_board()
        ai_board = self.generate_board()
        ai_board.hid = True

        self.human = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)

    def generate_board(self):
        board = None
        while board is None:
            board = self.random_board()
        return board

    def random_board(self):
        ship_list = [3, 2, 2, 1, 1, 1, 1]
        orientation_list = ['Horizontal', 'Vertical']
        board = Board()
        count = 0
        for size in ship_list:
            while True:
                if count > 2000:
                    return None
                count += 1
                x, y = randint(1, 6), randint(1, 6)
                ship = Ship(Dot(x, y), size, choice(orientation_list))
                try:
                    board.add_ship(ship)
                    board.contour(ship)
                except:
                    continue
                else:
                    break
        return board

    def greet(self):
        print('Добро пожаловать в игру Морской Бой!')
        print('     Формат ввода координат: x,y')
        print('       x - столбцы, y - строки')
        print('---------------------------------------')

    def loop(self):
        while self.human.ally_board.ships_alive > 0 and self.human.enemy_board.ships_alive > 0:
            print('  Your field:\n')
            print(self.human.ally_board)
            print('  Computer field:\n')
            print(self.human.enemy_board)
            self.human.move()
            if self.human.enemy_board.ships_alive == 0:
                print('You won!')
            self.ai.move()
            if self.human.ally_board.ships_alive == 0:
                print('You lost')

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
