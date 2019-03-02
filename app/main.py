import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response
from AStar import neighbours, a_star

def init(data):
#{  #"turn": 1,
    #"game": {  #"id": "d6e8f7e3-f95d-4d43-88bc-18768eb2960c"},
    #"board": { #"food": #[{"y": 6, "x": 8}, {"y": 2, "x": 9}, {"y": 1, "x": 5}, {"y": 7, "x": 1}, {"y": 7, "x": 6}, {"y": 3, "x": 4}, {"y": 6, "x": 10}, {"y": 10, "x": 4}, {"y": 12, "x": 2}, {"y": 13, "x": 8}],
                #"width": 15,
                #"snakes":  #[{"body": [{"y": 1, "x": 13}, {"y": 2, "x": 13}, {"y": 2, "x": 13}],
                #"health": 99,
                #"id": "f854cec3-fc10-465f-91c7-1f100d35e691",
                #"name": "Test2"}],
                #"height": 15},
    #"you": {   #"body": [{"y": -1, "x": 11}, {"y": 0, "x": 11}, {"y": 0, "x": 11}],
                #"health": 99,
                #"id": "7ecaaa6f-9c4a-4c90-9b44-fdd8423cf203",
                #"name": "Test1"}}

    grid = [[0 for col in xrange(data['game']["height"])] for row in xrange(data['width'])]
    for snek in data['snakes']:
        if snek['id']== data['you']:
            mysnake = snek
        for coord in snek['coords']:
            grid[coord[0]][coord[1]] = SNAKE

    for f in data['food']:
        grid[f[0]][f[1]] = FOOD

return mysnake, grid


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

    directions = ['up', 'left', 'down', 'right']

    our_snake, grid = init(data)


    our_snake = data["you"]["body"]
    snake_head = [our_snake[0]["x"], our_snake[0]["y"]]

    print(snake_head)
    path = a_star(snake_head, food, grid, snek_coords)
    direction = directions[data["turn"]%4]

    #direction = random.choice(directions)

    return move_response(direction)


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
