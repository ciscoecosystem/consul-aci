from sqlalchemy import create_engine
from sqlalchemy import Table, Column, ForeignKey, String, MetaData, PickleType, DateTime, Boolean, Integer
from datetime import datetime
from sqlalchemy.sql import select
from sqlalchemy.interfaces import PoolListener

from custom_logger import CustomLogger

logger = CustomLogger.get_logger("/home/app/log/app.log")

DATABASE_NAME = 'sqlite:////home/app/data/ConsulDatabase.db'


class MyListener(PoolListener):
    """ MyListner class to use database in WAL mode """
    def connect(self, dbapi_con, con_record):
        dbapi_con.execute('pragma journal_mode=WAL')


class Database:
    """Database class with all db functionalities"""

    LOGIN_TABLE_NAME = 'login'
    MAPPING_TABLE_NAME = 'mapping'
    NODE_TABLE_NAME = 'node'
    SERVICE_TABLE_NAME = 'service'
    NODECHECKS_TABLE_NAME = 'nodechecks'
    SERVICECHECKS_TABLE_NAME = 'servicechecks'
    EP_TABLE_NAME = 'ep'
    EPG_TABLE_NAME = 'epg'
    NODEAUDIT_TABLE_NAME = 'nodeaudit'
    SERVICEAUDIT_TABLE_NAME = 'serviceaudit'
    NODECHECKSAUDIT_TABLE_NAME = 'nodechecksaudit'
    SERVICECHECKSAUDIT_TABLE_NAME = 'servicechecksaudit'
    EPAUDIT_TABLE_NAME = 'epaudit'
    EPGAUDIT_TABLE_NAME = 'epgaudit'
    TENANT_TABLE_NAME = 'tenant'
    POLLING_TABLE_NAME = 'polling'
    VRF_TABLE_NAME = 'vrf'

    SCHEMA_DICT = {
        VRF_TABLE_NAME: [
            'vrf_dn',
            'created_ts'
        ],

        LOGIN_TABLE_NAME: [
            'agent_ip',
            'port',
            'protocol',
            'token',
            'status',
            'datacenter',
            'tenant',
            'vrf_dn'
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        MAPPING_TABLE_NAME: [
            'ip',
            'dn',
            'datacenter',
            'enabled',
            'ap',
            'bd',
            'epg',
            'vrf',
            'tenant',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        NODE_TABLE_NAME: [
            'node_id',
            'node_name',
            'node_ip',
            'datacenter',
            'agents',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        SERVICE_TABLE_NAME: [
            'service_id',
            'node_id',
            'service_name',
            'service_ip',
            'service_port',
            'service_address',
            'service_tags',
            'service_kind',
            'namespace',
            'datacenter',
            'agents',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        NODECHECKS_TABLE_NAME: [
            'check_id',
            'node_id',
            'node_name',
            'check_name',
            'service_name',
            'type',
            'notes',
            'output',
            'status',
            'agents',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        SERVICECHECKS_TABLE_NAME: [
            'check_id',
            'service_id',
            'service_name',
            'name',
            'type',
            'notes',
            'output',
            'status',
            'agents',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        EP_TABLE_NAME: [
            'mac',
            'ip',
            'tenant',
            'dn',
            'vm_name',
            'interfaces',
            'vmm_domain',
            'controller_name',
            'learning_source',
            'multicast_address',
            'encap',
            'hosting_server_name',
            'is_cep',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        EPG_TABLE_NAME: [
            'dn',
            'tenant',
            'epg',
            'bd',
            'contracts',
            'vrf',
            'epg_health',
            'app_profile',
            'epg_alias',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ],

        TENANT_TABLE_NAME: [
            'tenant',
            'created_ts'
        ],

        POLLING_TABLE_NAME: [
            'pkey',
            'interval',
            'created_ts',
            'updated_ts',
            'last_checked_ts'
        ]
    }

    def __init__(self):
        try:
            self.engine = create_engine(DATABASE_NAME, listeners=[MyListener()])
            self.table_obj_meta = dict()
            self.table_key_meta = dict()
            self.__metadata = self.get_metadata()
        except Exception as e:
            logger.exception("Exception in creating db obj: {}".format(str(e)))

    def get_metadata(self):
        """
        Function to create tables and save table objects
        """
        metadata = MetaData()

        self.vrf = Table(
            self.VRF_TABLE_NAME, metadata,
            Column('vrf_dn', String, primary_key=True),
            Column('created_ts', String)
        )

        self.login = Table(
            self.LOGIN_TABLE_NAME, metadata,
            Column('agent_ip', String, primary_key=True),
            Column('port', String, primary_key=True),
            Column('protocol', String),
            Column('token', String),
            Column('status', String),
            Column('datacenter', String),
            Column('tenant', String, primary_key=True),
            Column('vrf_dn', String, ForeignKey(self.vrf.c.vrf_dn), primary_key=True),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.mapping = Table(
            self.MAPPING_TABLE_NAME, metadata,
            Column('ip', String, primary_key=True),
            Column('dn', String, primary_key=True),
            Column('datacenter', String, primary_key=True),
            Column('enabled', Boolean),
            Column('ap', String),
            Column('bd', String),
            Column('epg', String),
            Column('vrf', String),
            Column('tenant', String),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.node = Table(
            self.NODE_TABLE_NAME, metadata,
            Column('node_id', String, primary_key=True),
            Column('node_name', String),
            Column('node_ip', String),
            Column('datacenter', String),
            Column('agents', PickleType),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.service = Table(
            self.SERVICE_TABLE_NAME, metadata,
            Column('service_id', String, primary_key=True),
            Column('node_id', String, ForeignKey(self.node.c.node_id), primary_key=True),
            Column('service_name', String),
            Column('service_ip', String),
            Column('service_port', String),
            Column('service_address', String),
            Column('service_tags', PickleType),
            Column('service_kind', String),
            Column('namespace', String),
            Column('datacenter', String),
            Column('agents', PickleType),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.nodechecks = Table(
            self.NODECHECKS_TABLE_NAME, metadata,
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
            Column('agents', PickleType),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.servicechecks = Table(
            self.SERVICECHECKS_TABLE_NAME, metadata,
            Column('check_id', String, primary_key=True),
            Column('service_id', String, ForeignKey(self.service.c.service_id), primary_key=True),
            Column('service_name', String),
            Column('name', String),
            Column('type', String),
            Column('notes', String),
            Column('output', String),
            Column('status', PickleType),
            Column('agents', PickleType),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.ep = Table(
            self.EP_TABLE_NAME, metadata,
            Column('mac', String, primary_key=True),
            Column('ip', String, primary_key=True),
            Column('tenant', String),
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

        self.epg = Table(
            self.EPG_TABLE_NAME, metadata,
            Column('dn', String, primary_key=True),
            Column('tenant', String),
            Column('epg', String),
            Column('bd', String),
            Column('contracts', PickleType),
            Column('vrf', String),
            Column('epg_health', String),
            Column('app_profile', String),
            Column('epg_alias', String),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime)
        )

        self.nodeaudit = Table(
            self.NODEAUDIT_TABLE_NAME, metadata,
            Column('node_id', String),
            Column('node_name', String),
            Column('node_ip', String),
            Column('datacenter', String),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime),
            Column('audit_ts', DateTime),
            Column('audit_category', PickleType)
        )

        self.serviceaudit = Table(
            self.SERVICEAUDIT_TABLE_NAME, metadata,
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

        self.nodechecksaudit = Table(
            self.NODECHECKSAUDIT_TABLE_NAME, metadata,
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

        self.servicechecksaudit = Table(
            self.SERVICECHECKSAUDIT_TABLE_NAME, metadata,
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

        self.epaudit = Table(
            self.EPAUDIT_TABLE_NAME, metadata,
            Column('mac', String),
            Column('ip', String),
            Column('tenant', String),
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

        self.epgaudit = Table(
            self.EPGAUDIT_TABLE_NAME, metadata,
            Column('dn', String, primary_key=True),
            Column('tenant', String),
            Column('epg', String),
            Column('bd', String),
            Column('contracts', PickleType),
            Column('vrf', String),
            Column('epg_health', String),
            Column('app_profile', String),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime),
            Column('audit_ts', DateTime),
            Column('audit_category', PickleType)
        )

        self.tenant = Table(
            self.TENANT_TABLE_NAME, metadata,
            Column('tenant', String, primary_key=True),
            Column('created_ts', DateTime)
        )

        self.polling = Table(
            self.POLLING_TABLE_NAME, metadata,
            Column('pkey', String, primary_key=True),
            Column('interval', Integer),
            Column('created_ts', DateTime),
            Column('updated_ts', DateTime),
            Column('last_checked_ts', DateTime),
        )

        self.table_obj_meta.update({
            self.VRF_TABLE_NAME: self.vrf,
            self.LOGIN_TABLE_NAME: self.login,
            self.MAPPING_TABLE_NAME: self.mapping,
            self.NODE_TABLE_NAME: self.node,
            self.SERVICE_TABLE_NAME: self.service,
            self.NODECHECKS_TABLE_NAME: self.nodechecks,
            self.SERVICECHECKS_TABLE_NAME: self.servicechecks,
            self.EP_TABLE_NAME: self.ep,
            self.EPG_TABLE_NAME: self.epg,
            self.NODEAUDIT_TABLE_NAME: self.nodeaudit,
            self.SERVICEAUDIT_TABLE_NAME: self.serviceaudit,
            self.NODECHECKSAUDIT_TABLE_NAME: self.nodechecksaudit,
            self.SERVICECHECKSAUDIT_TABLE_NAME: self.servicechecksaudit,
            self.EPAUDIT_TABLE_NAME: self.epaudit,
            self.EPGAUDIT_TABLE_NAME: self.epgaudit,
            self.TENANT_TABLE_NAME: self.tenant,
            self.POLLING_TABLE_NAME: self.polling
        })
        self.table_key_meta.update({
            self.VRF_TABLE_NAME: {
                'vrf_dn': self.vrf.c.vrf_dn,
                'created_ts': self.vrf.c.created_ts
            },
            self.LOGIN_TABLE_NAME: {
                'agent_ip': self.login.c.agent_ip,
                'port': self.login.c.port,
                'protocol': self.login.c.protocol,
                'token': self.login.c.token,
                'status': self.login.c.status,
                'datacenter': self.login.c.datacenter,
                'tenant': self.login.c.tenant,
                'created_ts': self.login.c.created_ts,
                'updated_ts': self.login.c.updated_ts,
                'last_checked_ts': self.login.c.last_checked_ts
            },
            self.MAPPING_TABLE_NAME: {
                'ip': self.mapping.c.ip,
                'dn': self.mapping.c.dn,
                'datacenter': self.mapping.c.datacenter,
                'enabled': self.mapping.c.enabled,
                'ap': self.mapping.c.ap,
                'bd': self.mapping.c.bd,
                'epg': self.mapping.c.epg,
                'vrf': self.mapping.c.vrf,
                'tenant': self.mapping.c.tenant,
                'created_ts': self.mapping.c.created_ts,
                'updated_ts': self.mapping.c.updated_ts,
                'last_checked_ts': self.mapping.c.last_checked_ts
            },
            self.NODE_TABLE_NAME: {
                'node_id': self.node.c.node_id,
                'node_name': self.node.c.node_name,
                'node_ip': self.node.c.node_ip,
                'datacenter': self.node.c.datacenter,
                'agents': self.node.c.agents,
                'created_ts': self.node.c.created_ts,
                'updated_ts': self.node.c.updated_ts,
                'last_checked_ts': self.node.c.last_checked_ts
            },
            self.SERVICE_TABLE_NAME: {
                'service_id': self.service.c.service_id,
                'node_id': self.service.c.node_id,
                'service_name': self.service.c.service_name,
                'service_ip': self.service.c.service_ip,
                'service_port': self.service.c.service_port,
                'service_address': self.service.c.service_address,
                'service_tags': self.service.c.service_tags,
                'service_kind': self.service.c.service_kind,
                'namespace': self.service.c.namespace,
                'datacenter': self.service.c.datacenter,
                'agents': self.service.c.agents,
                'created_ts': self.service.c.created_ts,
                'updated_ts': self.service.c.updated_ts,
                'last_checked_ts': self.service.c.last_checked_ts
            },
            self.NODECHECKS_TABLE_NAME: {
                'check_id': self.nodechecks.c.check_id,
                'node_id': self.nodechecks.c.node_id,
                'node_name': self.nodechecks.c.node_name,
                'check_name': self.nodechecks.c.check_name,
                'service_name': self.nodechecks.c.service_name,
                'type': self.nodechecks.c.type,
                'notes': self.nodechecks.c.notes,
                'output': self.nodechecks.c.output,
                'status': self.nodechecks.c.status,
                'agents': self.nodechecks.c.agents,
                'created_ts': self.nodechecks.c.created_ts,
                'updated_ts': self.nodechecks.c.updated_ts,
                'last_checked_ts': self.nodechecks.c.last_checked_ts
            },
            self.SERVICECHECKS_TABLE_NAME: {
                'check_id': self.servicechecks.c.check_id,
                'service_id': self.servicechecks.c.service_id,
                'service_name': self.servicechecks.c.service_name,
                'name': self.servicechecks.c.name,
                'type': self.servicechecks.c.type,
                'notes': self.servicechecks.c.notes,
                'output': self.servicechecks.c.output,
                'status': self.servicechecks.c.status,
                'agents': self.servicechecks.c.agents,
                'created_ts': self.servicechecks.c.created_ts,
                'updated_ts': self.servicechecks.c.updated_ts,
                'last_checked_ts': self.servicechecks.c.last_checked_ts
            },
            self.EP_TABLE_NAME: {
                'mac': self.ep.c.mac,
                'ip': self.ep.c.ip,
                'tenant': self.ep.c.tenant,
                'dn': self.ep.c.dn,
                'vm_name': self.ep.c.vm_name,
                'interfaces': self.ep.c.interfaces,
                'vmm_domain': self.ep.c.vmm_domain,
                'controller_name': self.ep.c.controller_name,
                'learning_source': self.ep.c.learning_source,
                'multicast_address': self.ep.c.multicast_address,
                'encap': self.ep.c.encap,
                'hosting_server_name': self.ep.c.hosting_server_name,
                'is_cep': self.ep.c.is_cep,
                'created_ts': self.ep.c.created_ts,
                'updated_ts': self.ep.c.updated_ts,
                'last_checked_ts': self.ep.c.last_checked_ts
            },
            self.EPG_TABLE_NAME: {
                'dn': self.epg.c.dn,
                'tenant': self.epg.c.tenant,
                'epg': self.epg.c.epg,
                'bd': self.epg.c.bd,
                'contracts': self.epg.c.contracts,
                'vrf': self.epg.c.vrf,
                'epg_health': self.epg.c.epg_health,
                'app_profile': self.epg.c.app_profile,
                'epg_alias': self.epg.c.epg_alias,
                'created_ts': self.epg.c.created_ts,
                'updated_ts': self.epg.c.updated_ts,
                'last_checked_ts': self.epg.c.last_checked_ts
            },
            self.TENANT_TABLE_NAME: {
                'tenant': self.tenant.c.tenant,
                'created_ts': self.tenant.c.created_ts
            },
            self.POLLING_TABLE_NAME: {
                'pkey': self.polling.c.pkey,
                'interval': self.polling.c.interval,
                'created_ts': self.polling.c.created_ts,
                'updated_ts': self.polling.c.updated_ts,
                'last_checked_ts': self.polling.c.last_checked_ts
            }
        })
        return metadata

    def create_tables(self):
        try:
            self.__metadata.create_all(self.engine, checkfirst=True)
        except Exception as e:
            logger.info("Exception in {} Error:{}".format(
                'create_tables()', str(e)))

    def insert_into_table(self, connection, table_name, field_values):
        """
        Function to insert single record in table

        Arguments:
            connection   {connection} --> connection object for database
            table_name   {str}        --> name of the database table
            field_values {list/tuple} --> values of single record

        Returns:
            True or False {bool} --> status of operation
        """
        field_values = list(field_values)
        try:
            ins = None
            table_name = table_name.lower()
            field_values.append(datetime.now())
            ins = self.table_obj_meta[table_name].insert().values(field_values)
            if ins is not None:
                connection.execute(ins)
                return True
        except Exception as e:
            logger.exception(
                "Exception in data insertion in {} Error:{}".format(table_name, str(e)))
        return False

    def select_from_table(self, connection, table_name, field_arg_dict={}, required_fields=[]):
        """
        Function to get data from database table

        Arguments:
            connection   {connection} --> connection object for database
            table_name   {str}        --> name of the database table

        Optional Arguments:
            field_arg_dict  {dict} --> key-value pairs of column name and data to filter records
            required_fields {list} --> list of column names which is required

        Returns:
            {list{tuple}} or None --> list of records found in database table on success
        """
        try:
            table_name = table_name.lower()
            field_list = [self.table_key_meta[table_name][each.lower()] for each in required_fields]
            if not field_list:
                field_list = [self.table_obj_meta[table_name]]

            if field_arg_dict:
                select_query = select(field_list)
                for key in field_arg_dict:
                    select_query = select_query.where(
                        self.table_key_meta[table_name][key] == field_arg_dict[key])
            else:
                select_query = select(field_list)

            result = connection.execute(select_query)
            return result.fetchall()
        except Exception as e:
            logger.exception("Exception in selecting data from {} Error:{}".format(table_name, str(e)))
        return None

    def update_in_table(self, connection, table_name, field_arg_dict, new_record_dict):
        """
        Function to update data into database table

        Arguments:
            connection      {connection} --> connection object for database
            table_name      {str}        --> name of the database table
            field_arg_dict  {dict}       --> key-value pairs of column name and data to filter records
            new_record_dict {dict}       --> key-value pairs of column name and data of new value

        Returns:
            True or False {bool} --> status of operation
        """
        try:
            table_name = table_name.lower()
            table_obj = self.table_obj_meta[table_name]
            new_record_dict['last_checked_ts'] = datetime.now()
            update_query = table_obj.update()
            for key in field_arg_dict:
                update_query = update_query.where(
                    self.table_key_meta[table_name][key] == field_arg_dict[key])
            update_query = update_query.values(new_record_dict)
            connection.execute(update_query)
            return True
        except Exception as e:
            logger.exception(
                "Exception in updating {} Error:{}".format(table_name, str(e)))
        return False

    def delete_from_table(self, connection, table_name, field_arg_dict={}):
        """
        Function to delete data from database table

        Arguments:
            connection      {connection} --> connection object for database
            table_name      {str}        --> name of the database table

        Optional Arguments:
            field_arg_dict  {dict}       --> key-value pairs of column name and data to filter records

        Returns:
            True or False {bool} --> status of operation
        """
        try:
            table_name = table_name.lower()
            if field_arg_dict:
                table_obj = self.table_obj_meta[table_name]
                delete_query = table_obj.delete()
                for key in field_arg_dict:
                    delete_query = delete_query.where(
                        self.table_key_meta[table_name][key] == field_arg_dict[key])
            else:
                delete_query = self.table_obj_meta[table_name].delete()
            connection.execute(delete_query)
            return True
        except Exception as e:
            logger.exception(
                "Exception in deletion from {} Error:{}".format(table_name, str(e)))
        return False

    def insert_and_update(self, connection, table_name, new_record, field_arg_dict={}):
        """
        Function to insert new record and update existing record into database table

        Arguments:
            connection      {connection} --> connection object for database
            table_name      {str}        --> name of the database table
            new_record      {list}       --> values of new record

        Optional Arguments:
            field_arg_dict  {dict}       --> key-value pairs of column name and data to filter records

        Returns:
            True or False {bool} --> status of operation
        """
        table_name = table_name.lower()
        if field_arg_dict:
            old_data = self.select_from_table(connection, table_name, field_arg_dict)
            if old_data is not None:
                if len(old_data) > 0:
                    old_data = old_data[0]
                    new_record_dict = dict()
                    index = []
                    for i in range(len(new_record)):
                        if isinstance(new_record[i], bool):
                            try:
                                old_column_value = bool(int(old_data[i]))
                                if old_column_value != new_record[i]:
                                    index.append(i)
                            except Exception:
                                logger.exception("Exception in insert_and_update for table {}".format(table_name))
                        else:
                            if old_data[i] != new_record[i]:
                                index.append(i)
                    field_names = [self.SCHEMA_DICT[table_name][i]for i in index]
                    new_record_dict = dict()
                    for i in range(len(field_names)):
                        new_record_dict[field_names[i]] = new_record[index[i]]

                    if new_record_dict:
                        new_record_dict['updated_ts'] = datetime.now()
                    self.update_in_table(connection, table_name, field_arg_dict, new_record_dict)
                else:
                    self.insert_into_table(connection, table_name, new_record)
            else:
                return False
        else:
            self.insert_into_table(connection, table_name, new_record)
        return True
