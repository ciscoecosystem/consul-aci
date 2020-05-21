import datetime
import time, json
from sqlalchemy import Column, Integer, String, ForeignKey, PickleType, update, Boolean, func, DateTime, and_
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, sessionmaker, relationship
from sqlalchemy import exists

from custom_logger import CustomLogger
from decorator import alchemy_commit_session
from decorator import alchemy_read


Base = declarative_base()
logger = CustomLogger.get_logger("/home/app/log/app.log")

class Login(Base):
    __tablename__ = 'Login'
    agent_ip = Column(String, primary_key=True)
    port = Column(Integer, primary_key=True)
    protocol = Column(String)
    token = Column(String)
    status = Column(Boolean)
    datacenter = Column(String)
    timestamp = Column(Integer)

    def __init__(self, agent_ip, port, protocol, token, status, datacenter, timestamp):
        self.agent_ip = agent_ip
        self.port = port
        self.protocol = protocol
        self.token = token
        self.status = status
        self.datacenter = datacenter
        self.timestamp = timestamp


class Mapping(Base):
    __tablename__ = 'Mapping'
    ip = Column(String, primary_key=True)
    dn = Column(String, primary_key=True)
    disabled = Column(Boolean)
    datacenter = Column(String)

    def __init__(self, ip, dn, disabled, datacenter):
        self.ip = ip
        self.dn = dn
        self.disabled = disabled
        self.datacenter = datacenter


class Node(Base):
    __tablename__ = 'Node'
    node_id = Column(String, primary_key=True)
    node_name = Column(String)
    node_ips = Column(PickleType)
    datacenter = Column(String)
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, node_id, node_name, node_ips, datacenter, created_ts=None, updated_ts=None):
        self.node_id = node_id
        self.node_name = node_name
        self.node_ips = node_ips
        self.datacenter = datacenter
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
    namespace = Column(String)
    datacenter = Column(String)
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, namespace, datacenter, created_ts=None, updated_ts=None):
        self.service_id = service_id
        self.node_id = node_id
        self.service_name = service_name
        self.service_ip = service_ip
        self.service_port = service_port
        self.service_address = service_address
        self.service_tags = service_tags
        self.service_kind = service_kind
        self.name_space = namespace
        self.datacenter = datacenter
        self.created_ts = created_ts
        self.updated_ts = updated_ts


class NodeChecks(Base):
    __tablename__ = 'NodeChecks'
    node_id = Column(String, ForeignKey('Node.node_id'), primary_key=True)
    check_id = Column(String, primary_key=True)
    node_name = Column(String)
    check_name = Column(String)
    service_name = Column(String)
    check_type = Column(String)
    notes = Column(String)
    output = Column(String)
    status = Column(String)
    created_ts = Column(DateTime)
    updated_ts = Column(DateTime)

    def __init__(self, node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status, created_ts=None, updated_ts=None):
        self.node_id = node_id
        self.check_id = check_id
        self.node_name = node_name
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

# class NodeAudit(Node):
#     __tablename__ = 'NodeAudit'
#     audit_ts = Column(DateTime)
#     audit_category = Column(String)

#     def __init__(self, node_id, node_name, node_ips, datacenter, created_ts=None, updated_ts=None, audit_ts=None, audit_category=None):
#         super().__init__(node_id, node_name, node_ips, datacenter, created_ts, updated_ts)
#         self.audit_ts = audit_ts
#         self.audit_category = audit_category


# class ServiceAudit(Service):
#     __tablename__ = 'ServiceAudit'
#     audit_ts = Column(DateTime)
#     audit_category = Column(String)

#     def __init__(self, service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, namespace, datacenter, created_ts=None, updated_ts=None, audit_ts=None, audit_category=None):
#         super().__init__(service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, namespace, datacenter, created_ts, updated_ts)
#         self.audit_ts = audit_ts
#         self.audit_category = audit_category


# class NodeChecksAudit(NodeChecks):
#     __tablename__ = 'NodeChecksAudit'
#     audit_ts = Column(DateTime)
#     audit_category = Column(String)

#     def __init__(self, node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status, created_ts=None, updated_ts=None, audit_ts=None, audit_category=None):
#         super().__init__(node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status, created_ts, updated_ts)
#         self.audit_ts = audit_ts
#         self.audit_category = audit_category


# class ServiceChecksAudit(ServiceChecks):
#     __tablename__ = 'ServiceChecksAudit'
#     audit_ts = Column(DateTime)
#     audit_category = Column(String)

