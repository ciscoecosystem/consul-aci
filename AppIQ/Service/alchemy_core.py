from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, Integer, String, MetaData, PickleType, Boolean, DateTime,exists
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.sql import select, text


class Database:
    def __init__(self, database_name):
        try:
            self.engine = create_engine(database_name)
            self.conn = self.engine.connect()
        except Exception as e:
            print "Error in database connection:", e

    def create_tables(self):
        metadata = MetaData()

        self.login = Table('Login', metadata,
                           Column('agent_ip', String, primary_key=True),
                           Column('port', String, primary_key=True),
                           Column('protocol', String),
                           Column('token', String),
                           Column('status', String),
                           Column('datacenter', String)
                           )
        self.mapping = Table('Mapping', metadata,
                             Column('ip', String, primary_key=True),
                             Column('dn', String, primary_key=True),
                             Column('disabled', String),
                             Column('datacenter', String)
                             )

        self.node = Table('Node', metadata,
                          Column('node_id', String, primary_key=True),
                          Column('node_name', String),
                          Column('node_ips', PickleType),
                          Column('datacenter', String),
                          Column('created_ts', DateTime),
                          Column('updated_ts', DateTime),
                          Column('last_checked_ts', DateTime)
                          )

        self.service = Table('Service', metadata,
                             Column('service_id', String, primary_key=True),
                             Column('node_id', String),
                             Column('service_name', String),
                             Column('service_ip', String),
                             Column('service_port', String),
                             Column('service_address', String),
                             Column('service_tags', PickleType),
                             Column('service_kind', String),
                             Column('namespace', String),
                             Column('datacenter', String),
                             Column('created_ts', DateTime),
                             Column('updated_ts', DateTime),
                             Column('last_checked_ts', DateTime)
                             )

        self.nodechecks = Table('NodeChecks', metadata,
                                Column('check_id', String, primary_key=True),
                                Column('node_id', String, ForeignKey(
                                    self.node.c.node_id), primary_key=True),
                                Column('node_name', String),
                                Column('check_name', String),
                                Column('service_name', String),
                                Column('type', String),
                                Column('notes', String),
                                Column('output', String),
                                Column('status', PickleType),
                                Column('created_ts', DateTime),
                                Column('updated_ts', DateTime),
                                Column('last_checked_ts', DateTime)
                                )

        self.servicechecks = Table('ServiceChecks', metadata,
                                   Column('check_id', String,
                                          primary_key=True),
                                   Column('service_id', String, ForeignKey(
                                       self.service.c.service_id), primary_key=True),
                                   Column('service_name', String),
                                   Column('name', String),
                                   Column('type', String),
                                   Column('notes', String),
                                   Column('output', String),
                                   Column('status', PickleType),
                                   Column('created_ts', DateTime),
                                   Column('updated_ts', DateTime),
                                   Column('last_checked_ts', DateTime)
                                   )

        self.ep = Table('EP', metadata,
                        Column('tenant_id', String),
                        Column('mac', String, primary_key=True),
                        Column('ip', String, primary_key=True),
                        Column('dn', String),
                        Column('vm_name', String),
                        Column('interfaces', PickleType),
                        Column('vmm_domain', String),
                        Column('controller_name', String),
                        Column('learning_source', String),
                        Column('multicast_address', String),
                        Column('encap', String),
                        Column('hosting_server_name', String),
                        Column('is_cep', String),
                        Column('created_ts', DateTime),
                        Column('updated_ts', DateTime),
                        Column('last_checked_ts', DateTime)
                        )

        self.epg = Table('EPG', metadata,
                         Column('tenant_id', String),
                         Column('dn', String, primary_key=True),
                         Column('EPG', String),
                         Column('BD', String),
                         Column('contracts', PickleType),
                         Column('VRF', String),
                         Column('epg_health', String),
                         Column('app_profile', String),
                         Column('created_ts', DateTime),
                         Column('updated_ts', DateTime),
                         Column('last_checked_ts', DateTime)
                         )
        #####################################################
        self.nodeaudit = Table('NodeAudit', metadata,
                               Column('node_id', String),
                               Column('node_name', String),
                               Column('node_ips', PickleType),
                               Column('datacenter', String),
                               Column('created_ts', DateTime),
                               Column('updated_ts', DateTime),
                               Column('last_checked_ts', DateTime),
                               Column('audit_ts', DateTime),
                               Column('audit_category', PickleType)
                               )

        self.serviceaudit = Table('ServiceAudit', metadata,
                                  Column('service_id', String),
                                  Column('node_id', String),
                                  Column('service_name', String),
                                  Column('service_ip', String),
                                  Column('service_port', String),
                                  Column('service_address', String),
                                  Column('service_tags', PickleType),
                                  Column('service_kind', String),
                                  Column('namespace', String),
                                  Column('datacenter', String),
                                  Column('created_ts', DateTime),
                                  Column('updated_ts', DateTime),
                                  Column('last_checked_ts', DateTime),
                                  Column('audit_ts', DateTime),
                                  Column('audit_category', PickleType)
                                  )

        self.nodechecksaudit = Table('NodeChecksAudit', metadata,
                                     Column('check_id', String),
                                     Column('node_id', String),
                                     Column('node_name', String),
                                     Column('check_name', String),
                                     Column('service_name', String),
                                     Column('type', String),
                                     Column('notes', String),
                                     Column('output', String),
                                     Column('status', PickleType),
                                     Column('created_ts', DateTime),
                                     Column('updated_ts', DateTime),
                                     Column('last_checked_ts', DateTime),
                                     Column('audit_ts', DateTime),
                                     Column('audit_category', PickleType)
                                     )

        self.servicechecksaudit = Table('ServiceChecksAudit', metadata,
                                        Column('check_id', String),
                                        Column('service_id', String),
                                        Column('service_name', String),
                                        Column('name', String),
                                        Column('type', String),
                                        Column('notes', String),
                                        Column('output', String),
                                        Column('status', PickleType),
                                        Column('created_ts', DateTime),
                                        Column('updated_ts', DateTime),
                                        Column('last_checked_ts', DateTime),
                                        Column('audit_ts', DateTime),
                                        Column('audit_category', PickleType)
                                        )

        self.epaudit = Table('EPAudit', metadata,
                             Column('tenant_id', String),
                             Column('mac', String),
                             Column('ip', String),
                             Column('dn', String),
                             Column('vm_name', String),
                             Column('interfaces', PickleType),
                             Column('vmm_domain', String),
                             Column('controller_name', String),
                             Column('learning_source', String),
                             Column('multicast_address', String),
                             Column('encap', String),
                             Column('hosting_server_name', String),
                             Column('is_cep', String),
                             Column('created_ts', DateTime),
                             Column('updated_ts', DateTime),
                             Column('last_checked_ts', DateTime),
                             Column('audit_ts', DateTime),
                             Column('audit_category', PickleType)
                             )

        self.epgaudit = Table('EPGAudit', metadata,
                              Column('tenant_id', String),
                              Column('dn', String, primary_key=True),
                              Column('EPG', String),
                              Column('BD', String),
                              Column('contracts', PickleType),
                              Column('VRF', String),
                              Column('epg_health', String),
                              Column('app_profile', String),
                              Column('created_ts', DateTime),
                              Column('updated_ts', DateTime),
                              Column('last_checked_ts', DateTime),
                              Column('audit_ts', DateTime),
                              Column('audit_category', PickleType)
                              )

        try:
            metadata.create_all(self.engine)
        except Exception as e:
            pass
            print "Error in table creation:", e

    def insert_into_table(self, table_name, *args):
        try:
            ins = None
            table_name = table_name.lower()
            if table_name == "login":
                ins = self.login.insert().values(args)
            elif table_name == "mapping":
                ins = self.mapping.insert().values(args)
            elif table_name == "node":
                ins = self.node.insert().values(args)
            elif table_name == "service":
                ins = self.service.insert().values(args)
            elif table_name == "nodechecks":
                ins = self.nodechecks.insert().values(args)
            elif table_name == "servicechecks":
                ins = self.servicechecks.insert().values(args)
            elif table_name == "ep":
                ins = self.ep.insert().values(args)
            elif table_name == "epg":
                ins = self.epg.insert().values(args)
            elif table_name == "nodeaudit":
                ins = self.nodeaudit.insert().values(args)
            elif table_name == "serviceaudit":
                ins = self.serviceaudit.insert().values(args)
            elif table_name == "nodechecksaudit":
                ins = self.nodechecksaudit.insert().values(args)
            elif table_name == "servicechecksaudit":
                ins = self.servicechecksaudit.insert().values(args)
            elif table_name == "epaudit":
                ins = self.epaudit.insert().values(args)
            elif table_name == "epgaudit":
                ins = self.epgaudit.insert().values(args)
            if ins != None:
                self.conn.execute(ins)
                return True
        except Exception as e:
            pass
            # print "Error in data insertion:",e
        return False

    def select_from_table(self, table_name, primary_key={}):
        try:
            select_query = None
            table_name = table_name.lower()
            if primary_key:
                if table_name == "login":
                    select_query = self.login.select().where(self.login.c.agent_ip ==
                                                             primary_key['agent_ip']).where(self.login.c.port == primary_key['port'])
                elif table_name == "mapping":
                    select_query = self.mapping.select().where(
                        self.mapping.c.ip == primary_key['ip']).where(self.mapping.c.dn == primary_key['dn'])
                elif table_name == "node":
                    select_query = self.node.select().where(
                        self.node.c.node_id == primary_key['node_id'])
                elif table_name == "service":
                    select_query = self.service.select().where(
                        self.service.c.service_id == primary_key['service_id'])
                elif table_name == "nodechecks":
                    select_query = self.nodechecks.select().where(self.nodechecks.c.check_id ==
                                                                  primary_key['check_id']).where(self.nodechecks.c.node_id == primary_key['node_id'])
                elif table_name == "servicechecks":
                    select_query = self.servicechecks.select().where(self.servicechecks.c.check_id ==
                                                                     primary_key['check_id']).where(self.servicechecks.c.service_id == primary_key['service_id'])
                elif table_name == "ep":
                    select_query = self.ep.select().where(
                        self.ep.c.mac == primary_key['mac']).where(self.ep.c.ip == primary_key['ip'])
                elif table_name == "epg":
                    select_query = self.epg.select().where(
                        self.epg.c.dn == primary_key['dn'])
            else:
                if table_name == "login":
                    select_query = self.login.select()
                elif table_name == "mapping":
                    select_query = self.mapping.select()
                elif table_name == "node":
                    select_query = self.node.select()
                elif table_name == "service":
                    select_query = self.service.select()
                elif table_name == "nodechecks":
                    select_query = self.nodechecks.select()
                elif table_name == "servicechecks":
                    select_query = self.servicechecks.select()
                elif table_name == "ep":
                    select_query = self.ep.select()
                elif table_name == "epg":
                    select_query = self.epg.select()
                elif table_name == "nodeaudit":
                    select_query = self.nodeaudit.select()
                elif table_name == "serviceaudit":
                    select_query = self.serviceaudit.select()
                elif table_name == "nodechecksaudit":
                    select_query = self.nodechecksaudit.select()
                elif table_name == "servicechecksaudit":
                    select_query = self.servicechecksaudit.select()
                elif table_name == "epaudit":
                    select_query = self.epaudit.select()
                elif table_name == "epgaudit":
                    select_query = self.epgaudit.select()
            if select_query != None:
                result = self.conn.execute(select_query)
                return result
        except Exception as e:
            pass
            print "Error in select:", e
        return None

    def update_into_table(self, table_name, primary_key, new_record_dict):
        try:
            update_query = None
            table_name = table_name.lower()
            if table_name == "login":
                update_query = self.login.update().where(self.login.c.agent_ip ==
                                                         primary_key['agent_ip']).where(self.login.c.port == primary_key['port']).values(new_record_dict)
            elif table_name == "mapping":
                update_query = self.mapping.update().where(
                    self.mapping.c.ip == primary_key['ip']).where(self.mapping.c.dn == primary_key['dn']).values(new_record_dict)
            elif table_name == "node":
                update_query = self.node.update().where(
                    self.node.c.node_id == primary_key['node_id']).values(new_record_dict)
            elif table_name == "service":
                update_query = self.service.update().where(
                    self.service.c.service_id == primary_key['service_id']).values(new_record_dict)
            elif table_name == "nodechecks":
                update_query = self.nodechecks.update().where(self.nodechecks.c.check_id ==
                                                              primary_key['check_id']).where(self.nodechecks.c.node_id == primary_key['node_id']).values(new_record_dict)
            elif table_name == "servicechecks":
                update_query = self.servicechecks.update().where(self.servicechecks.c.check_id ==
                                                                 primary_key['check_id']).where(self.servicechecks.c.service_id == primary_key['service_id']).values(new_record_dict)
            elif table_name == "ep":
                update_query = self.ep.update().where(
                    self.ep.c.mac == primary_key['mac']).where(self.ep.c.ip == primary_key['ip']).values(new_record_dict)
            elif table_name == "epg":
                update_query = self.epg.update().where(
                    self.epg.c.dn == primary_key['dn']).values(new_record_dict)
            if update_query != None:
                self.conn.execute(update_query)
                return True
        except Exception as e:
            pass
            print "Error in update:", e
        return False

    def delete_from_table(self, table_name, primary_key={}):
        try:
            delete_query = None
            table_name = table_name.lower()
            if primary_key:
                if table_name == "login":
                    delete_query = self.login.delete().where(self.login.c.agent_ip ==
                                                             primary_key['agent_ip']).where(self.login.c.port == primary_key['port'])
                elif table_name == "mapping":
                    delete_query = self.mapping.delete().where(
                        self.mapping.c.ip == primary_key['ip']).where(self.mapping.c.dn == primary_key['dn'])
                elif table_name == "node":
                    delete_query = self.node.delete().where(
                        self.node.c.node_id == primary_key['node_id'])
                elif table_name == "service":
                    delete_query = self.service.delete().where(
                        self.service.c.service_id == primary_key['service_id'])
                elif table_name == "nodechecks":
                    delete_query = self.nodechecks.delete().where(self.nodechecks.c.check_id ==
                                                                  primary_key['check_id']).where(self.nodechecks.c.node_id == primary_key['node_id'])
                elif table_name == "servicechecks":
                    delete_query = self.servicechecks.delete().where(self.servicechecks.c.check_id ==
                                                                     primary_key['check_id']).where(self.servicechecks.c.service_id == primary_key['service_id'])
                elif table_name == "ep":
                    delete_query = self.ep.delete().where(
                        self.ep.c.mac == primary_key['mac']).where(self.ep.c.ip == primary_key['ip'])
                elif table_name == "epg":
                    delete_query = self.epg.delete().where(
                        self.epg.c.dn == primary_key['dn'])
            else:
                if table_name == "login":
                    delete_query = self.login.delete()
                elif table_name == "mapping":
                    delete_query = self.mapping.delete()
                elif table_name == "node":
                    delete_query = self.node.delete()
                elif table_name == "service":
                    delete_query = self.service.delete()
                elif table_name == "nodechecks":
                    delete_query = self.nodechecks.delete()
                elif table_name == "servicechecks":
                    delete_query = self.servicechecks.delete()
                elif table_name == "ep":
                    delete_query = self.ep.delete()
                elif table_name == "epg":
                    delete_query = self.epg.delete()
            if delete_query != None:
                self.conn.execute(delete_query)
                return True
        except Exception as e:
            pass
            print "Error in delete:", e
        return False

    def insert_and_update(self, table_name, new_record, primary_key={}):
        if primary_key:
            old_data = self.select_from_table(table_name, primary_key)
            if old_data:
                pass
            else:
                self.insert_int_table(table_name,*new_record)
        else:
            self.insert_into_table(table_name, *new_record)
