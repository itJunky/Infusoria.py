#!/usr/bin/python
# -*- coding: utf-8 -*-
# Life_infusoria.py v0.6
# by ITJunky

import pygame, time
import math
import copy
import random
import sys

debug = 1
# TODO Отловить баг с бегающими трупами. Ловить их по цвету и при измененнии координат повторно удалять или не давать сдвинуться.

pygame.display.set_caption('Life Infusoria')
width = 400  # Размеры экрана
height = 400
screen = pygame.display.set_mode((width, height))
BGColor = 50, 40, 30  # Цвет фона
LocatorColor = 50, 45, 40
screen.fill(BGColor)

clock = pygame.time.Clock()
milli = seconds = 0.0

FoodColor = 0, 255, 0   # Цвет еды
FoodCount = 50         # Количество еды
FoodRadius = 2          # Размер еды
Foods = [(int(width / 2), int(height / 2))]  # Еда

clone_count = 0  # Количество делений
mutation_count = 0  # Количество мутаций
mutation_range = 40  # Диапазон(сила) мутации


class Infusoria:
    dna = ['SPEED', 'VISION', 'LIFE_TIME']  # ДНК(ячейки которые могут мутировать)
    dna[0] = 200
    dna[1] = 20
    dna[2] = 800

    def __init__(self):
        self.radius = 5
        self.InfColor = [0, 0, 255]     # Цвет инфузории
        self.SPEED = self.dna[0]        # m 0 Скорость
        self.POSITION = [100, 100]      #   1 Положене
        self.TARGET = [300, 275]        #   2 Цель
        self.TRG_INDX = 10              #   3 Индекс цели
        self.VISION = self.dna[1]       # m 4 Зрение или дальность видимости
        self.TRG_EXIST = 0              #   5 Имею цель или движусь безцельно
        self.AGE = 0                    #   6 Возраст
        self.EAT_COUNT = 0              #   7 Количество съеденной еды
        self.COLOR = self.InfColor      # m 8 Цвет
        self.HUNGRY = 0                 #   9 Давно ли ел
        self.LIFE_TIME = self.dna[2]    # m 10 Время жизни без еды
        self.MUTATION = 0               #   11 Мутация
        self.COUNT_SEGMENT = 0          ##  12 Количество делений инфузории(каждое 5 поедание еды)
        self.EAT_PRODUCTIVITY = 0       ##  13 Результативность поедания (статический, задается при рождении и записывается детям)
        self.PARENT_PRODUCTIVITY = 0    ##  14 Родительская результативность
        # 0,          #   15 Общее количство ходов
        #           время отдыха(выносливость)
        #           вес(связан с выносливостью и возрастом)
        #           Возможность делиться более чем на две особи
        self.IDX = int(0)

    def __repr__(self):
        return "ID: {} XY: {}".format(self.IDX, self.get_position())

    def get_position(self):
        return self.POSITION[0], self.POSITION[1]


    def clean(self):
        '''
        Стираем объект в текущей позиции
        '''
        # pygame.draw.circle(screen, BGColor, [self.POSITION[0], self.POSITION[1]], self.VISION)  # затираем инфузорию
        pygame.draw.circle(screen, BGColor, [self.POSITION[0], self.POSITION[1]], self.radius)  # затираем инфузорию


    def paint(self, backward=False):
        '''
        Прорисовка объекта в новой позиции
        '''
        if backward == False:
            self.move()
        else:
            self.move(backward=True)

        pygame.draw.circle(screen, LocatorColor, [self.POSITION[0], self.POSITION[1]], self.VISION)
        pygame.draw.circle(screen, self.COLOR, [self.POSITION[0], self.POSITION[1]], self.radius)  # рисуем инфузорию


    def move(self, backward=False):
        '''
        Осуществляет сдвиг экземпляра инфузории
        '''
        x = self.POSITION[0]
        y = self.POSITION[1]
        xk = self.TARGET[0]  # координаты цели
        yk = self.TARGET[1]
        Dl = self.get_inf_speed()
        distance = math.sqrt((xk-x)**2+(yk-y)**2)
        if distance > 0. and backward == False:
            x = x+Dl*(xk-x)/distance  # Считаем насколько надо сдвинуться по Х
            y = y+Dl*(yk-y)/distance  # По Y
        elif distance > 0. and backward == True:
            x = x-Dl*(xk-x)/distance  # Откатываемся назад
            y = y-Dl*(yk-y)/distance  # В случае коллизии

        self.POSITION[0] = int(x)
        self.POSITION[1] = int(y)


    def get_inf_speed(self):
        milli = clock.tick(1000)
        seconds = milli / 100.0
        Dl = self.SPEED * seconds  # Скорость инфузории
        return Dl


    def eating(self):
        '''
        Поедание еды инфузорией
        '''
        x = self.POSITION[0]    # Текущая позиция инфузории
        y = self.POSITION[1]
        xfood = self.TARGET[0]  # Позиция выбранной еды
        yfood = self.TARGET[1]
        distance = math.sqrt((xfood-x)**2+(yfood-y)**2)     # Считаем дистанцию до еды
        # Если дистанция меньше радиуса с половиной шага и есть цель
        if (distance < self.radius+self.get_inf_speed()) and (self.TRG_EXIST == 1):
            '''Если достигли еды, удаляем её'''
            try:
                pygame.draw.circle(screen, BGColor, Foods[self.TRG_INDX], FoodRadius)  # затираем еду
                del Foods[self.TRG_INDX]  # удаление еды
            except IndexError:
                pass
            self.TRG_EXIST = 0  # Теперь цели нет
            self.HUNGRY = 0  # Сбрасываем счётчик давности еды
            self.EAT_COUNT += 1  # Съел ещё одну еду


    def set_target(self):
        '''Поиск ближайшей еды'''
        ## NEED OPTIMIZE ###

        if not self.TRG_EXIST:
            x = self.POSITION[0]
            y = self.POSITION[1]
            min_distance = 200000000000

            # нахожу ближайшую еду
            for i in xrange(len(Foods)): # для каждой еды
                xfood = Foods[i][0]  # Х координата еды
                yfood = Foods[i][1]  # Y координата еды
                distance = math.sqrt((xfood-x)**2+(yfood-y)**2)
                if distance <= min_distance:  # Если текущая еда ближе чем предыдущая ближайшая
                    min_distance = distance  # Заменить прошлую ближайшую текущей
                    index = i  # заменить индекс ближайшей еды на текущий
                    #TODO Внести задержку что бы избежать прыганья на месте
                    print('\033[92mUnit: \033[94m{} \033[0m bread: \033[97m{} \t \033[0m Distance {} \t Target {} \033[0m'.format(
                            self.IDX,
                            (xfood, yfood),
                            distance,
                            self.TARGET
                        )
                    )
                else:
                    index = 0

            # Берём квадрат рвсстояния до ближайшей видимой еды
            min_distance = math.sqrt(min_distance)

            # Когда поиск еды закончен
            if min_distance <= self.VISION:  # И ближайшая еда в области видимости
                self.TRG_INDX = index  # Сохраняю индекс найденной еды
                self.TRG_EXIST = 1  # Цель выбрана
                self.TARGET[0] = Foods[self.TRG_INDX][0]  # Устанавливаю координаты цели
                self.TARGET[1] = Foods[self.TRG_INDX][1]
                print("{} - SET target for {} to {} -- D: {}".format(self.IDX, self.AGE, self.TARGET, min_distance))
            else:  # Если еда не видна
                self.TRG_EXIST = 0  # цель отсутствует

            if self.HUNGRY >= self.LIFE_TIME/3:  # Если нет цели и проголодался
                # if self.AGE % self.radius == 0:  # и ход кратен 20
                self.TARGET = [random.uniform(0, width), random.uniform(0, height)]  # Выбор новой случайной цели
                self.TRG_EXIST = 0
                print("\033[91m {} - Set RANDOM target for {} to {} \033[0m".format(self.IDX, self.AGE, self.TARGET))

            elif self.AGE % 50 == 0:  # Если же нет цели, не голоден и ход кратен 50
                self.TARGET = [random.uniform(0, width), random.uniform(0, height)]  # Выбор новой случайной цели
                self.TRG_EXIST = 0
                print("\033[91m {} - Set FREE RANDOM target for {} to {} \033[0m".format(self.IDX, self.AGE, self.TARGET))


    def clone(self):
        '''Размножение'''
        # TODO fix новая инфузория появляется в дефолтных координатах, а не рядом со своим клоном
        if self.EAT_COUNT == 5:  # Когда съели достаточно еды
            self.EAT_COUNT = 0   # Сбрасываем счётчик еды
            self.COUNT_SEGMENT += 1  # Увеличиваем количество делений

            # Подготавливаем новую инфузорию к клонированию
            new_inf = Infusoria()
            new_inf.COLOR = self.COLOR
            # Координаты новой инфузории смещены
            print(self.POSITION)
            new_inf.POSITION = [self.POSITION[0]-self.radius, self.POSITION[1]-self.radius]
            print(new_inf.POSITION)
            new_inf.AGE = 0  # Время жизни новой инфузории нулевое

            # поиск максмимального индекса
            tmp_idx = int(0)
            for u in unit:
                if u.IDX > tmp_idx:
                    tmp_idx = u.IDX

            # Увеличим индекс новой(текущей) инфузории на единицу
            new_inf.IDX = tmp_idx + 1
            # Клонируем инфузорию
            unit.append(new_inf)

            '''Мутация на каждое Х деление'''
            global clone_count
            global dna
            global mutation_count
            clone_count += 1
            if clone_count % 10 == 0:  # Каждое Х деление вызывает мутацию
                dna_index = random.randint(0, len(self.dna)-1)  # выбираем какой из генов будет мутировать
                mutation_to = random.randint(-mutation_range, mutation_range)  # Вычисляем насколько мутировать
                self.dna[dna_index] = self.dna[dna_index] + mutation_to  # Мутируем ген
                # TODO fix вся популяция меняет цвет на чёрный после 12-ого клона
                #clr = copy.copy(self.COLOR)        # Цвет новой инфузории меняется
                clr = self.COLOR[0]                 # Цвет новой инфузории меняется
                clr = clr+50                        # Цвет новой инфузории меняется
                if clr >= 255: clr = 0              # Если цвета кончились, обнуляем
                self.COLOR[0] = clr                 # Цвет новой инфузории меняется
                self.COUNT_SEGMENT = 0              # Новая клетка ниразу не делилась
                mutation_count = mutation_count + 1

                if debug:
                    print >> sys.stderr, '############### MUTATION ################ count:', mutation_count

            if debug:
                print >> sys.stderr, '!!!!!!!!!!!!!!!!!!!!!!CLONING!!!!!!!!!!!!!!!!!!!!!!!!!!', len(unit), 'units', '       sex_count', clone_count
                for u in unit:
                    print >> sys.stderr, unit.index(u), 'age:', u.AGE, '\teating:', u.EAT_COUNT, \
                        '\thunger:', u.HUNGRY, '\tvision:', u.VISION,  '\tcolor:', u.COLOR
                time.sleep(4)


    def death(self):
        '''Убиваем инфузорию'''
        if self.HUNGRY >= self.LIFE_TIME:  # Если время без еды меньше лимита
            # затираем инфузорию
            pygame.draw.circle(screen, (0, 0, 0), [self.POSITION[0], self.POSITION[1]], self.radius)
            try:
                idx = unit.index(self)
                del(unit[idx])
            except:
                print([self.POSITION[0], self.POSITION[1]])
                print('Trying to remove {}'.format(unt.IDX))
                print(self.InfColor)
                from IPython import embed
                embed()
                sys.exit()

            return 1
        else:
            return 0