#     def __init__(self, check_id, service_id, service_name, check_name, check_type, notes, output, status, created_ts=None, updated_ts=None, audit_ts=None, audit_category=None):
#         super().__init__(check_id, service_id, service_name, check_name, check_type, notes, output, status, created_ts, updated_ts)
#         self.audit_ts = audit_ts
#         self.audit_category = audit_category

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

    def __init__(self, dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile, created_ts=None, updated_ts=None, last_checked_ts=None):
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


# class EPAudit(EP):
#     __tablename__ = 'EPAudit'
#     audit_ts = Column(DateTime)
#     audit_category = Column(DateTime)

#     def __init__(self, mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep, created_ts=None, updated_ts=None, last_checked_ts=None, audit_ts=None, audit_category=None):
#         super().__init__(mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep, created_ts, updated_ts, last_checked_ts)
#         self.audit_ts = audit_ts
#         self.audit_category = audit_category


# class EPGAudit(EPG):
#     __tablename__ = 'EPGAudit'
#     audit_ts = Column(DateTime)
#     audit_category = Column(DateTime)

#     def __init__(self, dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile, created_ts=None, updated_ts=None, last_checked_ts=None, audit_ts=None, audit_category=None):
#         super().__init__(dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile, created_ts, updated_ts, last_checked_ts)
#         self.audit_ts = audit_ts
#         self.audit_category = audit_category


