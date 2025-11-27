import configparser
from itertools import combinations


class Config:
    def __init__(self, router_id, input_ports, outputs):
        self.router_id = router_id
        self.input_ports = input_ports
        self.outputs = outputs

    def __str__(self):
        lines = f"""CONFIG:
    router id: {self.router_id}
    input ports: {self.input_ports}
    outputs:"""
        for routerid, [port, metric] in self.outputs.items():
            lines += f"""
        router-id: {routerid} port: {port} metric: {metric}"""
        return lines + '\n'


def read_config_file(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    try:
        return get_config(config)
    except ValueError as e:
        raise ValueError(f'CONFIG {filename} ERROR: {e}')


def get_config(config):
    """
    >>> config = configparser.ConfigParser()
    >>> config['SETTINGS'] = {'router-id':'2','input-ports':'2000','outputs':'3000-1-3'}
    >>> c1 = get_config(config)
    >>> print(c1)
    CONFIG:
        router id: 2
        input ports: [2000]
        outputs:
            router-id: 3 port: 3000 metric: 1
    <BLANKLINE>

    """
    router_id, input_ports, outputs = validate_config(config)
    return Config(router_id, input_ports, outputs)


def validate_configs_by_filename(filenames):
    configs = [read_config_file(filename) for filename in filenames]
    validate_configs(configs)

def validate_configs(configs):
    """For all the provided configs:
    ensures that all router-ids are unique,
    sending/receiving router-ids match between neighbours,
    and that metrics between neighbours are the same.

    >>> config1 = configparser.ConfigParser()
    >>> config1['SETTINGS'] = {'router-id':'2','input-ports':'2000','outputs':'3000-1-3'}
    >>> config2 = configparser.ConfigParser()
    >>> config3 = configparser.ConfigParser()

    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3000','outputs':'2000-1-2'}
    >>> validate_configs([get_config(config1), get_config(config2)])

    >>> config2['SETTINGS'] = {'router-id':'2','input-ports':'3000','outputs':'2000-1-2'}
    >>> validate_configs([get_config(config1), get_config(config2)])
    Traceback (most recent call last):
    AssertionError: same router-id: 2

    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3333','outputs':'3000-1-2'}
    >>> validate_configs([get_config(config1), get_config(config2)])
    Traceback (most recent call last):
    AssertionError: port 3000 is already an output to router 3

    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3000','outputs':'2000-1-3'}
    >>> validate_configs([get_config(config1), get_config(config2)])
    Traceback (most recent call last):
    AssertionError: router-id mismatch between routers 2 and 3 on port 2000

    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3000','outputs':'2222-1-2'}
    >>> validate_configs([get_config(config1), get_config(config2)])
    Traceback (most recent call last):
    AssertionError: router 2 listening on port 2000 but no sender

    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3333','outputs':'2000-1-2'}
    >>> validate_configs([get_config(config1), get_config(config2)])
    Traceback (most recent call last):
    AssertionError: sending to router 3 on port 3000 but no receiver

    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3000','outputs':'2000-2-2'}
    >>> validate_configs([get_config(config1), get_config(config2)])
    Traceback (most recent call last):
    AssertionError: metric mismatch between routers 2 and 3

    >>> config1['SETTINGS'] = {'router-id':'2','input-ports':'2000,2001','outputs':'3000-1-3,4000-2-4'}
    >>> config2['SETTINGS'] = {'router-id':'3','input-ports':'3000,3001','outputs':'2000-1-2,4001-3-4'}
    >>> config3['SETTINGS'] = {'router-id':'4','input-ports':'4000,4001','outputs':'2001-2-2,3001-3-3'}
    >>> validate_configs([get_config(config1), get_config(config2), get_config(config3)])
    """
    for c1, c2 in combinations(configs, 2):
        assert c1.router_id != c2.router_id, f'same router-id: {c1.router_id}'

    port_ids = {} # {port: [input_id, output_id]}
    metrics = {}  # {(router1_id, router2_id), metric]} # where router1_id < router2_id
    for config in configs:
        for port in config.input_ports:
            current_ids = port_ids.get(port, [None, None])
            assert current_ids[0] is None, f'port {port} already an input for router {current_ids[0]}'
            current_ids[0] = config.router_id
            port_ids[port] = current_ids

        for router_id, [port, metric] in config.outputs.items():
            current_ids = port_ids.get(port, [None, None])
            assert current_ids[1] is None, f'port {port} is already an output to router {current_ids[1]}'
            current_ids[1] = router_id
            port_ids[port] = current_ids

            lower_id, upper_id = sorted([config.router_id, router_id])
            current_metric = metrics.get((lower_id, upper_id), None)
            if current_metric is not None:
                assert current_metric == metric, f'metric mismatch between routers {lower_id} and {upper_id}'
            metrics[(lower_id, upper_id)] = metric

    for port, [in_id, out_id] in port_ids.items():
        assert in_id != None, f'sending to router {out_id} on port {port} but no receiver'
        assert out_id != None, f'router {in_id} listening on port {port} but no sender'
        assert in_id == out_id, f'router-id mismatch between routers {in_id} and {out_id} on port {port}'


def routerid_is_valid(routerid):
    return  1 <= routerid <= 64000

def validate_router_id(routerid):
    """
    >>> validate_router_id('1')
    1
    >>> validate_router_id('64000')
    64000
    >>> validate_router_id('0')
    Traceback (most recent call last):
    ValueError: router-id must be a number between 1 and 64000. Got "0"
    >>> validate_router_id('64001')
    Traceback (most recent call last):
    ValueError: router-id must be a number between 1 and 64000. Got "64001"
    """
    routerid = routerid.strip()
    if routerid.isdigit() and routerid_is_valid(int(routerid)):
        return int(routerid)
    else:
        raise ValueError(f'router-id must be a number between 1 and 64000. Got "{routerid}"')


def port_is_valid(port):
    return 1024 <= port <= 64000

def validate_port(port):
    """
    >>> validate_port('1024')
    1024
    >>> validate_port('64000')
    64000
    >>> validate_port('1023')
    Traceback (most recent call last):
    ValueError: port must be a number between 1024 and 64000. Got "1023"
    >>> validate_port('64001')
    Traceback (most recent call last):
    ValueError: port must be a number between 1024 and 64000. Got "64001"
    """
    port = port.strip()
    if port.isdigit() and port_is_valid(int(port)):
        return int(port)
    else:
        raise ValueError(f'port must be a number between 1024 and 64000. Got "{port}"')


def metric_is_valid(metric):
    return 1 <= metric <= 16

def validate_metric(metric):
    """
    >>> validate_metric('1')
    1
    >>> validate_metric('16')
    16
    >>> validate_metric('0')
    Traceback (most recent call last):
    ValueError: metric must be a number between 1 and 16. Got "0"
    >>> validate_metric('17')
    Traceback (most recent call last):
    ValueError: metric must be a number between 1 and 16. Got "17"
    """
    metric = metric.strip()
    if metric.isdigit() and metric_is_valid(int(metric)):
        return int(metric)
    else:
        raise ValueError(f'metric must be a number between 1 and 16. Got "{metric}"')


def validate_config(config):
    """
    >>> config = configparser.ConfigParser()
    >>> validate_config(config)
    Traceback (most recent call last):
    ValueError: SETTINGS header not found

    >>> config['SETTINGS'] = {'input-ports':'1024','outputs':'64000-0-1'}
    >>> validate_config(config)
    Traceback (most recent call last):
    ValueError: "router-id" parameter not found

    >>> config['SETTINGS'] = {'router-id':'1','outputs':'64000-0-1'}
    >>> validate_config(config)
    Traceback (most recent call last):
    ValueError: "input-ports" parameter not found

    >>> config['SETTINGS'] = {'router-id':'1','input-ports':'1024'}
    >>> validate_config(config)
    Traceback (most recent call last):
    ValueError: "outputs" parameter not found

    >>> config['SETTINGS'] = {'router-id':'1','input-ports':'2000,2000','outputs':'5000-15-1'}
    >>> validate_config(config)
    Traceback (most recent call last):
    ValueError: "2000" is a duplicate port number

    >>> config['SETTINGS'] = {'router-id':'1','input-ports':'2000','outputs':'2000-15-1'}
    >>> validate_config(config)
    Traceback (most recent call last):
    ValueError: "2000" is already defined as an input port

    >>> config['SETTINGS'] = {'router-id':'1','input-ports':'1024','outputs':'64000-1-1'}
    >>> validate_config(config)
    (1, [1024], {1: [64000, 1]})

    >>> config['SETTINGS'] = {'router-id':' 01 ','input-ports':' 01024 , 01025','outputs':' 064000 - 011 - 01 , 05000 - 012 - 02'}
    >>> validate_config(config)
    (1, [1024, 1025], {1: [64000, 11], 2: [5000, 12]})

    >>> config['SETTINGS'] = {'router-id':'1','input-ports':'2000,2001,2002','outputs':'5000-14-2,5001-15-64000'}
    >>> validate_config(config)
    (1, [2000, 2001, 2002], {2: [5000, 14], 64000: [5001, 15]})

    """
    if not 'SETTINGS' in config:
        raise ValueError('SETTINGS header not found')
    for param in ['router-id', 'input-ports', 'outputs']:
        if not param in config['SETTINGS']:
            raise ValueError(f'"{param}" parameter not found')

    router_id = config['SETTINGS']['router-id']
    router_id = validate_router_id(router_id)

    input_ports_str = config['SETTINGS']['input-ports'].split(',')
    input_ports = []
    for port in input_ports_str:
        port = validate_port(port)
        if port in input_ports:
            raise ValueError(f'"{port}" is a duplicate port number')
        else:
            input_ports.append(port)

    outputs_str = config['SETTINGS']['outputs'].split(',')
    outputs = {}
    for output in outputs_str:
        port, metric, out_routerid = output.strip().split('-')

        port = validate_port(port)
        if port in input_ports:
            raise ValueError(f'"{port}" is already defined as an input port')
        metric = validate_metric(metric)
        out_routerid = validate_router_id(out_routerid)

        outputs[out_routerid] = [port, metric]

    if input_ports == []:
        raise ValueError(f'There must be at least one input port')
    if outputs == []:
        raise ValueError(f'There must be at least one output')

    return router_id, input_ports, outputs


if __name__ == '__main__':
    import doctest
    results = doctest.testmod()
    print(results)
