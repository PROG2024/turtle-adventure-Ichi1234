"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x - 10, self.y - 10, self.x + 10, self.y + 10)
            self.canvas.coords(self.__id2, self.x - 10, self.y + 10, self.x + 10, self.y - 10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y
        self.time = 1
        self.x_speed, self.y_speed = 0, 0

        self.intro = 0
        self.begin, self.move, self.second_phase = False, False, False

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved. Yes, I know.
        player_x = self.game.player.x
        player_y = self.game.player.y
        direction = [player_x - self.x, player_y - self.y]

        # check the direction which way player approach
        if not self.second_phase and -60 < direction[0] < 60 and -55 < direction[1] < 55:
            if direction[1] > 0:
                self.y_speed = -8
            elif direction[1] < 0:
                self.y_speed = 8
        # if player near in first phase surprise him
        if not self.second_phase and self.y_speed != 0:
            self.y += self.y_speed
            self.intro = 1
            self.time += self.intro
        # animation begin second phase
        if self.time % 40 == 0 and not self.second_phase:
            self.y_speed = 0
            self.x, self.y = 400, 250
            self.time, self.intro = 1, 0

            for delete_enemy in [FencingEnemy, RandomWalkEnemy, StalkerEnemy, ChasingEnemy]:
                self.game.delete_all_enemy(delete_enemy)

            self.second_phase = True

        # running when user is near animation
        if self.second_phase and -50 < direction[0] < 50 and -50 < direction[1] < 50 and not self.begin:
            self.x_speed = 10

        # show second phase text
        elif self.second_phase and self.x == 0 and not self.begin:
            self.x_speed = 0
            self.x, self.y = -10, -10
            self.intro = 1
            self.second_phase_text()

        self.x -= self.x_speed

        # give time for player to read
        self.time += self.intro
        if self.time % 60 == 0 and not self.begin:
            self.canvas.delete("intro")
            self.time = 1
            self.begin = True
            self.summon_enemy()

        if self.begin and self.time % 40 == 0:
            self.summon_enemy()

        # 10 second pass
        if self.time % 210 == 0:
            self.move = True

        if self.move:
            # move to player when 10 second has passed
            if direction[0] > 0:
                self.x += 20
            elif direction[0] < 0:
                self.x -= 20

            if direction[1] > 0:
                self.y += 20
            elif direction[1] < 0:
                self.y -= 20

    def summon_enemy(self):
        """This code use for add enemy overtime during phase 2"""

        color = ["#0B2447", "#19376D", "#576CBC", "#1C6758"]

        if self.begin:
            for _ in range(4):
                random_walk = RandomWalkEnemy(self.game, random.randint(15, 20), random.choice(color))
                random_walk.x = random.randint(90, 600)
                random_walk.y = random.randint(0, 500)
                self.game.add_enemy(random_walk)

            for _ in range(2):
                teleporter = StalkerEnemy(self.game, 20, "purple", random.randrange(45, 85, 15))
                teleporter.x = 650
                teleporter.y = 200
                self.game.add_enemy(teleporter)

    def second_phase_text(self):
        """show introduction text"""

        font = ("Arial", 36, "bold")
        font2 = ("Arial", 20, "bold")
        self.canvas.create_text(self.game.screen_width / 2,
                                self.game.screen_height / 2 - 40,
                                text="Second Phase", font=font, fill="black", tags="intro")
        # actually it's ~ 55 second
        self.canvas.create_text(self.game.screen_width / 2,
                                self.game.screen_height / 2,
                                text="Victory awaits if you can endure for 10 seconds!",
                                font=font2, fill="black", tags="intro")

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
                (self.x - self.size / 2 < self.game.player.x < self.x + self.size / 2)
                and
                (self.y - self.size / 2 < self.game.player.y < self.y + self.size / 2)
        )

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x - self.size / 2, self.x + self.size / 2
        y1, y2 = self.y - self.size / 2, self.y + self.size / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y) and self.game.home.second_phase:
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
                (self.x - self.size / 2 < self.game.player.x < self.x + self.size / 2)
                and
                (self.y - self.size / 2 < self.game.player.y < self.y + self.size / 2)
        )

    def hit_wall(self) -> bool:
        return self.x < 10 or self.x > 790 or self.y < 10 or self.y > 490


# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.

