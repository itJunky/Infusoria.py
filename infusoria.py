#!/usr/bin/python
# -*- coding: utf-8 -*-
# Life_infusoria.py v0.5
# by ITJunky
 
import pygame
import math
import random
import copy
import sys
 
pygame.display.set_caption('Life Infusoria')
 
width = 1000             # Размеры экрана
height = 1000
screen = pygame.display.set_mode((width, height))
BGColor = [50, 40, 30]    # Цвет фона

clock = pygame.time.Clock()
milli = seconds = 0.0
screen.fill(BGColor)
debug = 1

InfColor = [0, 0, 255]  # Цвет инфузории
FoodColor = 0, 255, 0   # Цвет еды
FoodCount = 200          # Количество еды
Foods = [(int(width/2),int(height/2))] # Еда
step = 0                # Ходы(основного цикла)
sex_count = 0           # Количество делений
mutation_count = 0      # Количество мутаций
mutation_range = 40     # Диапазон(сила) мутации
radius = 2

infusoria = {   'SPEED':               100,  #m  0 Скорость
                'POSITION':     [100, 100],  #   1 Положене
                'TARGET':       [300, 275],  #   2 Цель
                'TRG_INDX':             10,  #   3 Индекс цели
                'VISION':               30,  #m  4 Зрение или дальность видимости
                'TRG_EXIST':             0,  #   5 Имею цель или движусь безцельно
                'AGE':                   0,  #   6 Возраст
                'EAT_COUNT':             0,  #   7 Количество съеденной еды
                'COLOR':          InfColor,  #m  8 Цвет
                'HUNGRY':                0,  #   9 Давно ли ел
                'LIFE_TIME':           400,  #m  10 Время жизни без еды
                'MUTATION':              0,  #   11 Мутация
                'COUNT_SEGMENT':         0,  ##  12 Количество делений инфузории(каждое 5 поедание еды)
                'EAT_PRODUCTIVITY':      0,  ##  13 Результативность поедания (статический, задается при рождении и записывается детям)
                'PARENT_PRODUCTIVITY':   0,   ##  14 Родительская результативность
                'FREEZE':               0,  # Время задержки после деления
            }          
                #0,          #   15 Общее количство ходов
                #           время отдыха(выносливость)
                #           вес(связан с выносливостью и возрастом)
                #           Возможность делиться более чем на две особи

dna = ['SPEED', 'VISION', 'LIFE_TIME']  # ДНК(номера ячеек которые могут мутировать)
unit = [copy.copy(infusoria), copy.copy(infusoria)]
# Для отладки, вручную задаю значения второй инфузории
unit[1][0] = 10  # Скорость
unit[1]['POSITION'] = [500, 400]
unit[1]['TARGET'] = [247, 275]
#unit[1][4] = 40  # Зрение
unit[1]['COLOR'] = [255, 0, 0]
# Умолчальные значения голубой и красной инфузории
uniblue = copy.copy(unit[0])
unired = copy.copy(unit[1])

def painting(u):
    '''Стираем объект в текущей позиции'''
    x = u['POSITION'][0]
    y = u['POSITION'][1]
    pygame.draw.circle(screen, BGColor, [x, y], radius)  # затираем инфузорию
    '''Прорисовка объекта в новой позиции'''
    x = move('X', u)
    y = move('Y', u)
    #xk = u['TARGET'][0]
    #yk = u['TARGET'][1]
    # print('R {}'.format(radius))
    # print(type(radius))
    print('BGCLR: {}'.format(BGColor))
    print(type(BGColor))
    infusoria_color = u['COLOR'][0], u['COLOR'][1], u['COLOR'][2]
    print(infusoria_color )
    print(type(infusoria_color))
    pygame.draw.circle(screen, infusoria_color, [x, y], radius ) # рисуем инфузорию

def get_inf_speed(u):
    #milli = clock.tick(100)
    global milli
    seconds = milli / 1000.0
    Dl = u['SPEED'] * seconds # Скорость инфузории
    return Dl


# noinspection PyAugmentAssignment
def move(xy, u):
    '''Осуществляет сдвиг экземпляра инфузории'''
    # Не перемещаться, после деления
    if u['FREEZE'] > 10:

        x = u['POSITION'][0]
        y = u['POSITION'][1]
        xk = u['TARGET'][0]  # координаты цели
        yk = u['TARGET'][1]
        Dl = get_inf_speed(u)
        distance = math.sqrt((xk-x)**2+(yk-y)**2)
        if distance > 0.:
            x = x+Dl*(xk-x)/distance # Считаем насколько надо сдвинуться по Х
            y = y+Dl*(yk-y)/distance # По Y
        if xy == 'X': # Если запрашивалась X координата, возвращаем новый X
            u['POSITION'][0] = int(x)
            return int(x)
        if xy == 'Y': # Если запрашивалась Y координата, возвращаем новый Y
            u['POSITION'][1] = int(y)
            return int(y)

