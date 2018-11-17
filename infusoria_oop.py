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
width = 1000  # Размеры экрана
height = 800
screen = pygame.display.set_mode((width, height))
BGColor = 50, 40, 30  # Цвет фона
screen.fill(BGColor)

clock = pygame.time.Clock()
milli = seconds = 0.0

FoodColor = 0, 255, 0   # Цвет еды
FoodCount = 200         # Количество еды
FoodRadius = 2          # Размер еды
Foods = [(int(width / 2), int(height / 2))]  # Еда

clone_count = 0  # Количество делений
mutation_count = 0  # Количество мутаций
mutation_range = 40  # Диапазон(сила) мутации


class Infusoria:
    def __init__(self):
        pass

    InfColor = [0, 0, 255]  # Цвет инфузории
    radius = 5

    dna = ['SPEED', 'VISION', 'LIFE_TIME']  # ДНК(ячейки которые могут мутировать)
    dna[0] = 200
    dna[1] = 10
    dna[2] = 300

    SPEED = dna[0]          # m 0 Скорость
    POSITION = [100, 100]   #   1 Положене
    TARGET = [300, 275]     #   2 Цель
    TRG_INDX = 10           #   3 Индекс цели
    VISION = dna[1]         # m 4 Зрение или дальность видимости
    TRG_EXIST = 0           #   5 Имею цель или движусь безцельно
    AGE = 0                 #   6 Возраст
    EAT_COUNT = 0           #   7 Количество съеденной еды
    COLOR = InfColor        # m 8 Цвет
    HUNGRY = 0              #   9 Давно ли ел
    LIFE_TIME = dna[2]      # m 10 Время жизни без еды
    MUTATION = 0            #   11 Мутация
    COUNT_SEGMENT = 0       ##  12 Количество делений инфузории(каждое 5 поедание еды)
    EAT_PRODUCTIVITY = 0    ##  13 Результативность поедания (статический, задается при рождении и записывается детям)
    PARENT_PRODUCTIVITY = 0 ##  14 Родительская результативность
    # 0,          #   15 Общее количство ходов
    #           время отдыха(выносливость)
    #           вес(связан с выносливостью и возрастом)
    #           Возможность делиться более чем на две особи



    def painting(self, backward=False):
        '''Стираем объект в текущей позиции'''
        pygame.draw.circle(screen, BGColor, [self.POSITION[0], self.POSITION[1]], self.radius)  # затираем инфузорию
        '''Прорисовка объекта в новой позиции'''
        if backward == False:
            self.move()
        else:
            self.move(backward=True)
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
        #print milli
        #global milli
        seconds = milli / 250.0
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
        x = self.POSITION[0]
        y = self.POSITION[1]
        min_distance = 1000000000

        for i in xrange(len(Foods)):  # нахожу ближайшую еду
            xfood = Foods[i][0]  # Х координата еды
            yfood = Foods[i][1]  # Y координата еды
            distance = math.sqrt((xfood-x)**2+(yfood-y)**2)
            if distance <= min_distance:  # Если текущая еда ближе чем предыдущая ближайшая
                min_distance = distance  # Заменить прошлую ближайшую текущей
                index = i  # заменить индекс ближайшей еды на текущий

        min_distance = math.sqrt(min_distance)

        # Когда поиск еды закончен
        if min_distance <= self.VISION:  # И ближайшая еда в области видимости
            self.TRG_INDX = index  # Сохраняю индекс найденной еды
            self.TRG_EXIST = 1  # Цель выбрана
            self.TARGET[0] = Foods[self.TRG_INDX][0]  # Устанавливаю координаты цели
            self.TARGET[1] = Foods[self.TRG_INDX][1]
        else:  # Если еда не видна
            self.TRG_EXIST = 0  # цель отсутствует

        if (self.TRG_EXIST == 0) and (self.HUNGRY >= self.LIFE_TIME/2):  # Если нет цели и проголодался
            if self.AGE % self.radius == 0:  # и ход кратен 20
               self.TARGET = [random.uniform(0, width), random.uniform(0, height)]  # Выбор новой случайной цели
        elif (self.TRG_EXIST == 0) and (self.AGE % 50 == 0):  # Если же нет цели, не голоден и ход кратен 5
            self.TARGET = [random.uniform(0, width), random.uniform(0, height)]  # Выбор новой случайной цели


    def clone(self):
        '''Размножение'''
        if self.EAT_COUNT == 5:  # Когда съели достаточно еды
            self.EAT_COUNT = 0  # Сбрасываем счётчик еды
            self.COUNT_SEGMENT += 1  # Увеличиваем количество делений
            unit.append(copy.deepcopy(self))  # Клонируем инфузорию
            # Координаты новой инфузории смещены
            unit[len(unit)-1].POSITION = [self.POSITION[0]-self.radius, self.POSITION[1]-self.radius]
            unit[len(unit)-1].AGE = 0  # Время жизни новой инфузории нулевое

            '''Мутация на каждое Х деление'''
            global clone_count
            global dna
            global mutation_count
            clone_count += 1
            if clone_count % 10 == 0:  # Каждое Х деление вызывает мутацию
                dna_index = random.randint(0, len(self.dna)-1)  # выбираем какой из генов будет мутировать
                mutation_to = random.randint(-mutation_range, mutation_range)  # Вычисляем насколько мутировать
                self.dna[dna_index] = self.dna[dna_index] + mutation_to  # Мутируем ген
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
                for i in xrange(len(unit)):
                    print >> sys.stderr, i+1, '--', id(unit[i]), 'age:', unit[i].AGE, '   eating:', unit[i].EAT_COUNT, '  hunger:', unit[i].HUNGRY, '   color:', unit[i].COLOR


    def death(self):
        '''Убиваем инфузорию'''
        if self.HUNGRY >= self.LIFE_TIME:  # Если время без еды меньше лимита
            # затираем инфузорию
            pygame.draw.circle(screen, (0, 0, 0), [self.POSITION[0], self.POSITION[1]], self.radius)
            try:
                unit.pop(unt)
            except:
                print([self.POSITION[0], self.POSITION[1]])
                print(unt)
                print(unit[unt])
                from IPython import embed
                embed()
                sys.exit()

            return 1
        else:
            return 0

