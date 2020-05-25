from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, String, MetaData, PickleType, DateTime
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.sql import select, text


class Database:
    table_field_meta = {
        'login': ['agent_ip', 'port', 'protocol', 'token', 'status', 'datacenter'],
        'mapping': ['ip', 'dn', 'disabled', 'datacenter'],
        'node': ['node_id', 'node_name', 'node_ips', 'datacenter', 'created_ts', 'updated_ts', 'last_checked_ts'],
        'service': ['service_id', 'node_id', 'service_name', 'service_ip', 'service_port', 'service_address', 'service_tags', 'service_kind', 'namespace', 'datacenter', 'created_ts', 'updated_ts', 'last_checked_ts'],
        'nodechecks': ['check_id', 'node_id', 'node_name', 'check_name', 'service_name', 'check_type', 'notes', 'output', 'status', 'created_ts', 'updated_ts', 'last_checked_ts'],
        'servicechecks': ['check_id', 'service_id', 'service_name', 'check_name', 'check_type', 'notes', 'output', 'status', 'created_ts', 'updated_ts', 'last_checked_ts'],
        'ep': ['mac', 'ip', 'tenant',  'dn', 'vm_name', 'interfaces', 'vmm_domain', 'controller_name', 'learning_source', 'multicast_address', 'encap', 'hosting_server_name', 'is_cep', 'created_ts', 'updated_ts', 'last_checked_ts'],
        'epg': ['dn', 'tenant',  'epg', 'bd', 'contracts', 'vrf', 'epg_health', 'app_profile', 'created_ts', 'updated_ts', 'last_checked_ts']
    }
    table_obj_meta = dict()
    table_pkey_meta = dict()

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
            self.table_obj_meta.update({
                'login': self.login,
                'mapping': self.mapping,
                'node': self.node,
                'service': self.service,
                'nodechecks': self.nodechecks,
                'servicechecks': self.servicechecks,
                'ep': self.ep,
                'epg': self.epg,
                'nodeaudit': self.nodeaudit,
                'serviceaudit': self.serviceaudit,
                'nodechecksaudit': self.nodechecksaudit,
                'servicechecksaudit': self.servicechecksaudit,
                'epaudit': self.epaudit,
                'epgaudit': self.epgaudit
            })
            self.table_pkey_meta.update({
                'login': {'agent_ip': self.login.c.agent_ip, 'port': self.login.c.port},
                'mapping': {'ip': self.mapping.c.ip, 'dn': self.mapping.c.dn},
                'node': {'node_id': self.node.c.node_id},
                'service': {'service_id': self.service.c.service_id},
                'nodechecks': {'check_id': self.nodechecks.c.check_id, 'node_id': self.nodechecks.c.node_id},
                'servicechecks': {'check_id': self.servicechecks.c.check_id, 'service_id': self.servicechecks.c.service_id},
                'ep': {'mac': self.ep.c.mac, 'ip': self.ep.c.ip},
                'epg': {'dn': self.epg.c.dn}
            })
        except Exception as e:
            pass
            print "Error in table creation:", e

    def insert_into_table(self, table_name, field_values):
        try:
            ins = None
            table_name = table_name.lower()
            ins = self.table_obj_meta[table_name].insert().values(field_values)
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
                table_obj = self.table_obj_meta[table_name]
                select_query = table_obj.select()
                for key in primary_key:
                    select_query = select_query.where(
                        self.table_pkey_meta[table_name][key] == primary_key[key])
            else:
                select_query = self.table_obj_meta[table_name].select()

            if select_query != None:
                result = self.conn.execute(select_query)
                return result
        except Exception as e:
            pass
            print "Error in select:", e
        return None

    def update_into_table(self, table_name, primary_key, new_record_dict):
        try:
            table_name = table_name.lower()
            table_obj = self.table_obj_meta[table_name]
            update_query = table_obj.update()
            for key in primary_key:
                update_query = update_query.where(
                    self.table_pkey_meta[table_name][key] == primary_key[key])
            update_query = update_query.values(new_record_dict)
            self.conn.execute(update_query)
            return True
        except Exception as e:
            pass
            print "Error in update:", e
        return False

    def delete_from_table(self, table_name, primary_key={}):
        try:
            table_name = table_name.lower()
            if primary_key:
                table_obj = self.table_obj_meta[table_name]
                delete_query = table_obj.delete()
                for key in primary_key:
                    delete_query = delete_query.where(
                        self.table_pkey_meta[table_name][key] == primary_key[key])
            else:
                delete_query = self.table_obj_meta[table_name].delete()
            self.conn.execute(delete_query)
            return True
        except Exception as e:
            pass
            print "Error in delete:", e
        return False

    def insert_and_update(self, table_name, new_record, primary_key={}):
        table_name = table_name.lower()
        if primary_key:
            old_data = self.select_from_table(table_name, primary_key)
            if old_data:
                old_data = old_data.fetchone()
                if old_data:
                    new_record_dict = dict()
                    index = []
                    for i in range(len(old_data)):
                        if old_data[i] != new_record[i]:
                            index.append(i)
                    field_names = [self.table_field_meta[table_name][i]
                                   for i in index]
                    new_record_dict = dict()
                    for i in range(len(field_names)):
                        new_record_dict[field_names[i]] = new_record[index[i]]
                    # TODO: call audit
                    self.update_into_table(
                        table_name, primary_key, new_record_dict)
                else:
                    self.insert_into_table(table_name, new_record)
            else:
                return False
        else:
            self.insert_into_table(table_name, new_record)
        return True
