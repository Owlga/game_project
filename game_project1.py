import sys
import pygame
import random
import sqlite3


all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()  # группа для платформы (в ней будет один элемент - основная платформа)
borders = pygame.sprite.Group()  # группа для границ (в ней будет нижняя граница поля)


class RememberScore:  # работа с бд
    def __init__(self, score_now: int, max_combo_now: int):
        self.score_now = score_now
        self.max_combo_now = max_combo_now
        self.max_score = score_now
        self.max_combo = max_combo_now

    def write_new_result(self):  # запись текущих результатов
        conn = sqlite3.connect('files/database.sqlite')
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT
                        NOT NULL
                        UNIQUE,
            score       INTEGER NOT NULL,
            combo       INTEGER NOT NULL,
            best_score  INTEGER NOT NULL,
            best_combo  INTEGER NOT NULL
        );""")

        elements = cur.execute("""SELECT * FROM results""").fetchall()
        if len(elements) != 0:
            last = elements[-1]
            last_max_score, last_max_combo = last[-2], last[-1]
            self.max_score = max(self.max_score, last_max_score)
            self.max_combo = max(self.max_combo, last_max_combo)

        cur.execute(f"""INSERT INTO results(score, combo, best_score, best_combo)
                             VALUES ('{self.score_now}', '{self.max_combo_now}', 
                             '{self.max_score}', '{self.max_combo}')""")

        conn.commit()
        conn.close()

    def get_best_results(self):  # функция, возвращающая лучшие результаты зв все время
        ans = (self.max_score, self.max_combo)
        return ans


class Platform(pygame.sprite.Sprite):  # платформа, управляемая игроком с помощью перемещения мыши
    def __init__(self, x: int):
        super().__init__(all_sprites)
        self.lent = 80
        self.image = pygame.Surface((self.lent, 20))
        self.color = pygame.Color('grey')
        self.image.fill(self.color)
        self.x = x
        self.rect = pygame.Rect(self.x, 500, self.lent, 20)
        pygame.draw.rect(self.image, self.color, self.rect, 3)
        self.add(platforms)

    def update(self, *args):  # перемещение платформы
        if args:
            x = args[0][0]  # координата по горизонтали, к которой нужно переместиться
            while self.x < x and x <= 600 - self.lent:
                self.x += 1
                self.rect = self.rect.move(1, 0)
            while self.x > x and x <= 600 - self.lent:
                self.x -= 1
                self.rect = self.rect.move(-1, 0)

    def change_len(self):  # изменение длины, если не больше 120
        if self.lent < 120:
            self.lent += 10
            self.image = pygame.Surface((self.lent, 20))
            self.image.fill(self.color)
            self.rect = pygame.Rect(self.x, 500, self.lent, 20)
            pygame.draw.rect(self.image, self.color, self.rect, 3)

    def set_len(self):  # сокращение длины обратно
        self.lent = 80
        self.image = pygame.Surface((self.lent, 20))
        self.image.fill(self.color)
        self.rect = pygame.Rect(self.x, 500, self.lent, 20)
        pygame.draw.rect(self.image, self.color, self.rect, 3)


class Border(pygame.sprite.Sprite):  # граница поля
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.Surface((600, 10))
        self.color = pygame.Color('black')
        self.image.fill(self.color)
        self.rect = pygame.Rect(0, 590, 600, 10)
        pygame.draw.rect(self.image, self.color, self.rect, 3)
        self.add(borders)


class FirstNote(pygame.sprite.Sprite):  # обычный падающий объект
    def __init__(self):
        super().__init__(all_sprites)
        self.image = pygame.Surface((20, 20))
        self.color = pygame.Color('blue')
        self.image.fill(self.color)
        self.rect = pygame.Rect(random.randint(0, 580), 45, 20, 20)
        pygame.draw.rect(self.image, self.color, self.rect, 3)

    def update(self):
        if pygame.sprite.spritecollideany(self, platforms):  # если поймали
            stat.update(score=1, combo=1)
            if stat.combo % 10 == 0:
                stat.add_hp()
            self.kill()  # убиваем, чтобы потом создать новую
        elif pygame.sprite.spritecollideany(self, borders):  # если не поймали
            player.set_len()
            stat.update(hp=-1)
            self.kill()  # убиваем, чтобы потом создать новую
        else:
            self.rect = self.rect.move(0, 10)  # иначе продолжает падать


class YellowNote(FirstNote):  # падающий объект, увеличивающий размер платформы
    def __init__(self):
        super().__init__()
        self.color = pygame.Color('yellow')
        self.image.fill(self.color)
        pygame.draw.rect(self.image, self.color, self.rect, 3)

    def update(self):
        if pygame.sprite.spritecollideany(self, platforms):  # если поймали
            stat.update(score=1, combo=1)
            if stat.combo % 10 == 0:
                stat.add_hp()
            player.change_len()  # расширяем платформу
            self.kill()  # убиваем, чтобы потом создать новую
        elif pygame.sprite.spritecollideany(self, borders):  # если не поймали
            player.set_len()  # возвращаем начальную длину платформы
            stat.update(hp=-1)
            self.kill()  # убиваем, чтобы потом создать новую
        else:
            self.rect = self.rect.move(0, 10)  # иначе продолжает падать


class GreenNote(FirstNote):  # падающий объект, восстанавливающий 2 балла жизни
    def __init__(self):
        super().__init__()
        self.color = pygame.Color('green')
        self.image.fill(self.color)
        pygame.draw.rect(self.image, self.color, self.rect, 3)

    def update(self):
        if pygame.sprite.spritecollideany(self, platforms):  # если поймали
            stat.update(hp=2, score=1, combo=1)
            if stat.combo % 10 == 0:
                stat.add_hp()
            self.kill()  # убиваем, чтобы потом создать новую
        elif pygame.sprite.spritecollideany(self, borders):  # если не поймали
            player.set_len()
            stat.update(hp=-1)
            self.kill()  # убиваем, чтобы потом создать новую
        else:
            self.rect = self.rect.move(0, 10)  # иначе продолжает падать


class RedNote(FirstNote):  # падающий объект, убирающий 5 баллов жизни
    def __init__(self):
        super().__init__()
        self.color = pygame.Color('red')
        self.image.fill(self.color)
        pygame.draw.rect(self.image, self.color, self.rect, 3)

    def update(self):
        if pygame.sprite.spritecollideany(self, platforms):  # если поймали
            stat.update(hp=-5, combo=0)
            self.kill()  # убиваем, чтобы потом создать новую
        elif pygame.sprite.spritecollideany(self, borders):  # если не поймали
            stat.update(combo=1)
            self.kill()  # убиваем, чтобы потом создать новую
        else:
            self.rect = self.rect.move(0, 10)  # иначе продолжает падать


class Statistics:  # вся статистика
    def __init__(self):
        self.ep = False
        self.hp = 5
        self.score = 0
        self.combo = 0
        self.max_combo = 0

    def update(self, hp=0, score=0, combo=0):
        self.ep = True
        self.hp += hp
        self.score += score
        if combo:
            self.combo += 1
        else:
            self.combo = 0
        self.max_combo = max(self.max_combo, self.combo)

    def add_hp(self):
        self.hp += 1


def set_stat(screen):  # отображение на экране статистики во время игрового процесса
    font = pygame.font.Font(None, 50)
    text1 = font.render(f"lifes: {stat.hp}", True, (120, 255, 120))
    text2 = font.render(f"score: {stat.score}", True, (120, 255, 120))
    text3 = font.render(f"combo: {stat.combo}", True, (120, 255, 120))
    screen.blit(text1, (0, 0))
    screen.blit(text2, (200, 0))
    screen.blit(text3, (400, 0))
    pygame.draw.rect(screen, (120, 255, 120), (0, 0, 600, 50), 2)


def set_start_screen(screen):  # стартовый экран
    screen.fill((76, 141, 38))
    intro_text = [" ПРАВИЛА ИГРЫ", "",
                  " Ловите квадраты с помощью платформы",
                  " Управляйте платформой движением мыши",
                  " Если вы пропустите квадрат, вычтется жизнь",
                  " В начале у вас пять жизней",
                  " Зеленый восстанавливает две жизни",
                  " Красный убирает пять жизней",
                  " Желтый расширяет платформу",
                  " Синий обычный",
                  " При количестве комбо % 10, восстанавливается жизнь ",
                  " Чтобы продолжить, нажмите ЛКМ", "", "",]
    font = pygame.font.Font(None, 30)
    text_coord = 60
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 0
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def set_final_screen(screen):  # финальный экран
    db_sample = RememberScore(stat.score, stat.max_combo)  # вызов класса для работы с бд
    db_sample.write_new_result()
    best_score, best_combo = db_sample.get_best_results()
    for s in all_sprites:
        s.kill()
    screen.fill((224, 32, 11))
    font = pygame.font.Font(None, 45)
    text0 = font.render("  ВЫ ПРОИГРАЛИ", True, 'white')
    text1 = font.render(f"  вы набрали столько баллов: {stat.score}", True, 'white')
    text2 = font.render(f"  максимальное комбо: {stat.max_combo}", True, 'white')
    text3 = font.render("  лучший результат:", True, 'cadetblue1')  # вывод фраз с лучшими результатами
    text4 = font.render(f"  баллы: {best_score}, комбо: {best_combo}", True, 'cadetblue1')
    screen.blit(text0, (0, 100))
    screen.blit(text1, (0, 200))
    screen.blit(text2, (0, 200 + text1.get_size()[1]))
    screen.blit(text3, (0, 300))
    screen.blit(text4, (0, 300 + text3.get_size()[1]))
    if best_score == stat.score or best_combo == stat.max_combo:  # фразы на случай лучших результатов в любой категории
        text_win1 = font.render("  В этот раз Вы получили лучшие баллы", True, 'deepskyblue1')
        text_win2 = font.render("  за все время! Поздравляем!", True, 'deepskyblue1')
        screen.blit(text_win1, (0, 400))
        screen.blit(text_win2, (0, 400 + text_win1.get_size()[1]))


if __name__ == '__main__':
    pygame.init()
    size = 600, 600
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('note game')
    screen.fill('black')

    fps = 30
    clock = pygame.time.Clock()

    player = Platform(210)  # создаем платформу
    Border()  # ставим границу
    note_on = False  # есть ли сейчас нота на поле
    stat = Statistics()  # объект статистики
    final = None  # нужен ли финальный экран
    start = True  # нужен ли стартовый экран

    running = True
    while running:
        screen.fill('black')
        while start:  # стартовый экран, в это время все остальные функции не работают
            pygame.mouse.set_visible(True)
            set_start_screen(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    start = False
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pygame.mouse.set_visible(False)
                        start = False
            pygame.display.flip()
        all_sprites.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()
            if event.type == pygame.MOUSEMOTION:  # двигаем мышь - двигаем платформу
                player.update(event.pos)
        set_stat(screen)  # выводим на экран счет и хп
        if stat.hp <= 0:
            final = True
        if final:  # финальный экран
            pygame.mouse.set_visible(True)
            set_final_screen(screen)
        if not note_on:  # если на поле нет ноты, создаем ноту
            b = random.choice((0, 1, 2, 3))  # выбираем
            if not b:
                GreenNote()
            elif b == 1:
                YellowNote()
            elif b == 2:
                FirstNote()
            elif b == 3:
                RedNote()
            note_on = True  # теперь на поле есть нота
        if stat.ep:  # если мы что-то сделали с нотой (поймали/не поймали)
            note_on = False  # то на поле больше нет ноты
            stat.ep = False
        all_sprites.update()
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
    sys.exit()
