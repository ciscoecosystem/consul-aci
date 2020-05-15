import datetime
import time, json
from sqlalchemy import Column, Integer, String, ForeignKey, PickleType, update, Boolean, func, DateTime, and_
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, sessionmaker, relationship
from sqlalchemy import exists
from custom_logger import CustomLogger


Base = declarative_base()
logger = CustomLogger.get_logger("/home/app/log/app.log")

class Login(Base):
    __tablename__ = 'Login'
    ip = Column(String, primary_key=True)
    port = Column(Integer, primary_key=True)
    protocol = Column(String)
    token = Column(String)
    status = Column(Boolean)
    datacenter = Column(String)
    timestamp = Column(Integer)

    def __init__(self, ip, port, protocol, token, status, datacenter, timestamp):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.token = token
        self.status = status
        self.datacenter = datacenter
        self.timestamp = timestamp


class Mapping(Base):
    __tablename__ = 'Mapping'
    ip = Column(String, primary_key=True)
    domain_name = Column(String, primary_key=True)
    disabled = Column(Boolean)
    datacenter = Column(String)

    def __init__(self, ip, domain_name, disabled, datacenter):
        self.ip = ip
        self.domain_name = domain_name
        self.disabled = disabled
        self.datacenter = datacenter


class Node(Base):
    __tablename__ = 'Node'
    node_id = Column(String, primary_key=True)
    node_name = Column(String)
    node_ips = Column(PickleType)

    def __init__(self, node_id, node_name, node_ips):
        self.node_id = node_id
        self.node_name = node_name
        self.node_ips = node_ips


class Service(Base):
    __tablename__ = 'Service'
    service_id = Column(String, primary_key=True)
    node_id = Column(String, ForeignKey('Node.node_id'))
    service_name = Column(String)
    service_ip = Column(String)
    service_port = Column(Integer)
    service_address = Column(String)
    service_tags = Column(PickleType)
    service_kind = Column(String)
    name_space = Column(String)

    def __init__(self, service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, name_space):
        self.service_id = service_id
        self.node_id = node_id
        self.service_name = service_name
        self.service_ip = service_ip
        self.service_port = service_port
        self.service_address = service_address
        self.service_tags = service_tags
        self.service_kind = service_kind
        self.name_space = name_space


class NodeChecks(Base):
    __tablename__ = 'NodeChecks'
    node_name = Column(String, primary_key=True)
    check_id = Column(String, primary_key=True)
    node_id = Column(String, ForeignKey('Node.node_id'))
    check_name = Column(String)
    service_name = Column(String)
    check_type = Column(String)
    notes = Column(String)
    output = Column(String)
    status = Column(String)

    def __init__(self, node_name, check_id, node_id, check_name, service_name, check_type, notes, output, status):
        self.node_name = node_name
        self.check_id = check_id
        self.node_id = node_id
        self.check_name = check_name
        self.service_name = service_name
        self.check_type = check_type
        self.notes = notes
        self.output = output
        self.status = status


class ServiceChecks(Base):
    __tablename__ = 'ServiceChecks'
    check_id = Column(String, primary_key=True)
    service_id = Column(String, ForeignKey('Service.service_id'), primary_key=True)
    service_name = Column(String)
    check_name = Column(String)
    check_type = Column(String)
    notes = Column(String)
    output = Column(String)
    status = Column(String)

    def __init__(self, check_id, service_id, service_name, check_name, check_type, notes, output, status):
        self.check_id = check_id
        self.service_id = service_id
        self.service_name = service_name
        self.check_name = check_name
        self.check_type = check_type
        self.notes = notes
        self.output = output
        self.status = status


