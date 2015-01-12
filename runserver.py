from rankomatic import app
from otorderd_logd import daemon_is_running


if __name__ == '__main__':
    if daemon_is_running(app.config['WORKER_ADDRESS']):
        app.run(threaded=True)
    else:
        raise Exception("Run otorderd before starting server")
