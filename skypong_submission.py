# U of T AI Pong Tournament 2015 Entry
#
# Team Skypong
# Tirth Patel
# Monica Shver

import math
import numpy

# dictionary representation of game state
history = dict(paddle_y=[], ball_x=[], ball_y=[], y_dist=[], x_dist=[],
               d_dist=[], o_d_dist=[], x_vels=[], y_vels=[])

score = [1, [0, 0], [0, 0]]  # [round, round_one, round_two]
goto = -1

collision, scored, calculated = False, False, False


def trim_history(hist, trim_size=50):
    """Cut down history dict to specified trim_size.

    :param hist: history dict containing all moves in a given turn
    :param trim_size: size to cut dict down to
    """
    global history

    if trim_size == 0:
        history = dict(paddle_y=[], ball_x=[], ball_y=[], y_dist=[], x_dist=[],
                       d_dist=[], o_d_dist=[], x_vels=[], y_vels=[])

    if len(hist[hist.keys()[0]]) > trim_size:  # only check one for efficiency
        for key in hist.keys():
            while len(hist[key]) > trim_size:
                hist[key].pop(0)


def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    """Return "up" or "down", depending on which way the paddle should go.

    :rtype : str
    :param paddle_frect: a rectangle representing the coordinates of the paddle
                  paddle_frect.pos[0], paddle_frect.pos[1] is the top-left
                  corner of the rectangle.
                  paddle_frect.size[0], paddle_frect.size[1] are the dimensions
                  of the paddle along the x and y axis, respectively
                  
    :param other_paddle_frect: a rectangle representing the opponent paddle. 
                It is formatted in the same way as paddle_frect
                
    :param ball_frect: a rectangle representing the ball. It is formatted in 
                the same way as paddle_frect
                  
    :param table_size: table_size[0], table_size[1] are the dimensions of 
                the table, along the x and the y axis respectively
    """

    global collision, scored, goto, calculated

    # friendlier names, variables
    pad_x_coord, pad_y_coord = paddle_frect.pos[0], paddle_frect.pos[1]
    pad_x_size, pad_y_size = paddle_frect.size[0], paddle_frect.size[1]

    pad_x_centre, pad_y_centre = pad_x_coord + pad_x_size / 2, pad_y_coord + \
                                 pad_y_size / 2

    o_pad_x_coord, o_pad_y_coord = other_paddle_frect.pos[0], \
                                   other_paddle_frect.pos[1]
    o_pad_x_size, o_pad_y_size = other_paddle_frect.size[0], \
                                 other_paddle_frect.size[1]

    o_pad_x_centre, o_pad_y_centre = o_pad_x_coord + o_pad_x_size / 2, \
                                     o_pad_y_coord + o_pad_y_size / 2

    ball_x_coord, ball_y_coord = ball_frect.pos[0], ball_frect.pos[1]
    ball_x_size, ball_y_size = ball_frect.size[0], ball_frect.size[1]

    ball_x_centre, ball_y_centre = ball_x_coord + ball_x_size / 2, \
                                   ball_y_coord + ball_y_size / 2
    ball_d = float(ball_x_size) / 2

    # figure out which side we're on
    on_the_right = pad_x_centre == 420  # blaze it

    # calculate distances
    x_dist, y_dist = pad_x_centre - ball_x_centre, pad_y_centre - ball_y_centre
    d_dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

    o_x_dist, o_y_dist = o_pad_x_centre - ball_x_centre, o_pad_y_centre - \
                         ball_y_centre
    o_d_dist = math.sqrt(o_x_dist ** 2 + o_y_dist ** 2)

    # calculate table info
    table_x = table_size[0]
    table_y = table_size[1]
    gutter = ball_x_size

    starting_pos = (table_x // 2, table_y // 2)
    right_edge = table_x - gutter - pad_x_size - ball_d
    left_edge = gutter + pad_x_size + ball_d

    # rounding
    num_digits = 9

    # fill up global info arrays to keep track
    history['paddle_y'].append(pad_y_centre)
    history['ball_x'].append(round(ball_x_centre, num_digits))
    history['ball_y'].append(round(ball_y_centre, num_digits))
    history['x_dist'].append(round(x_dist, num_digits))
    history['y_dist'].append(round(y_dist, num_digits))
    history['d_dist'].append(round(d_dist, num_digits))
    history['o_d_dist'].append(round(o_d_dist, num_digits))

    trim_history(history, 30)

    # calculate ball velocity
    if len(history['ball_x']) > 1:
        ball_x_vel = -(history['ball_x'][-2] - history['ball_x'][-1])
        ball_y_vel = -(history['ball_y'][-2] - history['ball_y'][-1])
    else:
        ball_x_vel, ball_y_vel = 0, 0  # for the first run

    history['x_vels'].append(ball_x_vel)
    history['y_vels'].append(ball_y_vel)

    # relative stuff
    towards_us = (on_the_right and ball_x_vel > 0) or (
        not on_the_right and ball_x_vel < 0)

    # reset after goal
    if (ball_x_centre, ball_y_centre) == starting_pos and history[
        'ball_x'] != 0:
        scored, calculated, collision = False, False, False
        goto = -1

    # use collision detection for initial ball
    try:
        if (history['ball_x'][-3], history['ball_y'][-3]) == starting_pos:
            collision = True
    except IndexError:
        pass

    # track scoring
    if ball_x_centre > right_edge + 10 and not scored:  # goal on right
        score[score[0]][0] += 1  # changes score of current round's left player
        scored = True

    elif ball_x_centre < left_edge - 10 and not scored:  # goal on left
        score[score[0]][
            1] += 1  # changes score of current round's right player
        scored = True

    # post collision, do math magic
    if collision and not scored and not calculated:
        set_goto(table_y, ball_d, right_edge, left_edge,
                 on_the_right)

    # check for bouncing (bow chicka wow woooow)
    if not scored:
        bouncy(table_x, ball_x_centre)

    # the main show
    if towards_us and goto != -1:
        if pad_y_centre < goto:
            return "down"
        else:
            return "up"
    else:
        if pad_y_centre < ball_y_centre:
            return "down"
        else:
            return "up"


def bouncy(table_x, ball_x_centre):
    """Determine where and when collisions occur.

    :param table_x: horizontal table width
    :param ball_x_centre: self explanatory
    """
    global collision, calculated

    try:
        last_xv, second_last_xv = history['x_vels'][-1], history['x_vels'][-2]
        last_yv, second_last_yv = history['y_vels'][-1], history['y_vels'][-2]
    except IndexError:
        last_xv, second_last_xv = 0, 0
        last_yv, second_last_yv = 0, 0

    periphery = not (table_x - 50 > ball_x_centre > 50)

    # ceiling
    if last_yv > 0 > second_last_yv and last_xv == 0:
        collision = True

    # floor
    if last_yv < 0 < second_last_yv and last_xv == 0:
        collision = True

    # paddles
    if last_xv > 0 > second_last_xv and periphery:  # hit left side
        collision = True
        calculated = False

    elif last_xv < 0 < second_last_xv and periphery:  # hit right side
        collision = True
        calculated = False


def set_goto(table_y, ball_d, right_edge, left_edge, on_the_right):
    """Determine where the paddle should go in response to a collision.

    :param table_y: table vertical height
    :param ball_d: diameter of ball
    :param right_edge: as far as the ball can go to the right
    :param left_edge: as far as the ball can go to the left
    :param on_the_right: are we on the right side this round?
    """
    global goto, calculated, collision

    x = history['ball_x'][-1]
    xv = history['x_vels'][-1]
    y = history['ball_y'][-1]
    yv = history['y_vels'][-1]

    # next coords
    x_2 = x + xv
    y_2 = y + yv

    # negate y so we're in Q4
    points = [(x, -y), (x_2, -y_2)]
    x_coords, y_coords = zip(*points)
    a = numpy.vstack([x_coords, numpy.ones(len(x_coords))]).T

    # get solutions for linear equation
    m, b = numpy.linalg.lstsq(a, y_coords)[0]

    if xv > 0 and on_the_right:  # to the right, to the right
        goto = get_new_y_col(table_y, ball_d, b, m, right_edge)

    elif xv < 0 and not on_the_right:  # to the left, to the left
        goto = get_new_y_col(table_y, ball_d, b, m, left_edge)

    # offset for more random bounces
    goto += numpy.random.randint(-19, 19)
    calculated = True
    collision = False


def get_new_y_col(table_y, ball_d, b, m, side_col, iters=30):
    """Do algebra to figure out where and when the ball will bounce iters
    times.

    :rtype : float
    :param table_y: table vertical height
    :param ball_d: diameter of ball
    :param b: y-intercept
    :param m: slope
    :param side_col: maximum horizontal distance
    :param iters: number of predictions to make
    :return: y coordinate corresponding to a goal
    """
    y_col = ((m * side_col) + b)  # where on the scoring line it will hit

    for i in range(iters):
        if -ball_d > y_col > -(table_y - ball_d):
            break

        if y_col >= -ball_d:
            x_col = (-ball_d - b) / m  # hit ceiling here
            m = -m
            b = -ball_d - (m * x_col)
            y_col = ((m * side_col) + b)

        else:
            x_col = (-(table_y - ball_d) - b) / m  # hit floor here
            m = -m
            b = -(table_y - ball_d) - (m * x_col)
            y_col = ((m * side_col) + b)

    return -y_col
