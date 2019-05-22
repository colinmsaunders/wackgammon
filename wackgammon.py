# wackgammon.py


import sys, logging, wsgiref.simple_server, cgi, json, urllib, random


FN_WEBSITE = 'home.html'

DEFAULTS = {
    'points': 24,   # number of points
    'ca': 15,       # number of checkers for player A
    'cb': 15,
    'pa': 6,        # number of pips for player A dice
    'pb': 6,
    'da': 2,        # number of player A dice
    'db': 2,
    'ma': '',       # initial men, comma-delimited list of point indexes
    'mb': '',       #   (any unplaced men are put on the bar)
    'seed': '',
}


class Dice:
    def __init__(self, seed):
        self.rng = random.Random()
        if seed not in (None, ''):
            self.rng.seed(seed)
    def roll(self, n, d):
        dice = []
        for i in range(n):
            dice.append(self.rng.randint(1, d))
        return dice


class Game:
    def __init__(self):
        self.restore_defaults()
        self.new_game()
    def restore_defaults(self):
        self.rules = {}
        for i, j in DEFAULTS.items():
            self.rules[i] = j
    def new_game(self):
        self.moves = []
        self.points = [[]] * (int(self.rules['points']) + 2)
        for i in range(len(self.points)):
            self.points[i] = [0, 0]
        self.points[0][0] = int(self.rules['ca'])
        self.points[-1][1] = int(self.rules['cb'])
        for i in self.rules['ma'].split(','):
            if 0 == len(i):
                break
            self.points[int(i)][0] += 1
            self.points[0][0] -= 1
        for i in self.rules['mb'].split(','):
            if 0 == len(i):
                break
            self.points[int(i)][1] += 1
            self.points[int(self.rules['points'])][1] -= 1
        self.dice = Dice(self.rules.get('seed'))
    def serialize_move(self, dice, movements):
        s = '%s-%s' % (','.join(map(lambda x: '%d' % x, dice)), ','.join(map(lambda x: '%d/%d' % (x[0], x[1]), movements)))
        return s
    def serialize_moves(self, moves):
        return ';'.join(map(lambda x: self.serialize_move(x), moves))
    def deserialize_move(self, s):
        dice = []
        movements = []
        ds, ms = s.split('-')
        for i in ds.split(','):
            dice.append(int(i))
        for i in ms.split(','):
            a, b = i.split('/')
            movements.append((int(a), int(b)))
        return (dice, movements)
    def deserialize_moves(self, s):
        m = []
        if 0 != len(s):
            for i in s.split(';'):
                m.append(self.deserialize_move(i))
        return m
    def serialize_points(self, points):
        return ','.join(map(lambda x: '%d.%d' % (x[0], x[1]), points))
    def save_game(self):
        s = urllib.urlencode(self.rules.items())
        s += '&moves=%s' % self.serialize_moves(self.moves)
        return s
    def load_game(self, s):
        x = cgi.parse_qs(s)
        self.restore_defaults()
        for i, j in x.items():
            if 'moves' != i:
                self.rules[i] = j[0]
        self.new_game()
        self.moves = self.deserialize_moves(x.get('moves', ''))
        for move_num, move in self.moves:
            whosemove = move_num % 2
            for movement in move[1]:
                self.points[movement[0][whosemove]] -= 1
                self.points[movement[1][whosemove]] += 1
    def dump_game(self):
        a = []
        a.append('wackgammon -- %d points' % (int(self.rules['points']), ))
        a.append('white: %d men, %d %d-sided dice, initial: %s' % (int(self.rules['ca']), int(self.rules['da']), int(self.rules['pa']), self.rules['ma']))
        a.append('black: %d men, %d %d-sided dice, initial: %s' % (int(self.rules['cb']), int(self.rules['db']), int(self.rules['pb']), self.rules['mb']))
        a.append('moves: %s' % self.serialize_moves(self.moves))
        a.append('points: %s' % self.serialize_points(self.points))
        s = '\n'.join(a) + '\n'
        return s
    def set_seed(self, seed):
        self.rng.seed(seed)


def ping():
    return 'pong'


def www_website(params):
    g_website = open(FN_WEBSITE).read()
    d = {}
    if params.has_key('foo'):
        d['foo'] = 'bar'
    s = g_website % d
    return (200, {'Content-type': 'text/html'}, s.encode('utf-8'))


def gen_svg(params):
    return 'SVG'


def www_svg(params):
    svg = gen_svg(params)
    return (200, {'Content-type': 'image/svg+xml'}, svg.encode('utf-8'))


def www_api(params):
    if 0:
        pass
    elif 'ping' == params.get('m'):
        x = ping()
        return (200, {'Content-type': 'application/json'}, json.dumps(x, indent=2))


def www(params):
    if 0:
        pass
    elif 'svg' == params.get('p'):
        return www_svg(params)
    elif 'api' == params.get('p'):
        return www_api(params)
    else:
        return www_website(params)


def wsgi(env, start_response):
    params = {}
    for i, j in cgi.parse_qs(env.get('QUERY_STRING').decode('utf-8')).items():
        params[i] = j[0]
    x = www(params)
    start_response('%s ' % x[0], x[1].items())
    return (x[2], )


def lambda_handler(event, context):
    params = event['queryStringParameters']
    if None == params:
        params = {}
    x = www(params)
    return {'statusCode': x[0], 'headers': x[1], 'body': x[2]}


def main(argv):
    if 0 == len(argv):
        c = None
    else:
        c = argv[0]
    if 0:
        pass
    elif 'roll' == c:
        d = Dice(argv[1])
        dice = d.roll(int(argv[2]), int(argv[3]))
        sys.stdout.write('%s\n' % ' '.join(map(lambda x: '%d' % x, dice)))
    elif 'ping' == c:
        print(ping())
    elif 'wsgi' == c:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout)
        httpd = wsgiref.simple_server.make_server('127.0.0.1', 8000, lambda x, y: wsgi(x, y))
        logging.info('serving on 8000 ...')
        httpd.serve_forever()
    elif 'new_game' == c:
        g = Game()
        sys.stdout.write(g.save_game())
    elif 'load_game' == c:
        g = Game()
        g.load_game(sys.stdin.read())
        sys.stdout.write(g.dump_game())
    elif 'dump_game' == c:
        g = Game()
        g.load_game(sys.stdin.read())
        s = g.dump_game()
        sys.stdout.write(s)
    elif 'get_moves' == c:
        g = Game()
        g.load_game(sys.stdin.read())
        dice = g.deserialize_dice(argv[1])
        m = g.get_moves(dice)
        for i in m:
            sys.stdout.write('%s\n' % g.serialize_move(i))
    elif 'do_move' == c:
        g = Game()
        g.load_game(sys.stdin.read())
        move = g.deserialize_move(argv[2])
        g.do_move(move)
        s = g.dump_game()
        sys.stdout.write(s)
    elif 'get_move' == c:
        pass
    else:
        raise Exception('i don\'t know how to "%s". look at the source.' % c)


if __name__ == '__main__':
    main(sys.argv[1:])
