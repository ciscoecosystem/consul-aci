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
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, node_id, node_name, node_ips, created_ts=None, updated_ts=None):
        self.node_id = node_id
        self.node_name = node_name
        self.node_ips = node_ips
        self.created_ts = created_ts
        self.updated_ts = updated_ts


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
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, name_space, created_ts=None, updated_ts=None):
        self.service_id = service_id
        self.node_id = node_id
        self.service_name = service_name
        self.service_ip = service_ip
        self.service_port = service_port
        self.service_address = service_address
        self.service_tags = service_tags
        self.service_kind = service_kind
        self.name_space = name_space
        self.created_ts = created_ts
        self.updated_ts = updated_ts


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
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, node_name, check_id, node_id, check_name, service_name, check_type, notes, output, status, created_ts=None, updated_ts=None):
        self.node_name = node_name
        self.check_id = check_id
        self.node_id = node_id
        self.check_name = check_name
        self.service_name = service_name
        self.check_type = check_type
        self.notes = notes
        self.output = output
        self.status = status
        self.created_ts = created_ts
        self.updated_ts = updated_ts


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
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, check_id, service_id, service_name, check_name, check_type, notes, output, status, created_ts=None, updated_ts=None):
        self.check_id = check_id
        self.service_id = service_id
        self.service_name = service_name
        self.check_name = check_name
        self.check_type = check_type
        self.notes = notes
        self.output = output
        self.status = status
        self.created_ts = created_ts
        self.updated_ts = updated_ts


class EP(Base):
    __tablename__ = 'EP'
    mac = Column(String, primary_key=True)
    ip = Column(String, primary_key=True)
    tenant = Column(String)
    dn = Column(String, ForeignKey('EPG.dn'))
    vm_name = Column(String)
    interfaces = Column(PickleType)
    vmm_domain = Column(String)
    controller_name = Column(String)
    learning_source = Column(String)
    multicast_address = Column(String)
    encap = Column(String)
    hosting_server_name = Column(String)
    is_cep = Column(Boolean)
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)
    last_checked_ts = Column(DateTime)

    def __init__(self, mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep, created_ts=None, updated_ts=None, last_checked_ts=None):
        self.mac = mac
        self.ip = ip
        self.tenant = tenant
        self.dn = dn
        self.vm_name = vm_name
        self.interfaces = interfaces
        self.vmm_domain = vmm_domain
        self.controller_name = controller_name
        self.learning_source = learning_source
        self.multicast_address = multicast_address
        self.encap = encap
        self.hosting_server_name = hosting_server_name
        self.is_cep = is_cep
        self.created_ts = created_ts
        self.updated_ts = updated_ts
        self.last_checked_ts = last_checked_ts


class EPG(Base):
    __tablename__ = 'EPG'
    dn = Column(String, primary_key=True)
    tenant = Column(String)
    epg = Column(String)
    bd = Column(String)
    contracts = Column(PickleType)
    vrf = Column(String)
    epg_health = Column(Integer)
    app_profile = Column(String)
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)
    last_checked_ts = Column(DateTime)

    def __init__(self, dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile, created_ts, updated_ts, last_checked_ts):
        self.dn = dn
        self.tenant = tenant
        self.epg = epg
        self.bd = bd
        self.contracts = contracts
        self.vrf = vrf
        self.epg_health = epg_health
        self.app_profile = app_profile
        self.created_ts = created_ts
        self.updated_ts = updated_ts
        self.last_checked_ts = last_checked_ts

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
        for entry in data:
            self.session.add(Login(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], timestamp))

        # login_list = [Login(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], timestamp) for entry in data]
        # self.session.add_all(login_list)

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
        for entry in data:
            self.session.add(Mapping(entry[0], entry[1], entry[2], entry[3]))
        # mapping_list = [Mapping(entry[0], entry[1], entry[2], entry[3]) for entry in data]
        # self.session.add_all(mapping_list)

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
        for entry in data:
            self.session.add(Service(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]))
        # service_list = [Service(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]) for entry in data]
        # self.session.add_all(service_list)

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
        for entry in data:
            self.session.add(NodeChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]))
        # node_checks_list = [NodeChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]) for entry in data]
        # self.session.add_all(node_checks_list)

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
        for entry in data:
            self.session.add(ServiceChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]))
        # service_checks_list = [ServiceChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]) for entry in data]
        # self.session.add_all(service_checks_list)

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

    @decorator_read
    def read_EP(self):
        return self.session.query(EP).all()

    @decorator_edit
    def insert_into_EP(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep),
                (mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep),
                ...
            ]
        """
        for entry in data:
            self.session.add(EP(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10], entry[11], entry[12]))

    @decorator_edit
    def update_EP(self, old_mac, old_ip, data):
        """
        Arguments:
            old_mac {String}
            old_ip {String}
            data {Dict} -- {'mac': , 'ip': , 'tenant': , 'dn': , 'vm_name': , 'interfaces': , 'vmm_domain': , 'controller_name': , 'learning_source': , 'multicast_address': , 'encap': , 'hosting_server_name': , 'is_cep': }
        """
        self.session.filter(EP.mac == old_mac, EP.ip == old_ip).update(data)

    @decorator_edit
    def delete_entry_EP(self, mac, ip):
        """
        Arguments:
            mac {String}
            ip {String}
        """
        self.session.query(EP).filter(EP.mac == mac, EP.ip == ip).delete()

    @decorator_read
    def read_EPG(self):
        return self.session.query(EPG).all()

    @decorator_edit
    def insert_into_EPG(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile),
                (dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile),
                ...
            ]
        """
        for entry in data:
            self.session.add(EPG(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]))

    @decorator_edit
    def update_EPG(self, old_dn, data):
        """
        Arguments:
            old_dn {String}
            data {Dict} -- {'dn': , 'tenant': , 'epg': , 'bd': , 'contracts': , 'vrf': , 'epg_health': , 'app_profile': }
        """
        self.session.query(EPG.dn == old_dn).update(data)

    @decorator_edit
    def delete_entry_EPG(self, dn):
        """
        Arguments:
            dn {String}
        """
        self.session.query(EPG).filter(EPG.dn == dn).delete()