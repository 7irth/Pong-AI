__author__ = 'Tirth'

import math

# dictionary representation of game state
history = dict(paddle_y=[], ball_x=[], ball_y=[], y_dist=[], x_dist=[], d_dist=[],
               x_vels=[], y_vels=[])

score = [1, [0, 0], [0, 0]]  # [round, round_one, round_two]
goto = -1

collision, scored = False, False

def trim_history(hist, trim_size=50):
    global history

    if trim_size == 0:
        history = dict(paddle_y=[], ball_x=[], ball_y=[], y_dist=[], x_dist=[],
                       d_dist=[], x_vels=[], y_vels=[])

    if len(hist[hist.keys()[0]]) > trim_size:  # only check one for efficiency
        for key in hist.keys():
            while len(hist[key]) > trim_size:
                hist[key].pop(0)

def pong_ai(paddle_frect, other_paddle_frect, ball_frect, table_size):
    """return "up" or "down", depending on which way the paddle should go to
    align its centre with the centre of the ball, assuming the ball will
    not be moving

    Arguments:
    paddle_frect: a rectangle representing the coordinates of the paddle
                  paddle_frect.pos[0], paddle_frect.pos[1] is the top-left
                  corner of the rectangle.
                  paddle_frect.size[0], paddle_frect.size[1] are the dimensions
                  of the paddle along the x and y axis, respectively

    other_paddle_frect:
                  a rectangle representing the opponent paddle. It is formatted
                  in the same way as paddle_frect
    ball_frect:   a rectangle representing the ball. It is formatted in the
                  same way as paddle_frect
    table_size:   table_size[0], table_size[1] are the dimensions of the table,
                  along the x and the y axis respectively

    The coordinates look as follows:

     0             x
     |------------->
     |
     |
     |
 y   v
    """

    stock_ai = False
    metrics_debug = False
    collision_debug = False
    score_to_win = 10
    global collision
    global scored
    global goto

    # Ideas
    # - calculate where the ball will bounce off of the opponent's paddle?
    # - create ball and paddle classes?
    # - use linear algebra for plotting?

    # Issues/TODOs
    # - make sure collisions are using the right coordinates/values
    # - figure out how to get the final score for unit testing
    # - determine the optimal history trim size (philosophical quandary notwithstanding)
    # - replace constants with derived variables
    # - second round start auto gives a point, kinda randomly
    # - calculate more than a direct hit

    # friendlier names, variables
    pad_x_coord = paddle_frect.pos[0]
    pad_y_coord = paddle_frect.pos[1]
    pad_x_size = paddle_frect.size[0]
    pad_y_size = paddle_frect.size[1]

    pad_x_centre = pad_x_coord + pad_x_size/2
    pad_y_centre = pad_y_coord + pad_y_size/2

    o_pad_x_coord = other_paddle_frect.pos[0]
    o_pad_y_coord = other_paddle_frect.pos[1]
    o_pad_x_size = other_paddle_frect.size[0]
    o_pad_y_size = other_paddle_frect.size[1]

    o_pad_x_centre = o_pad_x_coord + o_pad_x_size/2
    o_pad_y_centre = o_pad_y_coord + o_pad_y_size/2

    ball_x_coord = ball_frect.pos[0]
    ball_y_coord = ball_frect.pos[1]
    ball_x_size = ball_frect.size[0]
    ball_y_size = ball_frect.size[1]

    ball_x_centre = ball_x_coord + ball_x_size/2
    ball_y_centre = ball_y_coord + ball_y_size/2

    # figure out which side we're on
    right_side = (pad_x_centre == 420)  # blaze it

    # calculate distances
    x_dist = pad_x_centre - ball_x_centre
    y_dist = pad_y_centre - ball_y_centre
    d_dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

    # calculate collision surfaces, if necessary

    # calculate table info
    table_x = table_size[0]
    table_y = table_size[1]

    starting_pos = [table_x//2, table_y//2]
    right_edge = table_x - (2 * pad_x_size)  # 420
    left_edge = 2 * pad_x_size  # 20

    # reset after goal
    if [ball_x_centre, ball_y_centre] == starting_pos:
        scored = False
        goto = -1
        trim_history(history, 0)

    # track scoring
    if ball_x_centre > right_edge and not scored:
        scored = True
        score[score[0]][0] += 1  # changes score of current round's left player
        print "GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOAL at",
        print str(ball_x_centre), str(ball_y_centre), "score is now", score

    elif ball_x_centre < left_edge and not scored:
        scored = True
        score[score[0]][1] += 1  # changes score of current round's right player
        print "GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOAL at",
        print str(ball_x_centre), str(ball_y_centre), "score is now", score

    if max(score[1]) == score_to_win:
        score[0] = 2  # switch to round 2

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

    # relative ball movement
    towards_us = (right_side and ball_x_vel > 0 or
                  not right_side and ball_x_vel < 0)

    # post collision, do math magic, TODO: investigate linear algebra
    if collision and not scored:
        x = ball_x_centre
        xv = ball_x_vel
        y = ball_y_centre
        yv = ball_y_vel

        # linear algebra instead? convert so we're in Q4
        x_2 = x + xv
        y_2 = y + yv
        # find eq for (x, y) and (x_2, y_2)

        slope = (-y_2 - -y)/(x_2 - x)
        print slope

        # set how far the ball can go horizontally
        if xv > 0:  # goin' right
            if right_side:
                max_x = pad_x_coord  # 415
            else:
                max_x = o_pad_x_coord  # 415

            dx_now = max_x - x
            dx_next = dx_now - xv

        else:  # goin' left
            if right_side:
                max_x = o_pad_x_coord + o_pad_x_size  # 25
            else:
                max_x = pad_x_coord + pad_x_size  # 25

            dx_now = x - max_x
            dx_next = dx_now + xv

        # set how far the ball can go vertically
        if yv < 0:  # goin' up
            max_y = 0
            dy_now = y
            dy_next = dy_now + yv
        else:  # headin' down
            max_y = table_y  # 280
            dy_now = max_y - y
            dy_next = dy_now - yv

        # time steps until max distance TODO: fix NaN hack
        try:
            max_x_steps = abs(dx_now/xv)
        except ZeroDivisionError:
            max_x_steps = 0

        max_y_steps = abs(dy_now/yv)

        # INTELLIGENCE
        if max_x_steps < max_y_steps:  # scoring trajectory
            if xv > 0:  # on right goal
                if right_side:  # watch out
                    goto = y + max_x_steps * yv  # figure out collision y
                    print 'could score at', goto

                else:
                    pass  # other guy better watch out

            else:  # on left goal
                if not right_side:  # watch out
                    goto = y + max_x_steps * yv  # figure out collision y
                    print 'could score at', goto

                else:
                    pass  # other guy better watch out

        else:  # going to hit the ceiling or floor
            if towards_us:  # calculate further out
                pass

            else:  # sit back
                pass

        if collision_debug:
            print 'Starting from', x, y, 'going', str(xv), str(yv),
            print "to a max:", max_x, max_y

            print 'x dx', dx_now, dx_next
            print 'y dy', dy_now, dy_next
            print 'x steps', max_x_steps, 'y steps', max_y_steps

            if max_x_steps < max_y_steps:
                print 'x contact!'
                print 'y around:', y + max_x_steps * yv
            else:
                print 'y contact'
                print 'x around:', x + max_y_steps * xv

        collision = False

    history['x_vels'].append(ball_x_vel)
    history['y_vels'].append(ball_y_vel)

    # bounce check for floor/ceiling
    if ball_x_vel == 0 and [ball_x_centre, ball_y_centre] != starting_pos:
        collision = True

        if collision_debug:
            if ball_y_vel > 0:
                print 'BOUNCED OFF CEILING' + ' at ' + str(ball_x_centre) + \
                      ', ' + str(ball_y_centre)
            else:
                print 'BOUNCED OFF FLOOR' + ' at ' + str(ball_x_centre) + \
                      ', ' + str(ball_y_centre)

    # bounce check for paddles (use paddle coords instead?)
    try:
        last_xv, second_last_xv = history['x_vels'][-1], history['x_vels'][-2]
    except IndexError:
        last_xv, second_last_xv = 0, 0

    periphery = not (table_x-50 > ball_x_centre > 50)

    if last_xv > 0 > second_last_xv and periphery:  # direction flipped to -
        collision = True

        if collision_debug:
            if right_side:
                print 'BOUNCED OFF ENEMY' + ' at ' + str(ball_x_centre) + \
                      ', ' + str(ball_y_centre)
            else:
                print 'BOUNCED OFF SELF' + ' at ' + str(ball_x_centre) + \
                      ', ' + str(ball_y_centre)

    elif last_xv < 0 < second_last_xv and periphery:  # direction flipped to +
        collision = True

        if collision_debug:
            if right_side:
                print 'BOUNCED OFF SELF' + ' at ' + str(ball_x_centre) + \
                      ', ' + str(ball_y_centre)
            else:
                print 'BOUNCED OFF ENEMY' + ' at ' + str(ball_x_centre) + \
                      ', ' + str(ball_y_centre)

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

        if right_side:
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
        # print str(ball_x_centre) + ', ' + str(ball_y_centre)

        if towards_us and goto != -1:
            if pad_y_centre < goto:
                return "down"
            else:
                return "up"
        elif towards_us:
            if pad_y_centre < ball_y_centre:
                return "down"
            else:
                return "up"
        else:
            if pad_y_centre < table_y/2:
                return "down"
            else:
                return "up"