class Database():
    def __init__(self):
        self.engine = create_engine("sqlite:///AppD_Test.db?check_same_thread=False")

        self.metadata = Base.metadata
        session = sessionmaker(bind=self.engine)

        self.conn = self.engine.connect()
        self.conn = self.engine.connect()
        try:
            self.conn.execute("PRAGMA journal_mode = WAL")
        except Exception as ex:
            logger.exception("Exception setting journal mode to WAL : " + str(ex))

        self.session = session(bind=self.conn)


    def create_tables(self):
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


    @alchemy_read
    def read_login(self):
        return self.session.query(Login).all()


    @alchemy_commit_session
    def insert_into_login(self, data):
        """
        Arguments:
            data {List of Touple} -- [
                (agent_ip, port, protocol, token, status, datacenter),
                (agent_ip, port, protocol, token, status, datacenter),
                ...
            ]
        """
        timestamp = int(time.time())
        for entry in data:
            self.session.add(Login(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], timestamp))


    @alchemy_commit_session
    def update_login(self, old_protocol, old_agent_ip, old_port, data):
        """
        Arguments:
            old_protocol {String}
            old_ip {String}
            old_port {Integer}
            data {dict} -- {'agent_ip': ,'port': ,'protocol': ,'token' ,'status': ,'datacenter'}
        """
        self.session.query(Login).filter(Login.protocol == old_protocol, Login.agent_ip == old_agent_ip, Login.port == old_port).update(data)


    @alchemy_commit_session
    def delete_entry_login(self, agent_ip, port):
        """
        Arguments:
            agent_ip {String}
            port {Integer}
        """
        self.session.query(Login).filter(Login.agent_ip == agent_ip, Login.port == port).delete()


    @alchemy_read
    def read_mapping(self):
        return self.session.query(Mapping).all()


    @alchemy_commit_session
    def insert_into_mapping(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (ip, dn, disabled, datacenter),
                (ip, dn, disabled, datacenter),
                ...
            ]
        """
        for entry in data:
            self.session.add(Mapping(entry[0], entry[1], entry[2], entry[3]))


    @alchemy_commit_session
    def update_mapping(self, old_ip, old_dn, data):
        """
        Arguments:
            old_ip {String}
            old_dn {String}
            data {dict} -- {'ip': ,'dn': ,'disabled': ,'datacenter': }
        """
        self.session.query(Mapping).filter(Mapping.ip == old_ip, Mapping.dn == old_dn).update(data)


    @alchemy_commit_session
    def delete_entry_mapping(self, ip, dn):
        """
        Arguments:
            ip {String}
            dn {String}
        """
        self.session.query(Mapping).filter(Mapping.ip == ip, Mapping.dn == dn).delete()


    @alchemy_read
    def read_node(self):
        return self.session.query(Node).all()


    @alchemy_commit_session
    def insert_into_node(self, data):
        """
        Arguments:
            data {list of Tuple} -- [
                (node_id, node_name, node_ips, datacenter),
                (node_id, node_name, node_ips, datacenter),
                ...
            ]
        """
        for entry in data:
            self.session.add(Node(entry[0], entry[1], entry[2], entry[3]))


    @alchemy_commit_session
    def update_node(self, old_node_id, data):
        """
        Arguments:
            old_node_id {String}
            data {Dict} -- {'node_id': , 'node_name': , 'node_ips': , 'datacenter': }
        """
        self.session.query(Node).filter(Node.node_id == old_node_id).update(data)


    @alchemy_commit_session
    def delete_entry_node(self, node_id):
        """
        Arguments:
            node_id {String}
        """
        self.session.query(Node).filter(Node.node_id == node_id).delete()


    @alchemy_read
    def read_service(self):
        self.session.query(Service).all()


    @alchemy_commit_session
    def insert_into_service(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, name_space, datacenter),
                (service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, name_space, datacenter),
                ...
            ]
        """
        for entry in data:
            self.session.add(Service(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9]))


    @alchemy_commit_session
    def update_service(self, old_service_id, data):
        """
        Arguments:
            old_service {String}
            data {Dict} -- {'service_id': , 'node_id': , 'service_name': , 'service_ip': , 'service_port': , 'service_address': , 'service_tags': , 'service_kind': , 'name_space': , 'datacenter': }
        """
        self.session.query.filter(Service.service_id == old_service_id).update(data)


    @alchemy_commit_session
    def delete_entry_service(self, service_id):
        """
        Arguments:
            service_id {String}
        """
        self.session.query(Service).filter(Service.service_id == service_id).delete()


    @alchemy_read
    def read_nodechecks(self):
        return self.session.query(NodeChecks).all()


    @alchemy_commit_session
    def insert_into_node_checks(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                (node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status),
                (node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status),
                ...
            ]
        """
        for entry in data:
            self.session.add(NodeChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]))


    @alchemy_commit_session
    def update_node_checks(self, old_node_id, old_check_id, data):
        """
        Arguments:
            old_node_name {string}
            old_check_id {string}
            data {dict} -- {'node_id': , 'check_id': , 'node_name': , 'check_name': , 'service_name': , 'check_type': , 'notes': , 'output': , 'status': }
        """
        self.session.query(NodeChecks).filter(NodeChecks.node_id == old_node_id, NodeChecks.check_id == old_check_id).update(data)


    @alchemy_commit_session
    def delete_entry_node_checks(self, node_id, check_id):
        """
        Arguments:
            node_id {String}
            check_id {String}
        """
        self.session.query(NodeChecks).filter(NodeChecks.node_id == node_id, NodeChecks.check_id == check_id).delete()


    @alchemy_read
    def read_service_chechecks(self):
        return self.session.query(ServiceChecks).all()


    @alchemy_commit_session
    def insert_into_service_checks(self, data):
        """
        Arguments:
            data {List of Tuple} -- [
                    (check_id, service_id, service_name, check_name, check_type, notes, output, status)
                ]
        """
        for entry in data:
            self.session.add(ServiceChecks(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]))


    @alchemy_commit_session
    def update_service_checks(self, old_check_id, old_service_id, data):
        """
        Arguments:
            old_check_id {String}
            old_service_id {String}
            data {Dict} -- {'check_id': , 'service_id': , 'service_name': , 'check_name': , 'check_type': , 'notes': , 'output': , 'status': }
        """
        self.session.query(ServiceChecks).filter(ServiceChecks.check_id == old_check_id, ServiceChecks.service_id == old_service_id).update(data)


    @alchemy_commit_session
    def delete_entry_service_checks(self, check_id, service_id):
        """
        Arguments:
            check_id {String}
            service_id {String}
        """
        self.session.query(ServiceChecks).filter(ServiceChecks.check_id == check_id, ServiceChecks.service_id == service_id).delete()


    @alchemy_read
    def read_ep(self):
        return self.session.query(EP).all()


    @alchemy_commit_session
    def insert_into_ep(self, data):
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


    @alchemy_commit_session
    def update_ep(self, old_mac, old_ip, data):
        """
        Arguments:
            old_mac {String}
            old_ip {String}
            data {Dict} -- {'mac': , 'ip': , 'tenant': , 'dn': , 'vm_name': , 'interfaces': , 'vmm_domain': , 'controller_name': , 'learning_source': , 'multicast_address': , 'encap': , 'hosting_server_name': , 'is_cep': }
        """
        self.session.query(EP).filter(EP.mac == old_mac, EP.ip == old_ip).update(data)


    @alchemy_commit_session
    def delete_entry_ep(self, mac, ip):
        """
        Arguments:
            mac {String}
            ip {String}
        """
        self.session.query(EP).filter(EP.mac == mac, EP.ip == ip).delete()


    @alchemy_read
    def read_epg(self):
        return self.session.query(EPG).all()


    @alchemy_commit_session
    def insert_into_epg(self, data):
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


    @alchemy_commit_session
    def update_epg(self, old_dn, data):
        """
        Arguments:
            old_dn {String}
            data {Dict} -- {'dn': , 'tenant': , 'epg': , 'bd': , 'contracts': , 'vrf': , 'epg_health': , 'app_profile': }
        """
        self.session.query(EPG).filter(EPG.dn == old_dn).update(data)


    @alchemy_commit_session
    def delete_entry_epg(self, dn):
        """
        Arguments:
            dn {String}
        """
        self.session.query(EPG).filter(EPG.dn == dn).delete()


    # @alchemy_read
    # def read_node_audit(self):
    #     return self.session.query(NodeAudit).all()


    # @alchemy_commit_session
    # def insert_into_node_audit(self, data):
    #     """
    #     Arguments:
    #         data {List of Tuple} -- [
    #             (node_id, node_name, node_ips, datacenter),
    #             (node_id, node_name, node_ips, datacenter),
    #             ...
    #         ]
    #     """
    #     for entry in data:
    #         self.session.add(NodeAudit(entry[0], entry[1], entry[2], entry[3]))


    # @alchemy_commit_session
    # def update_node_audit(self, old_node_id, data):
    #     """
    #     Arguments:
    #         old_node_id {String}
    #         data {Dict} -- {'node_id': , 'node_name': , 'node_ips': , 'datacenter': }
    #     """
    #     self.session.query(NodeAudit).filter(NodeAudit.node_id == old_node_id).update(data)


    # @alchemy_commit_session
    # def delete_entry_node_audit(self, node_id):
    #     """
    #     Arguments:
    #         node_id {String}
    #     """
    #     self.session.query(NodeAudit).filter(NodeAudit.node_id == node_id).delete()


    # @alchemy_read
    # def read_service_audit(self):
    #     return self.session.query(ServiceAudit).all()


    # @alchemy_commit_session
    # def insert_into_service_audit(self, data):
    #     """
    #     Arguments:
    #         data {List of Tuple} -- [
    #             (service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, namespace, datacenter),
    #             (service_id, node_id, service_name, service_ip, service_port, service_address, service_tags, service_kind, namespace, datacenter),
    #             ...
    #         ]
    #     """
    #     for entry in data:
    #         self.session.add(ServiceAudit(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9]))


    # @alchemy_commit_session
    # def update_service_audit(self, old_service_id, data):
    #     """
    #     Arguments:
    #         old_service_id {String}
    #         data {Dict} -- {'service_id': , 'node_id':, 'service_name': , 'service_ip': , 'service_port': , 'service_address': , 'service_tags': , 'service_kind': , 'namespace': , 'datacenter': }
    #     """
    #     self.session.query(ServiceAudit).filter(ServiceAudit.service_id == old_service_id).update(data)


    # @alchemy_commit_session
    # def delete_entry_service_audit(self, service_id):
    #     """
    #     Arguments:
    #         service_id {String}
    #     """
    #     self.session.query(ServiceAudit).filter(ServiceAudit.service_id == service_id).delete()


    # @alchemy_read
    # def read_node_checks_audit(self):
    #     return self.session.query(NodeChecksAudit).all()


    # @alchemy_commit_session
    # def insert_into_node_checks_audit(self, data):
    #     """
    #     Arguments:
    #         data {List of Tuple} -- [
    #             (node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status),
    #             (node_id, check_id, node_name, check_name, service_name, check_type, notes, output, status),
    #             ...
    #         ]
    #     """
    #     for entry in data:
    #         self.session.add(NodeChecksAudit(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8]))

    
    # @alchemy_commit_session
    # def update_node_checks_audit(self, old_node_id, old_check_id, data):
    #     """
    #     Arguments:
    #         old_node_id {String}
    #         old_check_id {String}
    #         data {Dict} -- {'node_id': , 'check_id': , 'node_name': , 'check_name': , 'service_name': , 'check_type': , 'notes': , 'output': , 'status': }
    #     """
    #     self.session.query(NodeChecksAudit).filter(NodeChecksAudit.node_id == old_node_id, NodeChecksAudit.check_id == old_check_id)


    # @alchemy_commit_session
    # def delete_entry_node_checks_audit(self, node_id, check_id):
    #     """
    #     Arguments:
    #         node_id {String}
    #         check_id {String}
    #     """
    #     self.session.query(NodeChecksAudit).filter(NodeChecksAudit.node_id == node_id, NodeChecksAudit.check_id == check_id).delete()


    # @alchemy_read
    # def read_service_checks_audit(self):
    #     return self.session.query(ServiceChecksAudit).all()


    # @alchemy_commit_session
    # def insert_into_service_checks_audit(self, data):
    #     """
    #     Arguments:
    #         data {List of Tuple} -- [
    #             (check_id, service_id, service_name, check_name, check_type, notes, output, status),
    #             (check_id, service_id, service_name, check_name, check_type, notes, output, status),
    #             ...
    #         ]
    #     """
    #     for entry in data:
    #         self.session.add(ServiceChecksAudit(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]))

    
    # @alchemy_commit_session
    # def update_service_checks_audit(self, old_check_id, old_service_id, data):
    #     """
    #     Arguments:
    #         old_check_id {String}
    #         old_service_id {String}
    #         data {Dict} -- {'check_id': , 'service_id': , 'service_name': , 'check_name': , 'check_type': , 'notes': , 'output': , 'status': }
    #     """
    #     self.session.query(ServiceChecksAudit).filter(ServiceChecksAudit.check_id == old_check_id, ServiceChecksAudit.service_id == old_service_id).update(data)

    
    # @alchemy_commit_session
    # def delete_entry_service_checks_audit(self, check_id, service_id):
    #     """
    #     Arguments:
    #         check_id {String}
    #         service_id {String}
    #     """
    #     self.session.query(ServiceChecksAudit).filter(ServiceChecksAudit.check_id == check_id, ServiceChecksAudit.service_id == service_id).delete()


    # @alchemy_read
    # def read_ep_audit(self):
    #     return self.session.query(EPAudit).all()


    # @alchemy_commit_session
    # def insert_into_ep_audit(self, data):
    #     """
    #     Arguments:
    #         data {List of Tuple} -- [
    #             (mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep),
    #             (mac, ip, tenant, dn, vm_name, interfaces, vmm_domain, controller_name, learning_source, multicast_address, encap, hosting_server_name, is_cep),
    #             ...
    #         ]
    #     """
    #     for entry in data:
    #         self.session.add(EPAudit(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7], entry[8], entry[9], entry[10], entry[11], entry[12]))


    # @alchemy_commit_session
    # def update_ep_audit(self, old_mac, old_ip, data):
    #     """
    #     Arguments:
    #         old_mac {String}
    #         old_ip {String}
    #         data {Dict} -- {'mac': , 'ip': , 'tenant': , 'dn': , 'vm_name': , 'interfaces': , 'vmm_domain': , 'controller_name': , 'learning_source': , 'multicast_address': , 'encap': , 'hosting_server_name': , 'is_cep': }
    #     """
    #     self.session.query(EPAudit).filter(EPAudit.mac == old_mac, EPAudit.ip == old_ip).update(data)


    # @alchemy_commit_session
    # def delete_entry_ep_audit(self, mac, ip):
    #     """
    #     Arguments:
    #         mac {String}
    #         ip {String}
    #     """
    #     self.session.query(EPAudit).filter(EPAudit.mac == mac, EPAudit.ip == ip).delete()


    # @alchemy_read
    # def read_epg_audit(self):
    #     return self.session.query(EPGAudit).all()


    # @alchemy_commit_session
    # def insert_into_epg_audit(self, data):
    #     """
    #     Arguments:
    #         data {List of Tuple} -- [
    #             (dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile),
    #             (dn, tenant, epg, bd, contracts, vrf, epg_health, app_profile),
    #             ...
    #         ]
    #     """
    #     for entry in data:
    #         self.session.add(EPGAudit(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7]))


    # @alchemy_commit_session
    # def update_epg_audit(self, old_dn, data):
    #     """
    #     Arguments:
    #         old_dn {String}
    #         data {Dict} -- {'dn': , 'tenant': , 'epg': , 'bd': , 'contracts': , 'vrf': , 'epg_health': , 'app_profile': }
    #     """
    #     self.session.query(EPGAudit).filter(EPGAudit.dn == old_dn).update(data)


    # @alchemy_commit_session
    # def delete_entry_epg_audit(self, dn):
    #     """
    #     Arguments:
    #         dn {String}
    #     """
    #     self.session.query(EPGAudit).filter(EPGAudit.dn == dn).delete()