class RandomWalkEnemy(Enemy):
    """
    Random walking enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.time = 0
        self.update_x = random.randint(-1, 1)
        self.update_y = random.randint(-1, 1)

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color, outline="black")

    def update(self) -> None:
        self.time += 1

        if self.time % 30 == 0:
            self.update_x = random.randint(-3, 3)
            self.update_y = random.randint(-3, 3)

        self.x += self.update_x
        self.y += self.update_y
        if self.hits_player():
            self.game.game_over_lose()

        if self.hit_wall():
            self.time = 0
            self.update_x *= -1
            self.update_y *= -1

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2,
                           )

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class ChasingEnemy(Enemy):
    """
    Chasing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.time = 0
        self.speed = 0
        self.update_x = random.randint(-1, 1)
        self.update_y = random.randint(-1, 1)

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="black", fill="red", width=2)

    def update(self) -> None:
        player_x = self.game.player.x
        player_y = self.game.player.y
        direction = [player_x - self.x, player_y - self.y]

        if direction[0] > 100 or direction[0] < -100:
            self.speed = 6
        else:
            self.speed = 3

        if direction[0] > 0 > self.speed:
            self.speed *= -1

        elif direction[0] < 0 < self.speed:
            self.speed *= -1

        self.x += self.speed

        if direction[1] > 0:
            self.y += 3
        elif direction[1] < 0:
            self.y -= 3

        if self.hits_player():
            self.game.game_over_lose()

        if self.hit_wall():
            self.time = 0
            self.update_x *= -1
            self.update_y *= -1

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2,
                           )

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class FencingEnemy(Enemy):
    """
    This enemy will move around finish point in square shape
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.x_speed = -3
        self.y_speed = 0

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill="blue")

    def update(self) -> None:

        # left border
        if self.x < self.game.home.x - 50:
            self.x, self.x_speed, self.y_speed = self.game.home.x - 50, 0, 3
        # right border
        elif self.x > self.game.home.x + 50:
            self.x, self.x_speed, self.y_speed = self.game.home.x + 50, 0, -3
        # top border
        elif self.y < self.game.home.y - 50:
            self.y, self.x_speed, self.y_speed = self.game.home.y - 50, -3, 0
        # bottom border
        elif self.y > self.game.home.y + 50:
            self.y, self.x_speed, self.y_speed = self.game.home.y + 50, 3, 0

        # enemy walking
        self.x += self.x_speed
        self.y += self.y_speed

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2,
                           )

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class StalkerEnemy(Enemy):
    """
    You can run, but you can't hide~~
    This enemy will teleport to in front of the player then run toward to player.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 timer: int):
        super().__init__(game, size, color)
        self.__id = None
        self.time = 0
        self.speed = 2
        self.teleport = 150
        self.timer = timer

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="black", fill="purple", width=2)

    def update(self) -> None:

        if self.game.waypoint.x - self.game.player.x > 0:
            self.teleport = 100
        else:
            self.teleport = -85

        # teleport to player
        if self.time % self.timer == 0:
            self.x = self.game.player.x + self.teleport
            self.y = self.game.player.y
        self.time += 1

        direction = [self.game.player.x - self.x, self.game.player.y - self.y]

        if direction[0] > 0 > self.speed:
            self.speed *= -1

        elif direction[0] < 0 < self.speed:
            self.speed *= -1

        self.x += self.speed

        if direction[1] > 0:
            self.y += 2
        elif direction[1] < 0:
            self.y -= 2

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2,
                           )

    def delete(self) -> None:
        self.canvas.delete(self.__id)


# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        color = ["#0B2447", "#19376D", "#576CBC", "#1C6758"]

        chaser_1 = ChasingEnemy(self.__game, 20, "red")
        chaser_1.x, chaser_1.y = 200, 100

        self.game.add_enemy(chaser_1)

        chaser_2 = ChasingEnemy(self.__game, 20, "red")
        chaser_2.x, chaser_2.y = 400, 400

        self.game.add_enemy(chaser_2)

        # create enemy depend on level difficulty
        for _ in range((self.level * 10) - 5):
            random_walk = RandomWalkEnemy(self.__game, random.randint(15, 20), random.choice(color))
            random_walk.x = random.randint(90, 600)
            random_walk.y = random.randint(0, 500)
            self.game.add_enemy(random_walk)

        shield_locate = [(-50, -50), (-50, 50), (50, -50), (50, 52)]
        for i in range(4):
            square_walk = FencingEnemy(self.__game, 20, "blue")
            square_walk.x = self.game.home.x + shield_locate[i][0]
            square_walk.y = self.game.home.y + shield_locate[i][1]
            self.game.add_enemy(square_walk)

        teleporter = StalkerEnemy(self.__game, 20, "purple", 40)
        teleporter.x, teleporter.y = 650, 200

        self.game.add_enemy(teleporter)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height - 1, self.screen_width - 1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width - 100, self.screen_height // 2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height // 2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def delete_all_enemy(self, enemy: Enemy):
        """delete all of the enemy of that specific type"""
        for remove in [i for i in self.enemies if isinstance(i, enemy)]:
            self.delete_element(remove)
            self.enemies.remove(remove)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Lose",
                                font=font,
                                fill="red")
