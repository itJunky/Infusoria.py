#!/usr/bin/python
# -*- coding: utf-8 -*-
# Life_infusoria.py v0.5
# by ITJunky
 
import pygame, math, random, copy, sys
 
pygame.display.set_caption('Life_infusoria')
 
width = 500     # Размеры экрана
height = 500
screen = pygame.display.set_mode((width,height))
BGColor = 50, 40, 30    # Цвет фона
screen.fill(BGColor)
InfColor = [0, 0, 255]  # Цвет инфузории
FoodColor = 0, 255, 0   # Цвет еды
FoodCount = 8  # Количество еды
Foods = [(int(width/2),int(height/2))] # Еда
step = 0 # Ходы(основного цикла)
sex_count = 0 # Количество делений
mutation_count = 0 # Количество мутаций
mutation_range = 40 # Диапазон(сила) мутации
radius = 5
infusoria = [   15,         #m  0 Скорость
                [100,100],  #   1 Положене
                [300,275],  #   2 Цель
                10,         #   3 Индекс цели
                30,         #m  4 Зрение или дальность видимости
                0,          #   5 Имею цель или движусь безцельно
                0,          #   6 Возраст
                0,          #   7 Количество съеденной еды
                InfColor,   #m  8 Цвет
                0,          #   9 Давно ли ел
                400,        #m  10 Время жизни без еды
                0,          #   11 Мутация
                0,          #   12 Количество делений инфузории(каждое 5 поедание еды)
                0,          #   13 Результативность поедания (статический, задается при рождении и записывается детям)
                0           #   14 Родительская результативность
            ]          
                #0,          #   15 Общее количство ходов
# время отдыха(выносливость)
# вес(связан с выносливостью и возрастом)
# возможность делиться на более чем одну особь
dna = [0, 4, 10] # ДНК(номера ячеек которые могут мутировать)
unit = [copy.copy(infusoria), copy.copy(infusoria)]
# Для отладки вручную задаю значения второй инфузории
#unit[1][0] = 8 # Скорость
unit[1][1] = [500,400]
unit[1][2] = [247,275]
#unit[1][4] = 40 # Зрение
unit[1][8] = [255,0,0]
# Умолчальные значения голубой и красной инфузории
uniblue = copy.copy(unit[0])
unired = copy.copy(unit[1])
 
def painting(u):
    '''Стираем объект в текущей позиции'''
    x = u[1][0]
    y = u[1][1]
    pygame.draw.circle(screen, BGColor, [x,y], radius) # затираем инфузорию
    '''Прорисовка объекта в новой позиции'''
    x = move('X', u)
    y = move('Y', u)
    xk = u[2][0]
    yk = u[2][1]
    pygame.draw.circle(screen, u[8], [x,y], radius) # рисуем инфузорию
 
def move(xy,u):
    '''Осуществляет сдвиг экземпляа инфузории''' 
    x = u[1][0]+0.1 # добавляем 0.1 чтобы число отличалось от нуля
    y = u[1][1]+0.1 # поскольку в послдующих подсчётах нельзя делить на нуль
    xk = u[2][0] # координаты цели
    yk = u[2][1]
    Dl = u[0] # Скорость инфузории
    distance = math.sqrt((xk-x)**2+(yk-y)**2)
    x = x+Dl*(xk-x)/distance # Считаем насколько надо сдвинуться по Х 
    y = y+Dl*(yk-y)/distance # По Y
    if xy == 'X': # Если запрашивалась X координата, возвращаем новый X
        u[1][0] = int(x)
        return int(x)
    if xy == 'Y': # Если запрашивалась Y координата, возвращаем новый Y
        u[1][1] = int(y)
        return int(y)
        
def where_food(u):
    '''Поиск ближайшей еды'''
    x = u[1][0]
    y = u[1][1]
    min_distance = 10000
    for i in xrange(len(Foods)): # нахожу ближайшую еду
        xfood = Foods[i][0] # Х координата еды
        yfood = Foods[i][1] # Y координата еды
        distance = math.sqrt((xfood-x)**2+(yfood-y)**2)
        if distance <= min_distance: # Если текущая еда ближе чем предыдущая ближайшая
            min_distance = distance # Заменить прошлую ближайшую текущей
            index = i # заменить индекс ближайшей еды на текущий
        
    # Когда поиск еды закончен
    if min_distance <= u[4]: # И ближайшая еда в области видимости
        u[3] = index # Сохраняю индекс найденной еды
        u[5] = 1 # Цель выбрана
        u[2][0] = Foods[u[3]][0] # Устанавливаю координаты цели
        u[2][1] = Foods[u[3]][1]
    else: # Если еда не видна
        u[5] = 0 # цель отсутствует
    
    if (u[5]==0) and (u[9] >= u[10]/3): # Если проголодался и нет цели
        if (u[6]%20==0): # и ход кратен 20
            u[2] = [random.uniform(0,width),random.uniform(0,height)] # Выбор новой случайной цели
    elif (u[5]==0) and (u[6]%5==0): # Если же нет цели, не голоден и ход кратен 5
        u[2] = [random.uniform(0,width),random.uniform(0,height)] # Выбор новой случайной цели
 
