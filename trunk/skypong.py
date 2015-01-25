__author__ = 'Tirth and Monica'

import math
import numpy

# dictionary representation of game state
history = dict(paddle_y=[], ball_x=[], ball_y=[], y_dist=[], x_dist=[], d_dist=[],
               x_vels=[], y_vels=[])

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
                       d_dist=[], x_vels=[], y_vels=[])

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

    stock_ai = False
    metrics_debug = False
    collision_debug = True
    score_to_win = 2000  # to keep track of rounds
    global collision, scored, goto, calculated

    # Ideas
    # - calculate where the ball will bounce off of the opponent's paddle?
    # - create ball and paddle classes?
    # - calculate whole path at once, or one ahead?

    # Issues/TODOs
    # - make sure collisions are using the right coordinates/values
    # - figure out how to get the final score for unit testing
    # - determine the optimal history trim size (philosophical quandary notwithstanding)
    # - replace constants with derived variables
    # - second round start auto gives a point, kinda randomly
    # - taunts, fancy returns
    # - verify second round
    # - deal with awkward bounces, weird global variable states

    # Neat
    # ^ sampling a few variables lets you approximate the system
    # ^ is it possible to fully approximate?

    # friendlier names, variables
    pad_x_coord, pad_y_coord = paddle_frect.pos[0], paddle_frect.pos[1]
    pad_x_size, pad_y_size = paddle_frect.size[0], paddle_frect.size[1]

    pad_x_centre, pad_y_centre = pad_x_coord + pad_x_size/2, pad_y_coord + pad_y_size/2

    o_pad_x_coord, o_pad_y_coord = other_paddle_frect.pos[0], other_paddle_frect.pos[1]
    o_pad_x_size, o_pad_y_size = other_paddle_frect.size[0], other_paddle_frect.size[1]

    o_pad_x_centre, o_pad_y_centre = o_pad_x_coord + o_pad_x_size/2, o_pad_y_coord + o_pad_y_size/2

    ball_x_coord, ball_y_coord = ball_frect.pos[0], ball_frect.pos[1]
    ball_x_size, ball_y_size = ball_frect.size[0], ball_frect.size[1]

    ball_x_centre, ball_y_centre = ball_x_coord + ball_x_size/2, ball_y_coord + ball_y_size/2
    ball_d = float(ball_x_size)/2

    # figure out which side we're on
    on_the_right = pad_x_centre == 420  # blaze it

    # calculate distances
    x_dist, y_dist = pad_x_centre - ball_x_centre, pad_y_centre - ball_y_centre
    d_dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

    # calculate collision surfaces, if necessary

    # calculate table info
    table_x = table_size[0]
    table_y = table_size[1]
    gutter = ball_x_size  # not really related, might have to figure out a better way

    starting_pos = (table_x//2, table_y//2)
    right_edge = table_x - gutter - pad_x_size - ball_d
    left_edge = gutter + pad_x_size + ball_d

    # rounding
    num_digits = 9

    # fill up global info arrays to keep track (more efficient trim here?)
    history['paddle_y'].append(pad_y_centre)
    history['ball_x'].append(round(ball_x_centre, num_digits))
    history['ball_y'].append(round(ball_y_centre, num_digits))
    history['x_dist'].append(round(x_dist, num_digits))
    history['y_dist'].append(round(y_dist, num_digits))
    history['d_dist'].append(round(d_dist, num_digits))

    # keep score history somehow

    trim_history(history, 30)

    # calculate ball velocity (only two point accuracy needed, no accel)
    if len(history['ball_x']) > 1:
        ball_x_vel = -(history['ball_x'][-2] - history['ball_x'][-1])
        ball_y_vel = -(history['ball_y'][-2] - history['ball_y'][-1])
    else:
        ball_x_vel, ball_y_vel = 0, 0  # for the first run

    history['x_vels'].append(ball_x_vel)
    history['y_vels'].append(ball_y_vel)

    # relative ball movement, relative velocity?
    towards_us = (on_the_right and ball_x_vel > 0) or (not on_the_right and ball_x_vel < 0)

    # reset after goal
    if (ball_x_centre, ball_y_centre) == starting_pos and history['ball_x'] != 0:
        scored, calculated, collision = False, False, False
        goto = -1


    # not sure if necessary, use collision detection for initial ball
    try:
        if (history['ball_x'][-3], history['ball_y'][-3]) == starting_pos:
            collision = True
    except IndexError:
        pass

    # track scoring
    if ball_x_centre > right_edge + 10 and not scored:  # goal on right
        score[score[0]][0] += 1  # changes score of current round's left player
        scored = True

        if on_the_right:
            print "DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMN at",
        else:
            print "GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOAL at",
        print str(ball_x_centre), str(ball_y_centre), "score is now", score

    elif ball_x_centre < left_edge - 10 and not scored:  # goal on left
        score[score[0]][1] += 1  # changes score of current round's right player
        scored = True

        if not on_the_right:
            print "DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMN at",
        else:
            print "GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOAL at",
        print str(ball_x_centre), str(ball_y_centre), "score is now", score

    if max(score[1]) == score_to_win:
        score[0] = 2  # switch to next round

    # post collision, do math magic - integrate right after collision somehow?
    if collision and not scored and not calculated:
        set_goto(ball_x_centre, ball_x_vel, ball_y_centre, ball_y_vel, table_y, ball_d, right_edge, left_edge, on_the_right)

    # check for bouncing (bow chicka wow woooow)
    bouncy(table_x, ball_x_centre, ball_y_centre, starting_pos, on_the_right, collision_debug)

    if metrics_debug:
        """Prints out debug info and metrics, currently:
        table dimensions
        current side
        paddle location (x, y)
        ball location (x, y)
        normalized (x, y), basically a position in [0, 1], useful? I dunno
        distance (x, y), from centre of ball to centre of paddle
        ball velocity (x, y)
        history
        score
        """

        # general debug info
        print 'table dimensions: ' + str(table_x) + ' by ' + str(table_y)

        print 'current side:',

        if on_the_right:
            print 'right'
        else:
            print 'left'

        print 'paddle_c   x: ' + str(pad_x_centre) + ',    y: ' + str(pad_y_centre)

        print 'ball_c     x: ' + str(round(ball_x_centre, num_digits)) + \
              ', y: ' + str(round(ball_y_centre, num_digits))

        print 'normalized x: ' + str(round(ball_x_centre/table_x, num_digits)) + \
              ',   y: ' + str(round(ball_y_centre/table_y, num_digits))

        # distances (centre of paddle to centre of ball)
        print 'distance   x: ' + str(round(x_dist, num_digits)) + \
              ', y: ' + str(round(y_dist, num_digits)) + ', d: ' + str(round(d_dist, num_digits))

        print 'ball_v     x: ' + str(round(ball_x_vel, num_digits)) + \
              ', y: ' + str(round(ball_y_vel, num_digits))

        # total history
        for key in history:
            print key
            print history[key]

        # score
        print score

        print '-'

    if stock_ai:
        # checks if middle of the paddle is lower than middle of the ball
        if pad_y_centre < ball_y_centre:
            return "down"
        else:
            return "up"
    else:
        # CUSTOM AI
        # if ball is moving away, return to middle
        # if ball is on a scoring trajectory, centre paddle there

        # runtime debugging
        print 'ball: {x}, {y}'.format(x=ball_x_centre, y=ball_y_centre)

        if towards_us and goto != -1:
            if pad_y_centre < goto:
                return "down"
            else:
                return "up"
        elif towards_us:
            # print 'LOL I DUNNO'
            if pad_y_centre < ball_y_centre:
                return "down"
            else:
                return "up"
        else:
            if pad_y_centre < table_y/2:
                return "down"
            else:
                return "up"


def bouncy(table_x, ball_x_centre, ball_y_centre, starting_pos, on_the_right, collision_debug):
    """Determine where and when collisions occur.

    :param table_x: horizontal table width
    :param ball_x_centre: self explanatory
    :param ball_y_centre: self explanatory
    :param starting_pos: exact centre of table
    :param on_the_right: are we on the right side this round?
    :param collision_debug: flag to print debug collision locations
    """
    global collision, calculated
    
    try:
        last_xv, second_last_xv = history['x_vels'][-1], history['x_vels'][-2]
        last_yv, second_last_yv = history['y_vels'][-1], history['y_vels'][-2]
    except IndexError:
        last_xv, second_last_xv = 0, 0
        last_yv, second_last_yv = 0, 0

    periphery = not (table_x-50 > ball_x_centre > 50)

    # ceiling
    if last_yv > 0 > second_last_yv:
        collision = True

        if collision_debug:
            print 'BOUNCED OFF CEILING at ({x}, {y}), going ({xv}, {yv})'.format(x=ball_x_centre, y=ball_y_centre, xv=last_xv, yv=last_yv)

    # floor
    if last_yv < 0 < second_last_yv:
        collision = True

        if collision_debug:
            print 'BOUNCED OFF FLOOR at ({x}, {y}), going ({xv}, {yv})'.format(x=ball_x_centre, y=ball_y_centre, xv=last_xv, yv=last_yv)

    # paddles (use paddle coords instead?)
    if last_xv > 0 > second_last_xv and periphery:  # hit left side
        collision = True
        calculated = False

        if collision_debug:
            if on_the_right:
                print 'BOUNCED OFF ENEMY at ({x}, {y}), going ({xv}, {yv})'.format(x=ball_x_centre, y=ball_y_centre, xv=last_xv, yv=last_yv)
            else:
                print 'BOUNCED OFF SELF at ({x}, {y}), going ({xv}, {yv})'.format(x=ball_x_centre, y=ball_y_centre, xv=last_xv, yv=last_yv)

    elif last_xv < 0 < second_last_xv and periphery:  # hit right side
        collision = True
        calculated = False

        if collision_debug:
            if on_the_right:
                print 'BOUNCED OFF SELF at ({x}, {y}), going ({xv}, {yv})'.format(x=ball_x_centre, y=ball_y_centre, xv=last_xv, yv=last_yv)
            else:
                print 'BOUNCED OFF ENEMY at ({x}, {y}), going ({xv}, {yv})'.format(x=ball_x_centre, y=ball_y_centre, xv=last_xv, yv=last_yv)


def set_goto(x, xv, y, yv, table_y, ball_d, right_edge, left_edge, on_the_right):
    """Determine where the paddle should go in response to a collision.

    :param x: ball x coordinate
    :param xv: ball x velocity
    :param y: ball y coordinate
    :param yv: ball y velocity
    :param table_y: table vertical height
    :param ball_d: diameter of ball
    :param right_edge: as far as the ball can go to the right
    :param left_edge: as far as the ball can go to the left
    :param on_the_right: are we on the right side this round?
    """
    global goto, calculated, collision

    print '----'
    print 'STARTING MAGIC'

    # TODO: fix when xv is 0
    # next coords
    x_2 = x + xv
    y_2 = y + yv

    print 'Using coords ({x}, {y}) and ({x2}, {y2}) for math'.format(x=x, y=y, x2=x_2, y2=y_2)

    # negate y so we're in Q4
    points = [(x, -y), (x_2, -y_2)]
    x_coords, y_coords = zip(*points)
    a = numpy.vstack([x_coords, numpy.ones(len(x_coords))]).T

    # get solutions for linear equation
    m, b = numpy.linalg.lstsq(a, y_coords)[0]

    print "y = {m}x + {b}".format(m=m, b=b)

    if xv > 0:  # to the right, to the right
        y_col = get_new_y_col(table_y, ball_d, b, m, right_edge)

        if on_the_right:
            goto = y_col
            print 'going to', goto
        else:
            print 'enemy should go to', y_col

        calculated = True

    else:  # to the left, to the left
        y_col = get_new_y_col(table_y, ball_d, b, m, left_edge)

        if not on_the_right:
            goto = y_col
            print 'going to', goto
        else:
            print 'enemy should go to', y_col

        calculated = True

    print '----'
    collision = False


def get_new_y_col(table_y, ball_d, b, m, side_col, iters=20):
    """Do algebra to figure out where and when the ball will bounce iters times.

    :rtype : float
    :param table_y: table vertical height
    :param ball_d: diameter of ball
    :param b: y-intercept
    :param m: slope
    :param side_col: maximum horizontal distance
    :param iters: number of predictions to make
    :return: y coordinate corresponding to a goal
    """
    y_col = ((m * side_col) + b)  # where on the scoring line it will hit, TODO: confirm centre

    # while not -ball_d > y_col > -(table_y-ball_d):  # figured out a score line intercept on the table
    for i in range(iters):
        print ''
        print "score line intercept: ", y_col

        if -ball_d > y_col > -(table_y-ball_d):
            print 'GOT IT'
            break

        if y_col >= -ball_d:
            x_col = (-ball_d - b) / m  # hit ceiling here

            # after it bounces at (x_col, ~0), where does it go next?
            # rejigger linear equation, new_b, flipped m
            m = -m
            b = -ball_d - (m * x_col)
            y_col = ((m * side_col) + b)
            print 'will hit ceiling at', x_col

        else:
            x_col = (-(table_y-ball_d) - b) / m  # hit floor here

            # after (x_col, ~280) bounce, what's next?
            m = -m
            b = -(table_y-ball_d) - (m * x_col)
            y_col = ((m * side_col) + b)
            print 'will hit floor at', x_col
    else:
        print '---------DEBUG ME BRO---------'

    return -y_col