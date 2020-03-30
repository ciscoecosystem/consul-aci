__author__ = 'nilayshah'

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

class Application(Base):
    __tablename__ = 'Application'
    appId = Column(Integer, primary_key=True)
    appName = Column(String)
    appMetrics = Column(PickleType)  # https://stackoverflow.com/questions/1378325/python-dicts-in-sqlalchemy
    timestamp = Column(DateTime)
    isViewEnabled = Column(Boolean, nullable=False)

    def __init__(self, appId, appName, appMetrics, timestamp, isViewEnabled=None):
        self.appId = appId
        self.appName = appName
        self.appMetrics = appMetrics
        self.timestamp = timestamp
        if isViewEnabled != None:
            self.isViewEnabled = isViewEnabled
        else:
            self.isViewEnabled = True


class Tiers(Base):
    __tablename__ = 'Tiers'
    tierId = Column(Integer, primary_key=True)
    tierName = Column(String)
    appId = Column(Integer, ForeignKey('Application.appId'))
    tierHealth = Column(String)
    sepchild = relationship('ServiceEndpoints', primaryjoin='Tiers.tierId==ServiceEndpoints.tierId', backref='Tiers')
    hevchild = relationship('HealthViolations', primaryjoin='Tiers.tierId==HealthViolations.tierId', backref='Tiers')

    def __init__(self, tierId, tierName, appId, tierHealth):
        self.tierId = tierId
        self.tierName = tierName
        self.appId = appId
        self.tierHealth = tierHealth


class ServiceEndpoints(Base):
    __tablename__ = 'ServiceEndpoints'
    sepId = Column(Integer, primary_key=True)
    sep = Column(PickleType)  # List of serialized json #https://stackoverflow.com/questions/1378325/python-dicts-in-sqlalchemy
    timestamp = Column(DateTime)
    tierId = Column(Integer, ForeignKey('Tiers.tierId'))
    appId = Column(Integer, ForeignKey('Application.appId'))

    def __init__(self, sepId, sep, tierId, appId, timestamp):
        self.sepId = sepId
        self.sep = sep
        self.tierId = tierId
        self.appId = appId
        self.timestamp = timestamp


class HealthViolations(Base):
    __tablename__ = 'HealthViolations'
    violationId = Column(Integer, primary_key=True)
    startTime = Column(String)
    businessTransaction = Column(String)
    description = Column(String)
    severity = Column(String)
    timestamp = Column(DateTime)
    endTime = Column(String)
    status = Column(String)
    evaluationStates = Column(PickleType)
    tierId = Column(Integer, ForeignKey('Tiers.tierId'))
    appId = Column(Integer, ForeignKey('Application.appId'))

    # TODO: Correct or remove following comment
    # violationId, startTime, businessTransaction, description, severity, tierId, appId
    def __init__(self, violationId, startTime, businessTransaction, description, severity, tierId, appId, timestamp, endTime, status, evaluationStates):
        self.violationId = violationId
        self.startTime = startTime
        self.businessTransaction = businessTransaction
        self.description = description
        self.severity = severity
        self.tierId = tierId
        self.appId = appId
        self.timestamp = timestamp
        self.endTime = endTime
        self.status = status
        self.evaluationStates = evaluationStates


class Nodes(Base):
    __tablename__ = 'Nodes'
    nodeId = Column(Integer, primary_key=True)
    nodeName = Column(String)
    tierId = Column(Integer, ForeignKey('Tiers.tierId'))
    nodeHealth = Column(String)
    ipAddress = Column(PickleType)
    timestamp = Column(DateTime)
    appId = Column(Integer, ForeignKey('Application.appId'))
    macAddress = Column(PickleType)

    def __init__(self, nodeId, nodeName, tierId, nodeHealth, ipList, appId, timestamp, macList):
        self.nodeId = nodeId
        self.nodeName = nodeName
        self.tierId = tierId
        self.nodeHealth = nodeHealth
        self.ipAddress = ipList
        self.appId = appId
        self.timestamp = timestamp
        self.macAddress = macList


