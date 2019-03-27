#!/usr/bin/env python
"""for IC fabrication demo, also with demos on Python GUI and elements"""

# use Tkinter in Python 2, but tkinter in Python 3
import tkinter as tk


def sdist(x, y):
    '''Return squared distance with respect to the (0, 0) origin,
    which is the center of wafer
    '''
    return x * x + y * y

def fully_outside(x, y, w, h, radius):
    '''Judge whether a rectangle is fully outside a circle;
    the circle's center is on (0,0).
    '''
    R2 = radius * radius
    ## can we remove '\' here?
    if sdist(x, y) > R2 and sdist(x + w - 1, y) > R2 \
    and sdist(x, y + h - 1) > R2 \
    and sdist(x + w - 1, y + h - 1) > R2:
        return True
    else:
        return False

def fully_inside(x, y, w, h, radius):
    '''Judge whether a rectangle is fully outside a circle;
    the circle's center is on (0,0).
    '''
    R2 = radius * radius
    ## can we remove '\' here?
    if sdist(x, y) < R2 and sdist(x + w - 1, y) < R2 \
    and sdist(x, y + h - 1) < R2 \
    and sdist(x + w - 1, y + h - 1) < R2:
        return True
    else:
        return False

def cross(range_1, range_2):
    range_min = min(range_1[0], range_2[0])
    range_max = max(range_1[1], range_2[1])
    length = range_max - range_min
    length_1 = range_1[1] - range_1[0]
    length_2 = range_2[1] - range_2[0]

    if length_1 + length_2 > length:
        return True
    else:
        return False

def gen_close_list(planned):
    (wrap_w, wrap_h) = mpw([])
    test_dices = [[] for i in range(DICE_NUM)]

    for i in range(DICE_NUM):
        # up close
        x_min = planned[i][0]
        x_max = planned[i][0] + planned[i][2]
        x_range = (x_min, x_max)

        y = planned[i][1]

        test_list = []
        for (test_x, test_y, test_w, test_h) in planned:
            y_down = test_y + test_h
            if y == 0:
                y_down = y_down - wrap_h
            if y_down == y:
                if cross(x_range, (test_x, test_x + test_w)):
                    test_dices[i].append((test_x - x_min,0 - test_h, test_w, test_h))

        # down close
        x_min = planned[i][0]
        x_max = planned[i][0] + planned[i][2]
        x_range = (x_min, x_max)

        y = planned[i][1] + planned[i][3]
        h = planned[i][3]

        test_list = []
        for (test_x, test_y, test_w, test_h) in planned:
            y_up = test_y
            if y == wrap_h:
                y_up = y_up + wrap_h
            if y_up == y:
                if cross(x_range, (test_x, test_x + test_w)):
                    test_dices[i].append((test_x - x_min, h, test_w, test_h))

        # left close
        y_min = planned[i][1]
        y_max = planned[i][1] + planned[i][3]
        y_range = (y_min, y_max)

        x = planned[i][0]

        test_list = []
        for (test_x, test_y, test_w, test_h) in planned:
            x_right = test_x + test_w
            if x == 0:
                x_right = x_right - wrap_w
            if x_right == x:
                if cross(y_range, (test_y, test_y + test_h)):
                    test_dices[i].append((0 - test_w,test_y - y_min, test_w, test_h))

        # right close
        y_min = planned[i][1]
        y_max = planned[i][1] + planned[i][3]
        y_range = (y_min, y_max)

        x = planned[i][0] + planned[i][2]
        w = planned[i][2]

        test_list = []
        for (test_x, test_y, test_w, test_h) in planned:
            x_left = test_x
            if x == wrap_w:
                x_left = x_left + wrap_w
            if x_left == x:
                if cross(y_range, (test_y, test_y + test_h)):
                    test_dices[i].append((w, test_y - y_min, test_w, test_h))

    return test_dices


def close_edge(n, x, y, radius):
    for (xx, yy, ww, hh) in test_dices[n]:
        xx = xx + x
        yy = yy + y
        if fully_inside(xx, yy, ww, hh, radius) or fully_outside(xx, yy, ww, hh, radius):
            pass
        else:
            return True
    return False

def mpw(l):
    ''' Return the desired field width and height in a tuple 'wrap',
    and return all dice's x/y/w/h information in list l.
    the information in list 'planned' could be automatically generated
    by a die placement optimizer, but here we just give a plan for demo.
    wrap has the dimensions of boundary box of all planned dice.
    '''
    planned = [(0, 0, 15, 15),
               (15, 0, 15, 10),
               (15, 10, 8, 8),
               (0, 15, 4, 5),
               (5, 15, 4, 5),
               (10, 15, 5, 5),
               (25, 12, 5, 7)]

    wrap_w = 0
    wrap_h = 0
    for one_planned in planned:
        wrap_w = max(wrap_w, one_planned[0] + one_planned[2])
        wrap_h = max(wrap_h, one_planned[1] + one_planned[3])
    wrap = (wrap_w, wrap_h)
    WRAP_W = wrap_w
    WRAP_H = wrap_h
    for t in planned:
        l.append(t)
    ## would you try use 'l = planned' to replace the 2 lines above?

    return wrap