class Database():
    def __init__(self):
        self.engine = create_engine("sqlite:///AppD_Test.db?check_same_thread=False")

        self.metadata = Base.metadata
        Session = sessionmaker(bind=self.engine)

        self.conn = self.engine.connect()
        self.conn = self.engine.connect()
        try:
            self.conn.execute("PRAGMA journal_mode = WAL")
        except Exception as ex:
            logger.exception("Exception setting journal mode to WAL : " + str(ex))

        self.session = Session(bind=self.conn)

    def createTables(self):
        try:
            self.metadata.create_all(self.engine)
        except Exception as e:
            logger.exception('Exception in creating tables: ' + str(e))
        return None

    def flush_session(self):
        try:
            self.session.flush()
        except Exception as e:
            logger.exception('Could not flush the session! Error:' + str(e))

    def commit_session(self):
        try:
            self.session.commit()
        except Exception as e:
            logger.exception('Exception in Committing session: ' + str(e))
            self.flush_session()

    def decorator_edit(func):
        def wrapper(*args):
            try:
                func(*args)
            except Exception as e:
                logger.exception('error in {} : {}'.format(func.__name__, str(e)))
            finally:
                args[0].commit_session() # here 0th argument is self so args[0].commit_session()
        return wrapper

    
    def decorator_read(func):
        def wrapper(*args):
            try:
                return func(*args)
            except Exception as e:
                logger.exception('error in {} : {}'.format(func.__name__, str(e)))
                return []
        return wrapper
        
    @decorator_read
    def read_login(self):
        return self.session.query(Login).all()

    @decorator_edit
    def insert_into_login(self, data):
        """
        Arguments:
            data {List of Touple} -- [
                (ip, port, protocol, token, status, datacenter),
                (ip, port, protocol, token, status, datacenter),
                ...
            ]
        """
        timestamp = int(time.time())
        login_list = [Login(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], timestamp) for entry in data]
        self.session.add_all(login_list)

    @decorator_edit
    def update_login(self, old_protocol, old_ip, old_port, data):
        """
        Arguments:
            old_protocol {String}
            old_ip {String}
            old_port {Integer}
            data {dict} -- {'ip': ,'port': ,'protocol': ,'token' ,'status': ,'datacenter'}
        """
        self.session.query(Login).filter(Login.protocol == old_protocol, Login.ip == old_ip, Login.port == old_port).update(data)

    @decorator_edit
    def delete_entry_login(self, ip, port):
        """
        Arguments:
            ip {String}
            port {Integer}
        """
        self.session.query(Login).filter(Login.ip == ip, Login.port == port).delete()

    @decorator_read
    def read_mapping(self):
        return self.session.query(Mapping).all()

    @decorator_edit
    def insert_into_mapping(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (ip, domain_name, disabled, datacenter),
                (ip, domain_name, disabled, datacenter),
                ...
            ]
        """
        mapping_list = [Mapping(entry[0], entry[1], entry[2], entry[3]) for entry in data]
        self.session.add_all(mapping_list)

    @decorator_edit
    def update_mapping(self, old_ip, old_dn, data):
        """
        Arguments:
            old_ip {String}
            old_dn {String}
            data {dict} -- {'ip': ,'domain_name': ,'disabled': ,'datacenter': }
        """
        self.session.query(Mapping).filter(Mapping.ip == old_ip, Mapping.domain_name == old_dn).update(data)


    @decorator_edit
    def delete_entry_mapping(self, ip, dn):
        """
        Arguments:
            ip {String}
            dn {String}
        """
        self.session.query(Mapping).filter(Mapping.ip == ip, Mapping.domain_name == dn).delete()

    @decorator_read
    def read_node(self):
        return self.session.query(Node).all()

    @decorator_edit
    def insert_into_node(self, data):
        """
        Arguments:
            data {list of Tuple} -- [
                (node_id, node_name, node_ips),
                (node_id, node_name, node_ips),
                ...
            ]
        """
        node_list = []
        for entry in data:
            # node_list.append(Node(entry[0], entry[1], entry[2]))
            self.session.add(Node(entry[0], entry[1], entry[2]))
        # node_list = [Node(entry[0], entry[1], entry[2]) for entry in data]
        # self.session.add_all(node_list)

    @decorator_edit
    def update_node(self, old_node_id, data):
        """
        Arguments:
            old_node_id {String}
            data {Dict} -- {'node_id': , 'node_name': , 'node_ips': }
        """
        self.session.filter(Node.node_id == old_node_id).update(data)

    @decorator_edit
    def delete_entry_node(self, node_id):
        """
        Arguments:
            node_id {String}
        """
        self.session.query(Node).filter(Node.node_id == node_id).delete()

    @decorator_read
    def read_service(self):
        self.session.query(Service).all()

    @decorator_edit
    def insert_into_service(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, name_space),
                (service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, name_space),
                ...
            ]
        """
        service_list = [Service(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]) for entry in data]
        self.session.add_all(service_list)

    @decorator_edit
    def update_service(self, old_service, data):
        """
        Arguments:
            old_service {String}
            data {Dict} -- {'service_id': , 'node_id': , 'service_name': , 'service_ip': , 'service_port': , 'service_address': , 'service_tags': , 'service_kind': , 'name_space': }
        """
        self.session.query.filter(Service.service_id == old_service).update(data)

    @decorator_edit
    def delete_entry_service(self, service_id):
        """
        Arguments:
            service_id {String}
        """
        self.session.query(Service).filter(Service.service_id == service_id).delete()

    @decorator_read
    def read_nodechecks(self):
        return self.session.query(NodeChecks).all()

    @decorator_edit
    def insert_into_node_checks(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (node_name, check_id, node_id, check_name, service_name, check_type, notes, output, status),
                (node_name, check_id, node_id, check_name, service_name, check_type, notes, output, status),
                ...
            ]
        """
        node_checks_list = [NodeChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]) for entry in data]
        self.session.add_all(node_checks_list)

    @decorator_edit
    def update_node_checks(self, old_node_name, old_check_id, data):
        """
        Arguments:
            old_node_name {string}
            old_check_id {string}
            data {dict} -- {'node_name': , 'check_id': , 'node_id': , 'check_name': , 'service_name': , 'check_type': , 'notes': , 'output': , 'status': }
        """
        self.session.query(NodeChecks).filter(NodeChecks.node_name == old_node_name, NodeChecks.check_id == old_check_id).update(data)

    @decorator_edit
    def delete_entry_node_checks(self, node_name, node_id):
        """
        Arguments:
            node_name {String}
            node_id {String}
        """
        self.session.query(NodeChecks).filter(NodeChecks.node_name == node_name, NodeChecks.node_id == node_id).delete()

    @decorator_read
    def read_service_chechecks(self):
        return self.session.query(ServiceChecks).all()

    @decorator_edit
    def insert_into_service_checks(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                    (check_id, service_id, service_name, check_name, check_type, notes, output, status)
                ]
        """
        service_checks_list = [ServiceChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]) for entry in data]
        self.session.add_all(service_checks_list)

    @decorator_edit
    def update_service_checks(self, old_check_id, old_service_id, data):
        """
        Arguments:
            old_check_id {String}
            old_service_id {String}
            data {Dict} -- {'check_id': , 'service_id': , 'service_name': , 'check_name': , 'check_type': , 'notes': , 'output': , 'status': }
        """
        self.session.query(ServiceChecks).filter(ServiceChecks.check_id == old_check_id, ServiceChecks.service_id == old_service_id).update(data)

    @decorator_edit
    def delete_entry_service_checks(self, check_id, service_id):
        """
        Arguments:
            check_id {String}
            service_id {String}
        """
        self.session.query(ServiceChecks).filter(ServiceChecks.check_id == check_id, ServiceChecks.service_id == service_id).delete()