class EpgHistory(Base):
    __tablename__ = 'EpgHistory'
    epgDn = Column(String, primary_key=True)
    epgFaultRecords = Column(PickleType)
    epgHealthRecords = Column(PickleType)
    epgEventRecords = Column(PickleType)
    epgLogRecords = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, epgDn, epgFaultRecords, epgHealthRecords, epgEventRecords, epgLogRecords, timestamp):
        self.epgDn = epgDn
        self.epgFaultRecords = epgFaultRecords
        self.epgHealthRecords = epgHealthRecords
        self.epgEventRecords = epgEventRecords
        self.epgLogRecords = epgLogRecords
        self.timestamp = timestamp

class EpgSummary(Base):
    __tablename__ = 'EpgSummary'
    epgDn = Column(String, primary_key=True)
    epgDomains = Column(PickleType)
    epgSubnets = Column(PickleType)
    epgStaticEps = Column(PickleType)
    epgStaticLeaves = Column(PickleType)
    epgFcPaths = Column(PickleType)
    epgStaticPorts = Column(PickleType)
    epgIfConns = Column(PickleType)
    epgContracts = Column(PickleType)
    epgLabels = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, epgDn, epgDomains, epgSubnets, epgStaticEps, epgStaticLeaves, epgFcPaths, epgStaticPorts, epgIfConns, epgContracts, epgLabels, timestamp):
        self.epgDn = epgDn
        self.epgDomains = epgDomains
        self.epgSubnets = epgSubnets
        self.epgStaticEps = epgStaticEps
        self.epgStaticLeaves = epgStaticLeaves
        self.epgFcPaths = epgFcPaths
        self.epgStaticPorts = epgStaticPorts
        self.epgIfConns = epgIfConns
        self.epgContracts = epgContracts
        self.epgLabels = epgLabels
        self.timestamp = timestamp

class ApHistory(Base):
    __tablename__ = 'ApHistory'
    apDn = Column(String, primary_key=True)
    apFaultRecords = Column(PickleType)
    apHealthRecords = Column(PickleType)
    apEventRecords = Column(PickleType)
    apLogRecords = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, apDn, apFaultRecords, apHealthRecords, apEventRecords, apLogRecords, timestamp):
        self.apDn = apDn
        self.apFaultRecords = apFaultRecords
        self.apHealthRecords = apHealthRecords
        self.apEventRecords = apEventRecords
        self.apLogRecords = apLogRecords
        self.timestamp = timestamp

class ApSummary(Base):
    __tablename__ = 'ApSummary'
    apDn = Column(String, primary_key=True)
    apEpgs = Column(PickleType)
    apUsegEpgs = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, apDn, apEpgs, apUsegEpgs, timestamp):
        self.apDn = apDn
        self.apEpgs = apEpgs
        self.apUsegEpgs = apUsegEpgs
        self.timestamp = timestamp


class ACItemp(Base):
    # ACI temp gets all EPs in APIC for all tenants, UI will request based on tenant and get EPs for that tenant
    __tablename__ = 'ACItemp'
    dn = Column(String, primary_key=True)
    IP = Column(String)
    tenant = Column(String)
    appId = Column(Integer, ForeignKey('Application.appId'))
    selector = Column(Integer, default=0)  # 0 or 1 (1 on user input selected, 0 on deselect)

    def __init__(self, dn, IP, tenant, appId=None, selector=0):
        self.dn = dn
        self.IP = IP
        self.tenant = tenant
        self.appId = appId  # Not required
        self.selector = selector


