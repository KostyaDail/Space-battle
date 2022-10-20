# Полет космического корабля


import random, math
from superwires import games, color

games.init(screen_width=1920, screen_height=1080, fps=50)


class Wrapper(games.Sprite):
    """ Спрайт, который, двигаясь, огибает графический экран. """

    def update(self):
        """ Переносит спрайт на противоположную сторону экрана """
        if self.top > games.screen.height:
            self.bottom = 0
        if self.bottom < 0:
            self.top = games.screen.height
        if self.left > games.screen.width:
            self.right = 0
        if self.right < 0:
            self.left = games.screen.width

    def die(self):
        """ Разрушает объект"""
        self.destroy()


class Collider(Wrapper):
    """ Уничтожает объекты, которые могут столкнуться за пределами экрана"""

    def update(self):
        """ Проверяет, нет ли спрайтов, визуально перекрывающихся с данным """
        super(Collider, self).update()
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die()

    def die(self):
        """ Разрушает объект со взрывом"""
        new_explosion = Explosion(x=self.x, y=self.y)
        games.screen.add(new_explosion)
        self.destroy()


class Ship(Collider):
    """ Корабль игрока. """
    # загружаем изображение корабля
    ship_image = games.load_image("images/ship.png")
    # загружаем звук двигателя корабля
    sound = games.load_sound("sounds/thrust.wav")
    # угол, на который может одномоментно повернуть корабль
    ROTATION_STEP = 3
    # константа, на основе которой будет происходить изменение скорости корабля
    VELOCITY_STEP = 0.05
    # ограничение максимальной скорости игрока
    VELOCITY_MAX = 3
    # задержка, выпуска ракет (Для стрельбы с перерывами)
    MISSILE_DELAY = 15

    def __init__(self, game, x, y):
        """ Инициализирует спрайт с изображением космического корабля"""
        super(Ship, self).__init__(image=Ship.ship_image, x=x, y=y)
        self.game = game
        self.missile_wait = 0

    def update(self):
        """ Перемещение корабля на основе нажатых клавиш. """
        super(Ship, self).update()

        # Движение корабля с ускорением вперед
        if games.keyboard.is_pressed(games.K_UP):
            Ship.sound.play()
            # изменение скорости корабля с учетом угла поворота
            angle = self.angle * math.pi / 180  # convert to radians
            self.dx += Ship.VELOCITY_STEP * math.sin(angle)
            self.dy += Ship.VELOCITY_STEP * -math.cos(angle)
            # ограничение скорости
            self.dx = min(max(self.dx, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)
            self.dy = min(max(self.dy, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)

        # реверс
        if games.keyboard.is_pressed(games.K_DOWN):
            Ship.sound.play()
            # изменение скорости корабля с учетом угла поворота
            angle = self.angle * math.pi / 180  # convert to radians
            self.dx -= Ship.VELOCITY_STEP * math.sin(angle)
            self.dy -= Ship.VELOCITY_STEP * -math.cos(angle)
            # ограничение скорости
            self.dx = min(max(self.dx, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)
            self.dy = min(max(self.dy, -Ship.VELOCITY_MAX), Ship.VELOCITY_MAX)

        # интервал ожидания запуска ракеты
        if self.missile_wait > 0:
            self.missile_wait -= 1

        # выпуск ракеты, если нажат пробел и истек интервал ожидания
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x, self.y, self.angle)
            games.screen.add(new_missile)
            self.missile_wait = Ship.MISSILE_DELAY

        # вращает корабль при нажатии клавиш со стрелками
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.angle += Ship.ROTATION_STEP
        if games.keyboard.is_pressed(games.K_LEFT):
            self.angle -= Ship.ROTATION_STEP

    def die(self):
        """ Разрушает корабль и завершает игру. """
        self.game.end()
        super(Ship, self).die()


class Missile(Collider):
    """ Ракета, которую выпускает космический корабль """
    # изображение ракеты
    image = games.load_image("images/missile.png")
    # звук, ракетного залпа
    sound = games.load_sound("sounds/missile.wav")
    # начальное удаление ракеты от корабля
    BUFFER = 100
    # влияет на скорость полета ракеты
    VELOCITY_FACTOR = 10
    # продолжительность жизни ракеты
    LIFETIME = 50

    def __init__(self, ship_x, ship_y, ship_angle):
        """ Инициализирует спрайт с изображением ракеты"""
        Missile.sound.play()
        # преобразование в радианы
        angle = ship_angle * math.pi / 180
        # вычисление начальной позиции ракеты
        buffer_x = Missile.BUFFER * math.sin(angle)
        buffer_y = Missile.BUFFER * -math.cos(angle)
        x = ship_x + buffer_x
        y = ship_y + buffer_y

        # вычисление горизонтальной и вертикальной скорости ракеты
        dx = Missile.VELOCITY_FACTOR * math.sin(angle)
        dy = Missile.VELOCITY_FACTOR * -math.cos(angle)

        # создадим ракеты
        super(Missile, self).__init__(image=Missile.image,
                                      x=x, y=y,
                                      dx=dx, dy=dy)
        self.lifetime = Missile.LIFETIME

    def update(self):
        """ Перемещает ракету"""
        super(Missile, self).update()
        # если "срок годности" ракеты истек, она уничтожается
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()


class Asteroid(Wrapper):
    """Астероид, движущийся по экрану"""
    # константы, соответствующие трем размерам астероидов
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    # словарь, в котором эти константы соответствуют объекты-изображения астероидов
    images = {SMALL: games.load_image("images/asteroid_small.jpg"),
              MEDIUM: games.load_image("images/asteroid_med.jpg"),
              LARGE: games.load_image("images/asteroid_big.jpg")
              }
    # скорость, на основе которой будет определяться случайная скорость каждого астероида
    SPEED = 2
    # количество новых астероидов, на которые распадается один взорванный
    SPAWN = 2
    # исходная величина, для расчета очков за уничтоженный астероид
    POINTS = 30

    # Для слежки за кол-м астероидов
    total = 0

    def __init__(self, game, x, y, size):
        """ Инициализирует спрайт с изображением астероида"""
        Asteroid.total += 1
        super(Asteroid, self).__init__(
            image=Asteroid.images[size],
            x=x, y=y,
            dx=random.choice([-1, 1]) * Asteroid.SPEED * random.random() / size,
            dy=random.choice([-1, 1]) * Asteroid.SPEED * random.random() / size
        )
        self.game = game
        self.size = size

    def die(self):
        """ Разрушает астероид. """
        Asteroid.total -= 1

        # исходя из размера астероида вычислим сумму очков, которую игрок получит за взрыв этого астероида
        self.game.score.value += int(Asteroid.POINTS / self.size)
        self.game.score.right = games.screen.width - 10

        # если размеры астероида крупный или средний, заменить его двумя более мелкими астероидами
        if self.size != Asteroid.SMALL:
            for i in range(Asteroid.SPAWN):
                new_asteroid = Asteroid(game=self.game,
                                        x=self.x,
                                        y=self.y,
                                        size=self.size - 1)
                games.screen.add(new_asteroid)

        # если больше астероидов не осталось, переходим на следующий уровень
        if Asteroid.total == 0:
            self.game.advance()

        super(Asteroid, self).die()


class Explosion(games.Animation):
    """ Анимированный взрыв. """
    # загрузка звука взрыва
    sound = games.load_sound("sounds/explosion.wav")
    # список картинок - имен файлов, последовательность которых образует анимированный взрыв
    images = ["images/explosion1.bmp",
              "images/explosion2.bmp",
              "images/explosion3.bmp",
              "images/explosion4.bmp",
              "images/explosion5.bmp",
              "images/explosion6.bmp",
              "images/explosion7.bmp",
              "images/explosion8.bmp",
              "images/explosion9.bmp"]

    def __init__(self, x, y):
        super(Explosion, self).__init__(images=Explosion.images,
                                        x=x, y=y,
                                        repeat_interval=4, n_repeats=1,
                                        is_collideable=False)
        Explosion.sound.play()


class Game(object):
    """ Сама игра. """

    def __init__(self):
        """ Инициализирует объект Game. """
        # установить уровень
        self.level = 0

        # загрузить звук для повышения уровня
        self.sound = games.load_sound("sounds/level.mp3")

        # Создание объекта, в котором будет храниться текущий счет
        self.score = games.Text(value=0,
                                size=70,
                                color=color.white,
                                top=5,
                                right=games.screen.width - 10,
                                is_collideable=False)
        games.screen.add(self.score)

        # создание корабля для игрока
        self.ship = Ship(game=self,
                         x=games.screen.width / 2,
                         y=games.screen.height / 2)
        games.screen.add(self.ship)

    def play(self):
        """ Начинает игру. """
        # Запуск музыкальной темы
        games.music.load("sounds/theme.mid")
        games.music.play(-1)

        # загрузить и установить фон
        nebula_image = games.load_image("images/space.jpg")
        games.screen.background = nebula_image

        # переход к уровню 1
        self.advance()
        # убираем курсор
        games.mouse.is_visible = False
        # начало игры
        games.screen.mainloop()

    def advance(self):
        """ Переводит игру на следующий уровень. """
        self.level += 1

        # Буфер вокруг корабля
        BUFFER = 150

        # создание новых астероидов
        for i in range(self.level):
            # рассчитать x и y, чтобы они отстояли минимум на БУФЕРНОЕ расстояние от корабля

            # выберем минимальное расстояние по оси x и оси y
            x_min = random.randrange(BUFFER)
            y_min = BUFFER - x_min

            # исходя из этих значений, сгенерируем расстояние от корабля по оси x и оси y
            x_distance = random.randrange(x_min, games.screen.width - x_min)
            y_distance = random.randrange(y_min, games.screen.height - y_min)

            # рассчитаем местоположение на основе расстояния
            x = self.ship.x + x_distance
            y = self.ship.y + y_distance

            # если необходимо, вернем объект внутрь окна
            x %= games.screen.width
            y %= games.screen.height

            # создадим астероид
            new_asteroid = Asteroid(game=self,
                                    x=x, y=y,
                                    size=Asteroid.LARGE)
            games.screen.add(new_asteroid)

        # Отображение номера уровня
        level_message = games.Message(value="Level " + str(self.level),
                                      size=70,
                                      color=color.yellow,
                                      x=games.screen.width / 2,
                                      y=games.screen.width / 10,
                                      lifetime=3 * games.screen.fps,
                                      is_collideable=False)
        games.screen.add(level_message)

        # Звуковой эффект для перехода (кроме первого уровня)
        if self.level > 1:
            self.sound.play()

    def end(self):
        """ Завершает игру. """
        # 10 секундное отображение "Game Over"
        end_message = games.Message(value="Game Over",
                                    size=90,
                                    color=color.red,
                                    x=games.screen.width / 2,
                                    y=games.screen.height / 2,
                                    lifetime=10 * games.screen.fps,
                                    after_death=games.screen.quit,
                                    is_collideable=False)

        sound = games.load_sound("sounds/game_over.mp3")
        sound.play()
        games.screen.add(end_message)


def main():
    astrocrash = Game()
    astrocrash.play()


# поехали!
main()
