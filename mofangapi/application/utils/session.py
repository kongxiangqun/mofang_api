from redis import Redis


def init_session(app):
    host = app.config.get('SESSION_REDIS_HOST', '127.0.0.1')
    port = app.config.get('SESSION_REDIS_PORT', 6379)
    db = app.config.get('SESSION_DB', 1)
    app.config['SESSION_REDIS'] = Redis(host=host, port=port, db=db)
