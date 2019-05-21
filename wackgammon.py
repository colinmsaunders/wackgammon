# movahhed.py


import sys, logging, wsgiref.simple_server, cgi, json


FN_WEBSITE = 'home.html'


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
    elif 'ping' == c:
        print(ping())
    elif 'wsgi' == c:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', stream=sys.stdout)
        httpd = wsgiref.simple_server.make_server('127.0.0.1', 8000, lambda x, y: wsgi(x, y))
        logging.info('serving on 8000 ...')
        httpd.serve_forever()
    elif 'load_game' == c:
        game = load_game(sys.stdin.read())
        print(json.dumps(serialize_game(game)))
    elif 'draw_game' == c:
        game = load_game(sys.stdin.read())
        options = {}
        svg = draw_game(game, options)
        sys.stdout.write(svg)
    elif 'get_moves' == c:
        game = load_game(sys.stdin.read())
        moves = gen_moves(game)
        for i, j in enumerate(moves):
            sys.stdout.write('%d\t%s\n' % (i, str(j)))
    elif 'do_move' == c:
        game = load_game(sys.stdin.read())
        move = parse_move(argv[1])
        game2 = do_move(game, move)
        sys.stdout.write(serialize_game(game2))
    elif 'get_move' == c:
        pass
    else:
        raise Exception('i don\'t know how to "%s". look at the source.' % c)


if __name__ == '__main__':
    main(sys.argv[1:])