infusoria = Infusoria()
unit = [infusoria, copy.deepcopy(infusoria)]
# Для отладки, вручную задаю значения второй инфузории
unit[1].SPEED = 210  # Скорость
unit[1].POSITION = [400, 400]
unit[1].TARGET = [247, 275]
unit[1].COLOR = [255, 0, 0]

def food():
    global first_run
    if len(Foods) < FoodCount:
        '''Если количество еды уменьшилось, добавить ещё'''
        toapp = [int(random.uniform(0, width)), int(random.uniform(0, height))]
        Foods.append(toapp)
        for i in xrange(len(Foods)):
            '''Прорисовка еды'''
            pygame.draw.circle(screen, FoodColor, Foods[i], FoodRadius)

def collision(u):
    unchecked = []
    for unt in xrange(len(unit)): # Заполняем массив для проверки
        if u.POSITION[0] == unit[unt].POSITION[0] and u.POSITION[1] == unit[unt].POSITION[1]:
            pass
        else: # Иключаем из списка выбранный экземпляр
            unchecked.append(unit[unt])

    x = u.POSITION[0]    # Текущая позиция инфузории
    y = u.POSITION[1]
    while unchecked: # not epmty
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

step = 0  # Ходы(основного цикла)
mainLoop = True
while mainLoop:
    '''
    Основной цикл программы
    '''
    step = step + 1
    milli = clock.tick(20)

    food()

    for unt in xrange(len(unit)):  # Выполняем операции с каждой инфузорией
        unit[unt].AGE += 1      # Возраст увеличиваем на 1
        unit[unt].HUNGRY += 1   # Увеличиваем на 1 время с последней кормёжки
        unit[unt].painting()
        unit[unt].eating()
        unit[unt].set_target()
        unit[unt].clone()
        collision(unit[unt])
        dt = unit[unt].death()
        if dt == 1: break


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
                        time.sleep(100)
                        #pygame.time.delay(100)
                        if event.key == pygame.K_SPACE:
                            unpause = False

    pygame.time.delay(1)
    pygame.display.update()  # Обновление экрана

pygame.quit()