def eating(u):
    '''Поедание еды'''

    x = u[1][0] 
    y = u[1][1]
    xfood = u[2][0]
    yfood = u[2][1]
    distance = math.sqrt((xfood-x)**2+(yfood-y)**2)
    if (distance < radius+u[0]/2) and (u[5] == 1): # Если дистанция меньше радиуса с половиной шага и есть цель 
        '''Если достигли еды, удаляем её'''
        pygame.draw.circle(screen, BGColor, Foods[u[3]], radius) # затираем еду
        del Foods[u[3]] # удаление еды
        u[5] = 0 # Теперь цели нет
        u[9] = 0 # Сбрасываем счётчик давности еды
        u[7] = u[7]+1 # Съел ещё одну еду
 
def sex(u):
    '''Размножение'''
    
    if u[7] == 5: # Когда съели достаточно еды
        u[7] = 0 # Сбрасываем счётчик еды
        u[12] = u[12]+1 # Увеличиваем количество делений
        unit.append(copy.copy(u)) # Клонируем инфузорию
        unit[len(unit)-1][1] = [u[1][0]-radius, u[1][1]-radius] # Координаты новой инфузории смещены
        unit[len(unit)-1][6] = 0 # Время жизни новой инфузории нулевое
        
        '''Мутация на каждое Х деление'''
        global sex_count
        global dna
        global mutation_count
        sex_count = sex_count+1
        if sex_count%2 == 0: # Каждое Х деление вызывает мутацию
            dna_index = dna[random.randint(0, len(dna)-1)] # выбираем какой из генов будет мутировать
            mutation_to = random.randint(-mutation_range, mutation_range) # Вычисляем насколько мутировать
            unit[len(unit)-1][dna_index] = unit[len(unit)-1][dna_index] + mutation_to # Мутируем ген
            clr = copy.copy(unit[len(unit)-1][8])   # Цвет новой инфузории меняется
            clr[1] = clr[1]+50                      # Цвет новой инфузории меняется
            if clr[1] >= 255: clr[1]=0              # Если цвета кончились, обнуляем
            unit[len(unit)-1][8] = clr              # Цвет новой инфузории меняется
            unit[len(unit)-1][12] = 0               # Новая клетка ниразу не делилась
            mutation_count = mutation_count + 1
            print >> sys.stderr, '############### MUTATION ################ count:', mutation_count
            #pygame.time.delay(1000)
 
        print >> sys.stderr, '!!!!!!!!!!!!!!!!!!!!!!CLONING!!!!!!!!!!!!!!!!!!!!!!!!!!', len(unit), 'units', '       sex_count', sex_count
        for i in xrange(len(unit)):
            print >> sys.stderr, i+1, unit[i]
            
def death(u):
    '''Убиваем инфузорию'''
    if u[9] >= u[10]: # Если время без еды меньше лимита
        pygame.draw.circle(screen, (0,0,0), [u[1][0],u[1][1]], radius) # затираем инфузорию
        del unit[unt]
        return 1
    else: return 0
    
def if_all_death():
    '''Если все экземпляры мертвы, добавим нулёвых'''
    red = 0
    blue = 0
    for i in xrange(len(unit)):
        if unit[i][8][0] == 255: red = red+1
        elif unit[i][8][2] == 255: blue = blue+1
        
    if red == 0: unit.append(copy.copy(unired))
    if blue == 0: unit.append(copy.copy(uniblue))
 
while 1:
    '''Основной цикл программы'''
    step = step+1
    print >> sys.stderr, 'Step:', step, '       Mutation count', mutation_count # Всякий дебаг
    for i in xrange(len(unit)):
        print >> sys.stderr, i+1, '--', 'age:', unit[i][6], '   eating:', unit[i][7], '  hunger:', unit[i][9], '   color:', unit[i][8]
    
    for unt in xrange(len(unit)): # Выполняем операции с каждой инфузорией
        unit[unt][6] = unit[unt][6]+1 # Возраст увеличиваем на 1
        unit[unt][9] = unit[unt][9]+1 # Увеличиваем на 1 время с последней кормёжки
        painting(unit[unt]) # Прорисовка
        where_food(unit[unt]) # Поиск еды
        eating(unit[unt]) # Поедание(если достигли какой-то еды)
        sex(unit[unt]) # Размножение
        dt = death(unit[unt]) # Смерть
        if dt == 1: break
        if_all_death() # Если все экземпляры мертвы, добавим нулёвых
        pygame.display.update() # Обновление экрана
    
    if len(Foods) < FoodCount:
        '''Если количество еды уменьшилось, добавить ещё'''
        toapp = [int(random.uniform(0,width)),int(random.uniform(0,height))]
        Foods.append(toapp)
        for i in xrange(len(Foods)):
            '''Прорисовка еды'''
            pygame.draw.circle(screen, FoodColor, Foods[i], radius)
 
 
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        sys.exit()
    
    pygame.time.delay(10)
