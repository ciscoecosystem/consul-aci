from Service import alchemy_core
import os
import pytest


dc = dict()
dc.update({
    'login': [
        'agent_ip',
        'port',
        'protocol',
        'token',
        'status',
        'datacenter',
        'tenant'
    ]
})
dc.update({
    'mapping': [
        'ip',
        'dn',
        'datacenter',
        True,
        'ap',
        'bd',
        'epg',
        'vrf',
        'tenant'
    ]
})
dc.update({
    'node': [
        'node_id',
        'node_name',
        'node_ip',
        'datacenter',
        ['agents1', 'agents2']
    ]
})
dc.update({
    'service': [
        'service_id',
        'node_id',
        'service_name',
        'service_ip',
        'service_port',
        'service_address',
        ['tag1', 'tag2'],
        'service_kind',
        'namespace',
        'datacenter',
        ['agents1', 'agents2']
    ]
})
dc.update({
    'nodechecks': [
        'check_id',
        'node_id',
        'node_name',
        'check_name',
        'service_name',
        'check_type',
        'notes',
        'output',
        ['status1', 'status2'],
        ['agents1', 'agents2']
    ]
})
dc.update({
    'servicechecks': [
        'check_id',
        'service_id',
        'service_name',
        'check_name',
        'check_type',
        'notes',
        'output',
        ['status1', 'status2'],
        ['agents1', 'agents2']
    ]
})
dc.update({
    'ep': [
        'mac',
        'ip',
        'tenant',
        'dn',
        'vm_name',
        ['interfaces1', 'interfaces2'],
        'vmm_domain',
        'controller_name',
        'learning_source',
        'multicast_address',
        'encap',
        'hosting_server_name',
        'is_cep'
    ]
})
dc.update({
    'epg': [
        'dn',
        'tenant',
        'epg',
        'bd',
        ['contracts1', 'contracts2'],
        'vrf',
        'epg_health',
        'app_profile',
        'epg_alias'
    ]
})
dc.update({
    'tenant': [
        'tenant'
    ]
})


def clear_db():
    os.remove('/home/app/data/ConsulDatabase.db')


tables = dc.keys()


@pytest.mark.parametrize("table", tables)
def test_insert_into_table(table):
    try:
        clear_db()
    except Exception:
        pass
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    connection = db_obj.engine.connect()

    assert db_obj.insert_into_table(connection, table, dc[table]) is True
    assert db_obj.insert_into_table(connection, table, dc[table]) is False

    inserted_rec = db_obj.select_from_table(connection, table)
    assert len(inserted_rec) == 1
    for record in inserted_rec:
        for index, value in enumerate(dc[table]):
            assert value == record[index]

    assert db_obj.insert_into_table(connection, '', dc[table]) is False
    assert db_obj.insert_into_table(connection, '', []) is False

    connection.close()
    clear_db()


@pytest.mark.parametrize("table", tables)
def test_select_from_table(table):
    try:
        clear_db()
    except Exception:
        pass
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    connection = db_obj.engine.connect()
    dummy = [dc[table], [i for i in dc[table]]]
    dummy[1][0] = '1'
    assert db_obj.insert_into_table(connection, table, dummy[0]) is True
    assert db_obj.insert_into_table(connection, table, dummy[1]) is True

    records = db_obj.select_from_table(connection, table)

    assert len(records) == 2
    for i, each in enumerate(dummy):
        for j, value in enumerate(each):
            assert value == records[i][j]

    connection.close()
    clear_db()


@pytest.mark.parametrize("table", tables)
def test_update_in_table(table):
    try:
        clear_db()
    except Exception:
        pass
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    connection = db_obj.engine.connect()

    if table != 'tenant':
        assert db_obj.insert_into_table(connection, table, dc[table]) is True

        assert db_obj.update_in_table(
            connection,
            table,
            {},
            {
                dc[table][0]: 'new{}'.format(dc[table][0]),
            }
        )
        records = db_obj.select_from_table(connection, table)
        assert len(records) == 1
        for i, each in enumerate(records):
            for j in range(len(dc[table])):
                if j == 0:
                    assert each[j] == 'new{}'.format(dc[table][j])
                    continue
                assert each[j] == records[i][j]

    connection.close()
    clear_db()


@pytest.mark.parametrize("table", tables)
def test_delete_from_table(table):
    try:
        clear_db()
    except Exception:
        pass
    db_obj = alchemy_core.Database()
    db_obj.create_tables()
    connection = db_obj.engine.connect()

    dummy = [dc[table], [i for i in dc[table]]]
    dummy[1][0] = 'new{}'.format(dummy[1][0])
    db_obj.insert_into_table(connection, table, dummy[0]) is True
    db_obj.insert_into_table(connection, table, dummy[1]) is True

    assert db_obj.delete_from_table(connection, table)
    records = db_obj.select_from_table(connection, table)

    assert len(records) == 0
    db_obj.insert_into_table(connection, table, dummy[0]) is True

    assert db_obj.delete_from_table(
        connection,
        table,
        {dc[table][0]: dc[table][0]}
    )

    assert db_obj.delete_from_table(connection, "") is False

    connection.close()
    clear_db()


@pytest.mark.parametrize("table", tables)
def test_insert_and_update(table):
    try:
        clear_db()
    except Exception:
        pass
    db_obj = alchemy_core.Database()
    db_obj.create_tables()

    if table != 'tenant':
        dummy = [dc[table], [i for i in dc[table]], [i for i in dc[table]]]
        connection = db_obj.engine.connect()

        for each in dummy:
            assert db_obj.insert_and_update(
                connection,
                table,
                each,
                {
                    dc[table][0]: each[0]
                }
            )

        connection.close()
        connection = db_obj.engine.connect()
        records = db_obj.select_from_table(connection, table)
        connection.close()
        assert len(records) == 1

        for each in records:
            assert each[-2] is None

        dummy[1][0] = 'new1'
        dummy[2][0] = 'new2'
        connection = db_obj.engine.connect()
        for each in dummy:
            assert db_obj.insert_and_update(
                connection,
                table,
                each,
                {
                    dc[table][0]: each[0]
                }
            )
        connection.close()

        connection = db_obj.engine.connect()
        records = db_obj.select_from_table(connection, table)
        connection.close()
        assert len(records) == 3

        for each in records:
            assert each[-2] is None
    clear_db()