def clean_all_visions():
    for u in unit:
        pygame.draw.circle(screen, BGColor, [u.POSITION[0], u.POSITION[1]], u.VISION+2)  # затираем инфузорию


def paint_all_visions():
    '''
    Рисовать области видимости инфузорий
    '''
    for u in unit:
        pygame.draw.circle(screen, LocatorColor, [u.POSITION[0], u.POSITION[1]], u.VISION)


def food():
    '''
    Прорисовка еды
    '''
    global first_run
    if len(Foods) < FoodCount:
        # Если количество еды уменьшилось, добавить ещё
        toapp = [int(random.uniform(0, width)), int(random.uniform(0, height))]
        Foods.append(toapp)

    for i in xrange(len(Foods)):
        # Прорисовка еды
        pygame.draw.circle(screen, FoodColor, Foods[i], FoodRadius)


def collision(u):
    unchecked = []
    for unt in unit: # Заполняем массив для проверки
        if u.POSITION[0] == unt.POSITION[0] and u.POSITION[1] == unt.POSITION[1]:
            pass
        else: # Иключаем из списка выбранный экземпляр
            unchecked.append(unt)

    x = u.POSITION[0]    # Текущая позиция инфузории
    y = u.POSITION[1]
    while unchecked:  # not epmty
        check_with = unchecked.pop()
        xt = check_with.POSITION[0]
        yt = check_with.POSITION[1]
        distance = math.sqrt((xt-x)**2+(yt-y)**2)
        rad2 = u.radius*2
        if distance < rad2:
            if xt > x:
                u.painting(backward=True)
            else:
                u.painting()