class ACIperm(Base):
    # ACI perm has user selected EPs for a given tenant and will show all selected EPs upon request for that tenant
    __tablename__ = 'ACIperm'
    IP = Column(String)
    dn = Column(String, primary_key=True)
    tenant = Column(String)
    appId = Column(Integer, ForeignKey('Application.appId'))

    def __init__(self, IP, dn, tenant, appId):
        self.IP = IP
        self.dn = dn
        self.tenant = tenant
        self.appId = appId


class Mapping(Base):
    # Map table will store mappings for each app. The appId is the primary key and the mapped data is a list of dicts
    __tablename__ = 'Mapping'
    appId = Column(String, primary_key=True)
    mapped_data = Column(PickleType)

    def __init__(self, appId, mapped_data):
        self.appId = appId
        self.mapped_data = mapped_data


class Database():
    def __init__(self):
        self.engine = create_engine("sqlite:///AppD_Test.db?check_same_thread=False")

        # get a handle on the table object
        # self.Application_table = Application.__table__
        # get a handle on the metadata
        self.metadata = Base.metadata
        Session = sessionmaker(bind=self.engine)
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


    # TODO: correct the comment with name of all the fields for all the tables
    def insert_into(self, table, data):
        try:
            if table == 'Mapping':
                #  appId, mapped_data [{dn, ipAddress}]
                self.session.add(Mapping(data[0], data[1]))

            elif table == 'Application':
                # appId, appName, appMetrics, timestamp
                self.session.add(Application(data[0], str(data[1]), data[2], data[3]))

            elif table == 'Tiers':
                # tierId, tierName, appId, tierHealth
                self.session.add(Tiers(data[0], str(data[1]), data[2], data[3]))

            elif table == 'Nodes':
                # nodeId, nodeName, tierId, nodeHealth, ipAddress, appId, timestamp, macAddress
                self.session.add(Nodes(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))

            elif table == 'ServiceEndpoints':
                # sepId, sep, tierId, appId, timestamp
                self.session.add(ServiceEndpoints(data[0], data[1], data[2], data[3], data[4]))

            elif table == 'HealthViolations':
                # violationId, startTime, businessTransaction,description,severity,tierId,appId
                self.session.add(HealthViolations(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10]))

            elif table == 'ACItemp':
                # IP, dn, appId, selector (0 or 1)
                self.session.add(ACItemp(data[0], data[1], data[2]))

            elif table == 'ACIPerm':
                # IP, dn, appId
                self.session.add(ACIperm(data[0], data[1], data[2], data[3]))

        except Exception as e:
            logger.exception('Exception in Insert: ' + str(e))
            self.commit_session()


    def update(self, table, data):
        try:
            if table == 'Mapping':
                self.session.query(Mapping).filter(Mapping.appId == data[0]).update({'mapped_data': data[1]})

            elif table == 'Application':
                # appId, appName, appMetrics, timestamp
                self.session.query(Application).filter(Application.appId == data[0]).update(
                    {'appName': str(data[1]), 'appMetrics': data[2], 'timestamp': data[3]})

            elif table == 'Tiers':
                # tierId, tierName, appId, tierHealth
                self.session.query(Tiers).filter(Tiers.tierId == data[0]).update(
                    {'tierName': data[1], 'appId': data[2], 'tierHealth': data[3]})

            elif table == 'Nodes':
                # nodeId, nodeName, tierId, nodeHealth, ipAddress, appId, timestamp, macAddress
                self.session.query(Nodes).filter(Nodes.nodeId == data[0]).update(
                    {'nodeName': data[1], 'tierId': data[2], 'nodeHealth': data[3], 'ipAddress': data[4],
                     'appId': data[5], 'timestamp': data[6], 'macAddress': data[7]})

            elif table == 'ServiceEndpoints':
                # sepId, sep, tierId, timestamp
                self.session.query(ServiceEndpoints).filter(ServiceEndpoints.sepId == data[0]).update(
                    {'sep': data[1], 'tierId': data[2], 'appId': data[3], 'timestamp': data[4]})

            elif table == 'HealthViolations':
                # violationId, startTime, businessTransaction,description,severity,tierId,appId
                self.session.query(HealthViolations).filter(HealthViolations.violationId == data[0]).update(
                    {'startTime': data[1], 'businessTransaction': data[2], 'description': data[3], 'severity': data[4],
                     'tierId': data[5], 'appId': data[6], 'timestamp': data[7]}, synchronize_session='fetch')

            elif table == 'ACItemp':
                # IP, dn, appId, selector (0 or 1)
                self.session.query(ACItemp).filter(ACItemp.dn == data[0]).update({'IP': data[1], 'tenant': data[2]})

            elif table == 'ACIPerm':
                # IP, dn, appId
                self.session.query(Tiers).filter(Tiers.tierId == data[0]).update(
                    {'tierName': data[1], 'appId': data[2], 'tierHealth': data[3]})
        except Exception as e:
            logger.exception('Exception in Update:' + str(e))
            self.commit_session()


    def return_values(self, table):
        try:
            if table == 'Mapping':
                return self.session.query(Mapping).all()
            elif table == 'Application':
                return self.session.query(Application).all()
            elif table == 'Tiers':
                return self.session.query(Tiers).all()
            elif table == 'Nodes':
                return self.session.query(Nodes).all()
            elif table == 'ServiceEndpoints':
                return self.session.query(ServiceEndpoints).all()
            elif table == 'HealthViolations':
                return self.session.query(HealthViolations).all()
            elif table == 'ACItemp':
                return self.session.query(ACItemp).all()
            elif table == 'ACIperm':
                return self.session.query(ACIperm).all()
        except Exception as e:
            logger.exception('Exception in returning values for table: ' + str(table) + ', Error:' + str(e))
            self.commit_session()
        return []


    def delete_entry(self, table, deleteid):
        try:
            logger.info('To delete from table: ' + str(table) + '; id -' + str(deleteid))
            if table == 'Application':
                self.session.query(Application).filter(Application.appId == int(deleteid)).delete()

            elif table == 'Mapping':
                self.session.query(Mapping).filter(Mapping.appId == str(deleteid)).delete()

            elif table == 'Tiers':
                self.session.query(Tiers).filter(Tiers.tierId == int(deleteid)).delete()

            elif table == 'Nodes':
                self.session.query(Nodes).filter(Nodes.nodeId == int(deleteid)).delete()

            elif table == 'ServiceEndpoints':
                self.session.query(ServiceEndpoints).filter(ServiceEndpoints.sepId == int(deleteid)).delete()

            elif table == 'HealthViolations':
                self.session.query(HealthViolations).filter(HealthViolations.violationId == int(deleteid)).delete()
            
            logger.debug('Table Values deleted for - '+str(table))
        
        except Exception as e:
            logger.exception('Exception Deleting values in table - ' + str(e))
            self.commit_session()

    def check_and_delete(self, table, idList):
        """This function deletes all the records except that in idList
        
        table : Name of the table
        idList: IDs to keep in DB  
        """
        
        try:
            tabledata = self.return_values(table)
        except Exception as e:
            logger.exception('Exception Deleting values in table - ' + str(e))
        if not tabledata:
            logger.info('Nothing to Delete')
        else:
            tableids = []
            if table == 'Application':
                for each in tabledata: tableids.append(each.appId)
            elif table == 'Tiers':
                for each in tabledata: tableids.append(each.tierId)
            elif table == 'Nodes':
                for each in tabledata: tableids.append(each.nodeId)
            elif table == 'ServiceEndpoints':
                for each in tabledata: tableids.append(each.sepId)
            elif table == 'HealthViolations':
                for each in tabledata: tableids.append(each.violationId)
            deleteList = list(set(tableids) - set(idList))
            logger.info('Delete for table:'+str(table)+', idlist: '+str(idList))
            try:
                for each in deleteList: self.delete_entry(table, each)
            except Exception as e:
                logger.exception('Exception in Check and Delete: ' + str(e))
                self.commit_session()


    def insert_or_update(self, table, key, data):
        try:
            if table == "EpgHistory":
                recordExists = self.session.query(exists().where(EpgHistory.epgDn == key)).scalar()
                if recordExists:
                    data_dict = {
                        "epgFaultRecords": data[0],
                        "epgHealthRecords": data[1],
                        "epgEventRecords": data[2],
                        "epgLogRecords": data[3],
                        "timestamp": data[4]
                    }
                    action = "Updating"
                    self.session.query(EpgHistory).filter(EpgHistory.epgDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    epgHistoryRecord = EpgHistory(epgDn = key, epgFaultRecords = data[0], epgHealthRecords = data[1], epgEventRecords = data[2], epgLogRecords = data[3], timestamp = data[4])
                    self.session.add(epgHistoryRecord)

            elif table == "EpgSummary":
                recordExists = self.session.query(exists().where(EpgSummary.epgDn == key)).scalar()
                if recordExists:
                    data_dict = {
                        "epgDomains": data[0],
                        "epgSubnets": data[1],
                        "epgStaticEps": data[2],
                        "epgStaticLeaves": data[3],
                        "epgFcPaths": data[4],
                        "epgStaticPorts": data[5],
                        "epgIfConns": data[6],
                        "epgContracts": data[7],
                        "epgLabels": data[8],
                        "timestamp": data[9]
                    }
                    action = "Updating"
                    self.session.query(EpgSummary).filter(EpgSummary.epgDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    epgSummaryRecord = EpgSummary(epgDn = key, epgDomains = data[0], epgSubnets = data[1], epgStaticEps = data[2], epgStaticLeaves = data[3], epgFcPaths = data[4], 
                    epgStaticPorts = data[5], epgIfConns = data[6], epgContracts = data[7], epgLabels = data[8], timestamp = data[9])
                    self.session.add(epgSummaryRecord)

            elif table == "ApHistory":
                recordExists = self.session.query(exists().where(ApHistory.apDn == key)).scalar()
                if recordExists:
                    data_dict = {
                        "apFaultRecords": data[0],
                        "apHealthRecords": data[1],
                        "apEventRecords": data[2],
                        "apLogRecords": data[3],
                        "timestamp": data[4]
                    }
                    action = "Updating"
                    self.session.query(ApHistory).filter(ApHistory.apDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    epgHistoryRecord = ApHistory(apDn = key, apFaultRecords = data[0], apHealthRecords = data[1], apEventRecords = data[2], apLogRecords = data[3], timestamp = data[4])
                    self.session.add(epgHistoryRecord)

            elif table == "ApSummary":
                recordExists = self.session.query(exists().where(ApSummary.apDn == key)).scalar()
                if recordExists:
                    data_dict = {
                        "apEpgs": data[0],
                        "apUsegEpgs": data[1],
                        "timestamp": data[2]
                    }
                    action = "Updating"
                    self.session.query(ApSummary).filter(ApSummary.apDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    apSummaryRecord = ApSummary(apDn = key, apEpgs = data[0], apUsegEpgs = data[1], timestamp = data[2])
                    self.session.add(apSummaryRecord)

            elif table == "HealthViolations":
                recordExists = self.session.query(exists().where(HealthViolations.violationId == key)).scalar()
                if recordExists:
                    data_dict = {
                        "startTime": data[0],
                        "businessTransaction": data[1],
                        "description": data[2],
                        "severity": data[3],
                        "tierId": data[4],
                        "appId": data[5],
                        "timestamp": data[6],
                        "endTime": data[7],
                        "status": data[8],
                        "evaluationStates": data[9],
                    }
                    action = "Updating"
                    self.session.query(HealthViolations).filter(HealthViolations.violationId == key).update(data_dict)
                else:
                    action = "Inserting"
                    healthViolationRecord = HealthViolations(
                        violationId = key,
                        startTime = data[0],
                        businessTransaction = data[1],
                        description = data[2],
                        severity = data[3],
                        tierId = data[4],
                        appId = data[5],
                        timestamp = data[6],
                        endTime = data[7],
                        status = data[8],
                        evaluationStates = data[9]
                    )
                    self.session.add(healthViolationRecord)

            self.commit_session()
        except Exception as ex:
            logger.exception('Exception while ' + action + ' Record in: \n Table : ' + table + "\n " + str(ex))
            self.commit_session()


    # TODO: Refactor the function with use of WHERE clause.
    # Gets Data From Table and Updates or Inserts a record with given ID
    def check_if_exists_and_update(self, table, data):
        try:
            dataId = data[0]
            tableids = []

            # Step 1: Insert or Update
            tabledata = self.return_values(table)

            if tabledata:
                if table == 'Mapping':
                    for each in tabledata: tableids.append(each.appId)
                elif table == 'Application':
                    for each in tabledata: tableids.append(each.appId)
                elif table == 'Tiers':
                    for each in tabledata: tableids.append(each.tierId)
                elif table == 'Nodes':
                    for each in tabledata: tableids.append(each.nodeId)
                elif table == 'ServiceEndpoints':
                    for each in tabledata: tableids.append(each.sepId)
                elif table == 'HealthViolations':
                    for each in tabledata: tableids.append(each.violationId)
                elif table == 'ACItemp':
                    for each in tabledata: tableids.append(each.dn)

            if tableids:
                if dataId in tableids:
                    logger.info('Update table:' + str(table) + ' with Values:' + str(data))
                    self.update(table, data)
                else:
                    logger.info('Insert into table:' + str(table) + ' with Values:' + str(data))
                    self.insert_into(table, data)
            else:
                logger.info('Insert into table:' + str(table) + ' with Values:' + str(data))
                self.insert_into(table, data)

            self.commit_session()
        except Exception as e:
            logger.exception('Exception in Insert: ' + str(e))
            self.commit_session()


    # TODO: check and update the return statements of all the below functions
    # Returns values from database based on query filers (IDs)
    def return_application(self, query_type, query_params):
        try:
            if query_type == 'appId':
                # query = self.session.query(Application).all()
                return self.session.query(Application).filter(Application.appId == query_params)
            if query_type == 'appName':
                return self.session.query(Application).filter(Application.appName == query_params)
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not return Application details. Error: " + str(e))
            logger.info("Exception occured for query_type: "+query_type)
            logger.info("Exception occured for query_params: "+query_params)
            return []


    def return_tiers(self, query_type, query_params):
        try:
            if query_type == 'tierId':
                # query = self.session.query(Application).all()
                return self.session.query(Tiers).filter(Tiers.tierId == query_params)
            if query_type == 'tierName':
                return self.session.query(Tiers).filter(Tiers.tierName == query_params)
            if query_type == 'appId':
                return self.session.query(Tiers).filter(Tiers.appId == query_params)
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not return Tier details. Error: " + str(e))
            logger.info("Exception occured for query_type: "+query_type)
            logger.info("Exception occured for query_params: "+query_params)
            return []


    def return_nodes(self, query_type, query_params):
        try:
            if query_type == 'nodeId':
                return self.session.query(Nodes).filter(Nodes.nodeId == query_params)
            if query_type == 'nodeName':
                return self.session.query(Nodes).filter(Nodes.nodeName == query_params)
            if query_type == 'tierId':
                return self.session.query(Nodes).filter(Nodes.tierId == query_params)
            if query_type == 'appId':
                return self.session.query(Nodes).filter(Nodes.appId == query_params)
            if query_type == 'ipAddress':
                return self.session.query(Nodes).filter(func.json_contains(Nodes.ipAddress, query_params) == 1).all()
            if query_type == 'macAddress':
                return self.session.query(Nodes).filter(func.json_contains(Nodes.macAddress, query_params) == 1).all()
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not return Node details. Error: " + str(e))
            logger.info("Exception occured for query_type: "+query_type)
            logger.info("Exception occured for query_params: "+query_params)
            return []


    def return_service_endpoints(self, query_type, query_params):
        try:
            if query_type == 'tierId':
                return self.session.query(ServiceEndpoints).filter(ServiceEndpoints.tierId == query_params)
            if query_type == 'appId':
                return self.session.query(ServiceEndpoints).filter(ServiceEndpoints.appId == query_params)
            if query_type == 'sepId':
                return self.session.query(ServiceEndpoints).filter(ServiceEndpoints.sepId == query_params)
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not return service endpoints. Error: " + str(e))
            logger.info("Exception occured for query_type: "+query_type)
            logger.info("Exception occured for query_params: "+query_params)
            return []


    def return_health_violations(self, query_type, query_params):
        try:
            if query_type == 'tierId':
                return self.session.query(HealthViolations).filter(HealthViolations.tierId == query_params)
            if query_type == 'appId':
                return self.session.query(HealthViolations).filter(HealthViolations.appId == query_params)
            if query_type == 'violationId':
                return self.session.query(HealthViolations).filter(HealthViolations.violationId == query_params)
            if query_type == 'severity':
                return self.session.query(HealthViolations).filter(HealthViolations.severity == query_params)
            if query_type == 'startTime':
                return self.session.query(HealthViolations).filter(HealthViolations.startTime == query_params)
            if query_type == 'businessTransaction':
                return self.session.query(HealthViolations).filter(HealthViolations.businessTransaction == query_params)
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not return Health violations. Error: " + str(e))
            logger.info("Exception occured for query_type: "+query_type)
            logger.info("Exception occured for query_params: "+query_params)
            return []


    def get_app_list(self):
        applicationList = []
        try:
            appList = self.session.query(Application).all()
            for app in appList:
                application = {'appId': app.appId, 'appName': str(app.appName),
                               'appHealth': str(app.appMetrics['data'][0]['severitySummary']['performanceState']),
                               'isViewEnabled': app.isViewEnabled}
                applicationList.append(application)
            self.commit_session()
        except Exception as e:
            self.flush_session()
            logger.exception( "Internal backend error: could not retrieve Application list. Error: " + str(e))
        return applicationList
    

    def get_app_by_id(self, id):
        try:
            app = self.session.query(Application).filter(and_(Application.appId == id, Application.isViewEnabled == True)).first()
            if app:
                application = {'appId': app.appId, 'appName': str(app.appName),
                               'appHealth': str(app.appMetrics['data'][0]['severitySummary']['performanceState']),
                               'isViewEnabled': app.isViewEnabled}
                return application
            self.commit_session()
        except Exception as e:
            logger.exception( "Internal backend error: could not retrieve Application by Id. Error: " + str(e))
            self.flush_session()

        return None


    def enable_view_update(self, appId, bool):
        try:
            self.session.query(Application).filter(Application.appId == appId).update(
                {'isViewEnabled': bool})
            return self.commit_session()
        except Exception as e:
            self.flush_session()
            logger.exception("Could not enable the view for application"+str(appId)+". Error: " + str(e))
            return json.dumps({"payload": {}, "status_code": "300", "message": "Could not enable the view for application"+str(appId)+". Error: "+str(e)})


    def return_mapping(self, query_params):
        try:
            table_data = self.session.query(Mapping).filter(Mapping.appId == query_params)
            for first in table_data:
                return first.mapped_data
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not retrieve mappings. Error: " + str(e))
            logger.info("Exception occured for query_params: "+query_params)
            return []


    def ips_for_app(self, appId):
        try:
            return self.return_nodes('appId', appId)
        except Exception as e:
            self.flush_session()
            logger.exception("Internal backend error: could not retrieve nodes. Error: " + str(e))
            return []
