from muranocommon.messaging import MqClient
from engine import config as cfg


def create_rmq_client():
    rabbitmq = cfg.CONF.rabbitmq
    connection_params = {
        'login': rabbitmq.login,
        'password': rabbitmq.password,
        'host': rabbitmq.host,
        'port': rabbitmq.port,
        'virtual_host': rabbitmq.virtual_host,
        'ssl': rabbitmq.ssl,
        'ca_certs': rabbitmq.ca_certs.strip() or None
    }
    return MqClient(**connection_params)
