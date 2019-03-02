import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response
from AStar import neighbours, a_star

import copy


NEK_BUFFER = 3
SNAKE = 1
WALL = 2
FOOD = 3
SAFTEY = 5


def direction(from_cell, to_cell):
    dx = to_cell[0] - from_cell[0]
    dy = to_cell[1] - from_cell[1]

    if dx == 1:
        return 'right'
    elif dx == -1:
        return 'left'
    elif dy == -1:
        return 'up'
    elif dy == 1:
        return 'down'


def distance(p, q):
    dx = abs(p[0] - q[0])
    dy = abs(p[1] - q[1])
    return dx + dy


def closest(items, start):
    closest_item = None
    closest_distance = 10000

    # TODO: use builtin min for speed up
    for item in items:
        item_distance = distance(start, item)
        if item_distance < closest_distance:
            closest_item = item
            closest_distance = item_distance

    return closest_item

# Returns the points around the specified point,
# in clockwise order from the top-left.


def spaces_around(point, width, height):
    l = []
    if point[1] > 0:
        if point[0] > 0:
            l.append((point[0] - 1, point[1] - 1))
        l.append((point[0], point[1] - 1))
        if point[0] < width - 1:
            l.append((point[0] + 1, point[1] - 1))
    if point[0] < width - 1:
        l.append((point[0] + 1, point[1]))
        if point[1] < height - 1:
            l.append((point[0] + 1, point[1] + 1))
    if point[1] < height - 1:
        if point[0] < width - 1:
            l.append((point[0] + 1, point[1] + 1))
        l.append((point[0], point[1] + 1))
        if point[0] > 0:
            l.append((point[0] - 1, point[1] + 1))
    if point[0] > 0:
        l.append((point[0] - 1, point[1]))
    return l


def init(data):
    mysnake={}
    grid = [[0 for col in xrange(data['height'])]
            for row in xrange(data['width'])]
    for snek in data['snakes']:
        if snek['id'] == data['you']:
            mysnake = snek
        for coord in snek['coords']:
            grid[coord[0]][coord[1]] = SNAKE

    for f in data['food']:
        grid[f[0]][f[1]] = FOOD

    mysnake = data["mysnake"]
    return mysnake, grid


def revert(data):
    old_style = {}
    old_style["game"] = data["game"]
    old_style["turn"] = data["turn"]
    old_style["height"] = data["board"]["height"]
    old_style["width"] = data["board"]["width"]
    food = []
    for f in data["board"]["food"]:
        food.append([f["x"], f["y"]])
    old_style["food"] = food
    snakes = []
    for snake in data["board"]["snakes"]:
        old_snake = {}
        old_snake["name"] = snake["name"]
        old_snake["id"] = snake["id"]
        old_snake["health_points"] = snake["health"]
        coords = []
        for coord in snake["body"]:
            coords.append([coord["x"], coord["y"]])
        old_snake["coords"] = coords
    old_style["snakes"] = snakes
    old_style["mysnake"] = {}
    coords=[]
    for coord in data["you"]["body"]:
        coords.append([coord["x"], coord["y"]])
    old_style["mysnake"]["coords"] = coords

    return old_style