def debug_out(u):
    print('\033[91mUnit: \033[94m{} \033[0m TRGT: {} XY: \033[93m {} \033[96m {} \033[0m'.format(
            u.IDX,
            u.TRG_EXIST,
            u.get_position(),
            u.TARGET
        )
    )

    if u.POSITION[0] > width or u.POSITION[1] > height or \
       u.POSITION[0] < 0     or u.POSITION[1] < 0:
        print('Wrong unit. Removing')
        print('U {} XY {}'.format(u.IDX, u.get_position()))
        # del(unit[unit.index(u)])
        u.POSITION = [100, 100]
        print(u.get_position())
        # time.sleep(3)


def population_limit(population):
    if len(population) > 20:
        # Убиваем самых старых
        oldest = 0
        idx = 0
        for e in population:
            if e.AGE > oldest:
                oldest = e.AGE
                idx = population.index(e)

        print('Removing oldest {} with age {}'.format(idx, oldest))
        # затираем инфузорию
        pygame.draw.circle(screen, (0, 0, 0), [population[idx].POSITION[0], population[idx].POSITION[1]], population[idx].radius)
        del(population[idx])
        # time.sleep(2)


def init_world():
    # # Для отладки, вручную задаю значения второй инфузории
    infusoria = Infusoria()
    infusoria2 = Infusoria()

    infusoria.IDX = 1
    infusoria.POSITION = [100, 340]

    infusoria2.IDX = 2
    infusoria2.SPEED = 210  # Скорость
    infusoria2.POSITION = [200, 220]
    infusoria2.TARGET = [247, 275]
    infusoria2.COLOR = [255, 0, 0]

    print(infusoria)
    print(infusoria2)
    # unit = [infusoria, copy.deepcopy(infusoria)]
    unit.append(infusoria)
    unit.append(infusoria2)