def where_food(u):
    '''Поиск ближайшей еды'''
    ## NEED OPTIMIZE ###
    x = u['POSITION'][0]
    y = u['POSITION'][1]
    min_distance = 1000000000
    global radius
    for i in xrange(len(Foods)):  # нахожу ближайшую еду
        xfood = Foods[i][0]  # Х координата еды
        yfood = Foods[i][1]  # Y координата еды
        distance = math.sqrt((xfood-x)**2+(yfood-y)**2)
        if distance <= min_distance:  # Если текущая еда ближе чем предыдущая ближайшая
            min_distance = distance  # Заменить прошлую ближайшую текущей
            index = i  # заменить индекс ближайшей еды на текущий

    min_distance = math.sqrt(min_distance)

    # Когда поиск еды закончен
    if min_distance <= u['VISION']:  # И ближайшая еда в области видимости
        u['TRG_INDX'] = index  # Сохраняю индекс найденной еды
        u['TRG_EXIST'] = 1  # Цель выбрана
        u['TARGET'][0] = Foods[u['TRG_INDX']][0]  # Устанавливаю координаты цели
        u['TARGET'][1] = Foods[u['TRG_INDX']][1]
    else:  # Если еда не видна
        u['TRG_EXIST'] = 0  # цель отсутствует
    
    if (u['TRG_EXIST'] == 0) and (u['HUNGRY'] >= u['LIFE_TIME']/3): # Если нет цели и проголодался
        if (u['AGE']%radius==0): # и ход кратен 20
            u['TARGET'] = [random.uniform(0,width),random.uniform(0,height)] # Выбор новой случайной цели
    elif (u['TRG_EXIST']==0) and (u['AGE']%radius==0): # Если же нет цели, не голоден и ход кратен 5
        u['TARGET'] = [random.uniform(0,width),random.uniform(0,height)] # Выбор новой случайной цели

def food():
    global first_run
    if len(Foods) < FoodCount:
        '''Если количество еды уменьшилось, добавить ещё'''
        toapp = [int(random.uniform(0,width)),int(random.uniform(0,height))]
        Foods.append(toapp)
        for i in xrange(len(Foods)):
            '''Прорисовка еды'''
            pygame.draw.circle(screen, FoodColor, Foods[i], radius)
    else:
        first_run = False
        return first_run

def eating(u):
    '''Поедание еды'''

    x = u['POSITION'][0]        # Текущая позиция инфузории
    y = u['POSITION'][1]
    xfood = u['TARGET'][0]      # Позиция выбранной еды
    yfood = u['TARGET'][1]
    distance = math.sqrt((xfood-x)**2+(yfood-y)**2)     # Считаем дистанцию до еды
    if (distance < radius+(get_inf_speed(u)/10)) and (u['TRG_EXIST'] == 1): # Если дистанция меньше радиуса с половиной шага и есть цель 
        '''Если достигли еды, удаляем её'''
        pygame.draw.circle(screen, BGColor, Foods[u['TRG_INDX']], radius) # затираем еду
        del Foods[u['TRG_INDX']] # удаление еды
        u['TRG_EXIST'] = 0 # Теперь цели нет
        u['HUNGRY'] = 0 # Сбрасываем счётчик давности еды
        u['EAT_COUNT'] = u['EAT_COUNT']+1 # Съел ещё одну еду