def field(width=30, height=30, radius=300, det=False):
    '''Expose many fields on wafer by stepper,
    each field has width, height; each wafer has diameter
    when det is True:
        mpw() returns a list of die positions and dimensions,
        then details inside each field are drawn (a few dices inside)
    the wafer center might be on a field center or on field corner
    but here to demonstrate Python list, we just implement the latter
    '''
    root = tk.Tk()

    cv_rect_list = [[] for i in range(DICE_NUM)]

    x_c = 1.5 * radius; y_c = 1.25 * radius
    cv = tk.Canvas(root, bg='white', width=2*x_c, height=2*y_c)

    if det:
        dice_list = []
        ## when det is True, field width and height are over-set by mpw()
        (width, height) = mpw(dice_list)

    ## expose all fields below. first generate a list of tuples,
    ## which contains 4 quadrants' field left-bottom corners x/y
    ## copying from one quadrant can easily keep field placement symmetry
    x_list = [x for x in range(0, radius, width)]
    y_list = [y for y in range(0, radius, height)]

    xy_list = [(x, y) for x in x_list for y in y_list] \
    + [(-x - width, y) for x in x_list for y in y_list] \
    + [(-x - width, -y - height) for x in x_list for y in y_list] \
    + [(x, -y - height) for x in x_list for y in y_list]

    for (x, y) in xy_list:
        if not fully_outside(x, y, width, height, radius):
            cv.create_rectangle(x_c + x, y_c + y, \
            x_c + x + width, y_c + y + height, width=1)

            ## next, draw all mpw dice in detail. for each field,
            ## the given x/y coordinates from mpw() are drawn
            if det:
                for (i, (xx, yy, ww, hh)) in enumerate(dice_list):
                    x1 = x_c + x + xx
                    y1 = y_c + y + yy
                    if fully_inside(x1 - x_c, y1 - y_c, ww, hh, radius):
                        if close_edge(i, x1 - x_c, y1 -y_c, radius):
                            cv_rect_list[i].append(cv.create_rectangle(x1, y1, x1 + ww, y1 + hh, fill = "green"))
                        else:
                            cv_rect_list[i].append(cv.create_rectangle(x1, y1, x1 + ww, y1 + hh))
                    elif fully_outside(x1 - x_c, y1 - y_c, ww, hh, radius):
                        cv.create_rectangle(x1, y1, x1 + ww, y1 + hh)
                    else:
                        cv.create_rectangle(x1, y1, x1 + ww, y1 + hh, fill = "red")

    if det:
        string_var = [tk.StringVar() for i in range(7)]

        def show_dice(n):
            print("show_dice" + str(n))
            for i in range(DICE_NUM):
                if i == n:
                    string_var[i].set(len(cv_rect_list[i]))
                    for one_rect in cv_rect_list[i]:
                        cv.itemconfig(one_rect, fill = 'blue')
                else:
                    string_var[i].set("")
                    for one_rect in cv_rect_list[i]:
                        cv.itemconfig(one_rect, fill = 'white')

        for i in range(DICE_NUM):
            if i == 0:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(0))
            elif i == 1:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(1))
            elif i == 2:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(2))
            elif i == 3:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(3))
            elif i == 4:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(4))
            elif i == 5:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(5))
            elif i == 6:
                tmp_button = tk.Button(cv, text = ("dice" + str(i)), bg = "blue", command = lambda: show_dice(6))
            tmp_button.place(rely = i/DICE_NUM, relx = 0)

            tk.Label(cv, textvariable = string_var[i], background = 'white').place(rely = i/DICE_NUM, relx = 0.1)

    ## draw a wafer, its center is on canvas center, r=radius
    cv.create_oval(x_c - radius, y_c - radius,
                   x_c + radius, y_c + radius, outline = 'yellow')
    cv.pack()

    root.mainloop()


def show_mpw(n=10):
    ''' Show the MPW arrangement in detail with adjusting scale 'n'
    Usage: show_mpw() or show_mpw(n=value)
    '''
    ## get mpw information
    singleMPW = []
    (w, h) = mpw(singleMPW)

    root = tk.Tk()
    cv = tk.Canvas(root, bg='white', width=20+w*n, height=20+h*n)
    cv.pack()

    ## init position setting
    xcor = 10
    ycor = 10

    cv.create_rectangle(xcor, ycor,
                        xcor + w * n, ycor + h * n, fill='lightgrey')

    for (x, y, w, h) in singleMPW:
        x1 = xcor + x * n
        y1 = ycor + y * n
        cv.create_rectangle(x1, y1, x1+w*n, y1+h*n, width=3)

    root.mainloop()

#Try all commands below, one by one
# show_mpw()
# field()
# field(24,28,150)
# field(30,20)
# field(det=True)
# field(det=True, radius=450)

if __name__ == "__main__":
    planned = [(0, 0, 15, 15),
               (15, 0, 15, 10),
               (15, 10, 8, 8),
               (0, 15, 4, 5),
               (5, 15, 4, 5),
               (10, 15, 5, 5),
               (25, 12, 5, 7)]
    DICE_NUM = len(planned)
    test_dices = gen_close_list(planned)

    # show_mpw()
    # field()
    # field(24,28,150)
    # field(30,20)
    field(det=True)
    # field(det=True, radius=450)

## Let us try another dice floor plan
#    planned = [(0, 0, 15, 15), \
#         (15, 0, 10, 15), \
#         (0, 15, 8, 8), \
#         (8, 15, 5, 4), \
#         (8, 19, 5, 4), \
#         (13, 15, 5, 5), \
#         (18, 15, 7, 5)]
#
#    wrap = (25, 23)
# also try to automatically generate 'wrap' as required in homework
