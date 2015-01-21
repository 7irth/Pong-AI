__author__ = 'Tirth'

import math

# globals to contain game history
pad_y_vals, ball_x_vals, ball_y_vals = [], [], []
x_distances, y_distances, d_distances = [], [], []
score = [0, 0]

# dictionary representation of game state
history = dict(paddle_y=pad_y_vals, ball_x=ball_x_vals, ball_y=ball_y_vals,
               y_dist=y_distances, x_dist=x_distances, d_dist=d_distances)

def trim_history(hist, trim_size=50):
    if len(hist[hist.keys()[0]]) > trim_size:  # for efficiency
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
    debug = False

    # Ideas
    # - calculate where the ball will bounce off of the opponent's paddle?
    # - create ball and paddle classes?
    # - track ball's velocity to predict where it will go; use game source?

    # Issues/TODOs
    # - make sure collisions are using the right coordinates
    # - figure out how to get the final score for unit testing
    # - determine the optimal history trim size (philosophical quandary notwithstanding)
    # - replace constants with derived variables

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

    table_x = table_size[0]
    table_y = table_size[1]

    # figure out which side we're on
    right_side = (pad_x_centre == 420)  # blaze it

    # calculate distances
    x_dist = pad_x_centre - ball_x_centre
    y_dist = pad_y_centre - ball_y_centre
    d_dist = math.sqrt(x_dist ** 2 + y_dist ** 2)

    # calculate collision surfaces, if necessary

    # keep track of score
    starting_pos = [table_x//2, table_y//2]

    if len(history['ball_x']) is not 0:
        last_ball_x = history['ball_x'][-1]

        if [ball_x_centre, ball_y_centre] == starting_pos:
            print "GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOAL!"
            if last_ball_x > table_x/2:  # ball was last on the right, so left scored
                score[0] += 1
            else:
                score[1] += 1

    # rounding
    num_digits = 2

    # fill up global info arrays to keep track
    pad_y_vals.append(pad_y_centre)
    ball_x_vals.append(round(ball_x_centre, num_digits))
    ball_y_vals.append(round(ball_y_centre, num_digits))
    x_distances.append(round(x_dist, num_digits))
    y_distances.append(round(y_dist, num_digits))
    d_distances.append(round(d_dist, num_digits))

    trim_history(history, 30)

    if debug:
        """Prints out debug info and metrics, currently:
        table dimensions
        current side
        paddle (x, y)
        ball (x, y)
        normalized (x, y), basically a position in [0, 1], useful? I dunno
        distance (x, y), from centre of ball to centre of paddle
        history
        """

        # general debug info
        print 'table dimensions: ' + str(table_x) + ' by ' + str(table_y)

        print 'current side:',

        if right_side:
            print 'right'
        else:
            print 'left'

        print 'paddle     x: ' + str(pad_x_centre) + ',    y: ' + str(pad_y_centre)

        print 'ball       x: ' + str(round(ball_x_centre, num_digits)) + \
              ', y: ' + str(round(ball_y_centre, num_digits))

        print 'normalized x: ' + str(round(ball_x_centre/table_x, num_digits)) + \
              ',   y: ' + str(round(ball_y_centre/table_y, num_digits))

        # distances (centre of paddle to centre of ball)
        print 'distance   x: ' + str(round(x_dist, num_digits)) + \
              ', y: ' + str(round(y_dist, num_digits)) + ', d: ' + str(round(d_dist, num_digits))

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
        # custom ai
        # if ball is moving away, return to middle,
        # otherwise standard behaviour

        # runtime debugging
        print score

        if right_side and history['x_dist'][-1:] < history['x_dist'][-2:-1] or \
       not right_side and history['x_dist'][-1:] > history['x_dist'][-2:-1]:  # moving towards us
            if pad_y_centre < ball_y_centre:
                return "down"
            else:
                return "up"
        else:
            if pad_y_centre < table_y/2:
                return "down"
            else:
                return "up"