@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    data = revert(data)
    #directions = ['up', 'left', 'down', 'right']
    #direction = directions[data["turn"] % 4]
    #direction = random.choice(directions)
    #return move_response(direction)

    #snake_head = our_snake[0]

    #print(snake_head)
    #path = a_star(snake_head, food, grid, our_snake)

    snek, grid = init(data)
    taunt = "I'm a sneeky snek!"

    # Dodge other snakes.
    for enemy in data['snakes']:
        if (enemy['id'] == data['you']):
            continue
        if distance(snek['coords'][0], enemy['coords'][0]) > SNEK_BUFFER:
            continue
        if (len(enemy['coords']) > len(snek['coords']) - 1):
            # dodge
            if enemy['coords'][0][1] < data['height'] - 1:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1] + 1] = SAFTEY
            if enemy['coords'][0][1] > 0:
                grid[enemy['coords'][0][0]][enemy['coords'][0][1] - 1] = SAFTEY

            if enemy['coords'][0][0] < data['width'] - 1:
                grid[enemy['coords'][0][0] + 1][enemy['coords'][0][1]] = SAFTEY
            if enemy['coords'][0][0] > 0:
                grid[enemy['coords'][0][0] - 1][enemy['coords'][0][1]] = SAFTEY
    # end for enemy in enemy snakes

    snek_head = snek['coords'][0]
    snek_coords = snek['coords']
    path = None
    middle = [data['width'] / 2, data['height'] / 2]
    foods = sorted(data['food'], key=lambda p: distance(snek_head, p))

    for food in foods:
        print food
        path = a_star(snek_head, food, grid, snek_coords)
        if not path:
            print "no path to food"
            continue

        snek_length = len(snek_coords) + 1

        can_reach_food = True
        for enemy in data['snakes']:
            if enemy['id'] == data['you']:
                continue
            pathing_epsilon = max(data['width'], data['height']) / 5
            # When racing another snake to food, we will go for the food if no
            # other snek is pathing_epsilon spaces closer than us.
            if len(path) > distance(enemy['coords'][0], food) + pathing_epsilon:
                can_reach_food = False
            # We also always go for the food if we have less than 40 health.
            if snek['health_points'] < 40:
                can_reach_food = True
                taunt = "I'm hungry!"
        if not can_reach_food:
            continue

        # If there's only one food and we're the healthiest snek,
        # then we can try to starve out the other sneks.
        if len(foods) == 1:
            least_hungry_snek = True
            for enemy in data['snakes']:
                if enemy['id'] == data['you']:
                    continue
                if enemy['health_points'] >= snek['health_points']:
                    least_hungry_snek = False
                    break
            if least_hungry_snek:
                # Encircle the food in an attempt to starve other snakes.
                path = a_star(snek_head, food, grid, snek_coords)
                if not path or len(path) > 3:
                    continue
                # If we're really close, move to a space NEXT TO the food.
                spaces_around_food = spaces_around(
                    food, data['width'], data['height'])
                spaces_around_food = filter(lambda x: x not in snek[
                                            'coords'], spaces_around_food)
                for space in spaces_around_food:
                    print "Moving to space ({0}, {1}).".format(space[0], space[1])
                    print "Food at ({0}, {1}).".format(food[0], food[1])
                    grid[food[0]][food[1]] = WALL
                    temp_path = a_star(snek_head, space, grid, snek_coords)
                    # If we're only one space away from encircling the food, go
                    # there.
                    print temp_path
                    if temp_path is not None and len(temp_path) < snek_length + 2:
                        print "blocking other sneks"
                        path = temp_path
                        taunt = "im in ur base stealin ur foodz"
                        break
        # end trying to starve out sneks

        # Update snek
        if len(path) < snek_length:
            remainder = snek_length - len(path)
            new_snek_coords = list(reversed(path)) + snek_coords[:remainder]
        else:
            new_snek_coords = list(reversed(path))[:snek_length]

        if grid[new_snek_coords[0][0]][new_snek_coords[0][1]] == FOOD:
            # we ate food so we grow
            new_snek_coords.append(new_snek_coords[-1])

        # Create a new grid with the updated snek positions
        new_grid = copy.deepcopy(grid)

        for coord in snek_coords:
            new_grid[coord[0]][coord[1]] = 0
        for coord in new_snek_coords:
            new_grid[coord[0]][coord[1]] = SNAKE

        foodtotail = a_star(
            food, new_snek_coords[-1], new_grid, new_snek_coords)
        if not foodtotail:
            path = None
            print "no path to tail from food"

        # If we have a good path, use it.
        if path is not None:
            break
    # end for food in foods

    current_direction = direction(snek['coords'][1], snek['coords'][0])
    for enemy in data['snakes']:
        if enemy['id'] == data['you']:
            continue
        if current_direction == 'left' or current_direction == 'right':
            if (len(enemy['coords']) < len(snek['coords']) - 1):
                if enemy['coords'][0] == snek['coords'][1][1] + 1:
                    path = [snek_head, (snek['coords'][0][0], snek[
                                        'coords'][0][1] + 1)]
                    taunt = "swerve!"
                elif enemy['coords'][0] == snek['coords'][1][1] - 1:
                    path = [snek_head, (snek['coords'][0][0], snek[
                                        'coords'][0][1] - 1)]
                    taunt = "swerve!"
            else:
                if enemy['coords'][0] == snek['coords'][2][1] + 1:
                    path = [snek_head, (snek['coords'][0][0], snek[
                                        'coords'][0][1] + 1)]
                    taunt = "swerve!"
                elif enemy['coords'][0] == snek['coords'][2][1] - 1:
                    path = [snek_head, (snek['coords'][0][0], snek[
                                        'coords'][0][1] - 1)]
                    taunt = "swerve!"
        elif current_direction == 'up' or current_direction == 'down':
            if (len(enemy['coords']) < len(snek['coords']) - 1):
                if enemy['coords'][0] == snek['coords'][1][0] + 1:
                    path = [snek_head, (snek['coords'][0][
                                        0] + 1, snek['coords'][0][1])]
                    taunt = "swerve!"
                elif enemy['coords'][0] == snek['coords'][1][0] - 1:
                    path = [snek_head, (snek['coords'][0][
                                        0] - 1, snek['coords'][0][1])]
                    taunt = "swerve!"
            else:
                if enemy['coords'][0] == snek['coords'][2][0] + 1:
                    path = [snek_head, (snek['coords'][0][
                                        0] + 1, snek['coords'][0][1])]
                    taunt = "swerve!"
                elif enemy['coords'][0] == snek['coords'][2][0] - 1:
                    path = [snek_head, (snek['coords'][0][
                                        0] - 1, snek['coords'][0][1])]
                    taunt = "swerve!"

    # If we aren't going for the food, go for our own tail instead.
    if not path:
        # Don't just go for your own tail. Prefer to go closer to the middle.
        # determine snake circle radius
        snek_length = len(snek_coords) + 1
        snek_radius = snek_length / 6

        # determine center of board (might be bad, check above)
        board_x_center = len(grid) / 2
        board_y_center = len(grid[0]) / 2

        # determine the location of the snake's head
        snek_head_x = snek['coords'][0][0]
        snek_head_y = snek['coords'][0][1]

        # determine bounds of snake circle around center
        left_x = board_x_center - snek_radius
        right_x = board_x_center + snek_radius
        upper_y = board_y_center - snek_radius
        bottom_y = board_y_center + snek_radius

        # if outside, move towards center.  If inside, continue as normal
        if snek_head_x < left_x or snek_head_x > right_x or snek_head_y < upper_y or snek_head_y > bottom_y:
            path = a_star(snek_head, (board_x_center,
                                      board_y_center), grid, snek_coords)
            taunt = "To the middle!"

    if not path:
        path = a_star(snek_head, snek['coords'][-1], grid, snek_coords)

    despair = not (path and len(path) > 1)
    if despair:
        for neighbour in neighbours(snek_head, grid, 0, snek_coords, [1, 2, 5]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            taunt = 'i\'m scared'
            break
    despair = not (path and len(path) > 1)

    if despair:
        for neighbour in neighbours(snek_head, grid, 0, snek_coords, [1, 2]):
            path = a_star(snek_head, neighbour, grid, snek_coords)
            taunt = 'lik so scared'
            break

    if path:
        assert path[0] == tuple(snek_head)
        assert len(path) > 1

    #return {
    #    'move': direction(path[0], path[1]),
    #}
    return move_response(direction(path[0], path[1]))


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
