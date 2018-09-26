import xmlrpc.client as xmlrpclib
import logging
_logger = logging.getLogger(__name__)

def connection(host, port, https_on):
    _logger.debug("Creating object_facade")
    if https_on:
        url_template = "https://%s/xmlrpc/%s"
        object_facade = xmlrpclib.ServerProxy(url_template % (
            host, 'object'))
    else:
        url_template = "http://%s:%s/xmlrpc/%s"
        object_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'object'))
    return object_facade


def authenticate_connection(host, port, user, user_pw, database, https_on):
    _logger.debug("Validating Connection to Odoo via XMLRPC")
    if https_on:
        url_template = "https://%s/xmlrpc/%s"
        login_facade = xmlrpclib.ServerProxy(url_template % (
            host, 'common'))
    else:
        url_template = "http://%s:%s/xmlrpc/%s"
        login_facade = xmlrpclib.ServerProxy(url_template % (
            host, port, 'common'))
    try:
        user_id = login_facade.login(database, user, user_pw)
        if user_id:
            _logger.debug("Odoo Connection succed on XMLRPC user %s", str(user_id))
        return user_id
    except Exception:
        _logger.debug("Odoo Connection can't return user_id")
        return False