def sex(u):
    '''Размножение'''
    
    if u['EAT_COUNT'] == 5: # Когда съели достаточно еды
        u['EAT_COUNT'] = 0 # Сбрасываем счётчик еды
        u['COUNT_SEGMENT'] = u['COUNT_SEGMENT']+1 # Увеличиваем количество делений
        unit.append(copy.copy(u)) # Клонируем инфузорию
        unit[len(unit)-1]['POSITION'] = [u['POSITION'][0]-radius, u['POSITION'][1]-radius] # Координаты новой инфузории смещены
        unit[len(unit)-1]['AGE'] = 0 # Время жизни новой инфузории нулевое
        
        '''Мутация на каждое Х деление'''
        global sex_count
        global dna
        global mutation_count
        sex_count = sex_count+1
        if sex_count%20 == 0: # Каждое Х деление вызывает мутацию
            dna_index = dna[random.randint(0, len(dna)-1)] # выбираем какой из генов будет мутировать
            mutation_to = random.randint(-mutation_range, mutation_range) # Вычисляем насколько мутировать
            unit[len(unit)-1][dna_index] = unit[len(unit)-1][dna_index] + mutation_to # Мутируем ген
            clr = copy.copy(unit[len(unit)-1]['COLOR'])   # Цвет новой инфузории меняется
            clr[1] = clr[1]+50                      # Цвет новой инфузории меняется
            if clr[1] >= 255: clr[1]=0              # Если цвета кончились, обнуляем
            unit[len(unit)-1]['COLOR'] = clr        # Цвет новой инфузории меняется
            unit[len(unit)-1]['COUNT_SEGMENT'] = 0  # Новая клетка ниразу не делилась
            mutation_count = mutation_count + 1
            #pygame.time.delay(1000)
            if debug:
                print >> sys.stderr, '############### MUTATION ################ count:', mutation_count

 	if debug:
            print >> sys.stderr, '!!!!!!!!!!!!!!!!!!!!!!CLONING!!!!!!!!!!!!!!!!!!!!!!!!!!', len(unit), 'units', '       sex_count', sex_count
            for i in xrange(len(unit)):
                print >> sys.stderr, i+1, '--', 'age:', unit[i]['AGE'], '   eating:', unit[i]['EAT_COUNT'], '  hunger:', unit[i]['HUNGRY'], '   color:', unit[i]['COLOR']

def death(u):
    '''Убиваем инфузорию'''
    if u['HUNGRY'] >= u['LIFE_TIME']: # Если время без еды меньше лимита
        pygame.draw.circle(screen, (0,0,0), [u['POSITION'][0],u['POSITION'][1]], radius) # затираем инфузорию
        del unit[unt]
        return 1
    else: return 0

def if_all_death():
    '''Если все экземпляры мертвы, добавим нулёвых'''
    red = 0
    blue = 0
    for i in unit:
        if i['COLOR'][0] == 255: red = red+1
        elif i['COLOR'][2] == 255: blue = blue+1

    if red == 0: unit.append(copy.copy(unired))
    if blue == 0: unit.append(copy.copy(uniblue))

def units_count():
    red = 0
    blue = 0
    for i in xrange(len(unit)):
        if unit[i]['COLOR'][0] == 255: red = red+1
        elif unit[i]['COLOR'][2] == 255: blue = blue+1
    return red, blue
 
first_run = True  # Необходимо для первоначальной отрисовки еды
mainLoop = True

while mainLoop :
    '''Основной цикл программы'''
    step = step+1
    milli = clock.tick(20)

    if_all_death() # Если все экземпляры мертвы, добавим нулёвых
    pygame.display.update() # Обновление экрана

    UC = units_count()
    if debug:
        print >> sys.stderr, 'Step:', step, '       Mutation count', mutation_count, '        Red units:', UC[0], 'Blue units:', UC[1] # Всякий дебаг 
        for i in xrange(len(unit)):
            print >> sys.stderr, i+1, '--', 'age:', unit[i]['AGE'], '   eating:', unit[i]['EAT_COUNT'], '  hunger:', unit[i]['HUNGRY'], '   color:', unit[i]['COLOR'], '    xy:', unit[i]['POSITION']
    
    for unt in xrange(len(unit)): # Выполняем операции с каждой инфузорией
        unit[unt]['AGE'] = unit[unt]['AGE']+1 # Возраст увеличиваем на 1
        unit[unt]['HUNGRY'] = unit[unt]['HUNGRY']+1 # Увеличиваем на 1 время с последней кормёжки
        unit[unt]['FREEZE'] = unit[unt]['FREEZE'] + 1  # Увеличиваем на 1 время с последней кормёжки
        painting(unit[unt]) # Прорисовка
        where_food(unit[unt]) # Поиск едыa
        eating(unit[unt]) # Поедание(если достигли какой-то еды)
        sex(unit[unt]) # Размножение
        dt = death(unit[unt]) # Смерть
        if dt == 1: break
    
    #while first_run :
        food()
        #if debug:
        #    print >> sys.stderr, first_run, len(Foods)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                mainLoop = False
    
    pygame.time.delay(2000)

pygame.quit()