unit = []
init_world()

step = 0  # Ходы(основного цикла)
mainLoop = True
while mainLoop:
    '''
    Основной цикл программы
    '''
    step = step + 1
    milli = clock.tick(20)

    clean_all_visions()


    # Clear debug screen
    # time.sleep(2)
    print(chr(27) + "[2J")
    print('Step: {}  units: {}'.format(step, len(unit)))

    population_limit(unit)

    # Подсчёт изменений по каждой инфузории
    for unt in unit:  # Выполняем операции с каждой инфузорией
        unt.AGE += 1      # Возраст увеличиваем на 1
        unt.HUNGRY += 1   # Увеличиваем на 1 время с последней кормёжки
        unt.clean()
        unt.move()
        # unt.paint()
        unt.eating()
        unt.set_target()
        unt.clone()
        # collision(unt)
        dt = unt.death()
        if dt == 1: break

        # Debug
        debug_out(unt)

    # Прорисовка новых координат
    paint_all_visions()
    food()

    for unt in unit:
        unt.paint()



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                mainLoop = False
            elif event.key == pygame.K_SPACE:
                unpause = True
                while unpause:
                    for event in pygame.event.get():
                        time.sleep(3)
                        #pygame.time.delay(100)
                        if event.key == pygame.K_SPACE:
                            unpause = False

    pygame.time.delay(1)
    pygame.display.update()  # Обновление экрана

pygame.quit()
