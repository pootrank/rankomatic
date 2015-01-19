from rankomatic import app
from otorderd_logd import daemon_is_running


if not daemon_is_running(app.config['WORKER_ADDRESS']):
    raise Exception("Run otorderd before starting server")

if __name__ == '__main__':
    app.run(threaded=True)
