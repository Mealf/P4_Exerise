#!/usr/bin/env python3
from time import sleep
import argparse, os

from p4_mininet import P4Switch, P4Host

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI

from p4runtime_switch import P4RuntimeSwitch
import p4runtime_lib.simple_controller



parser = argparse.ArgumentParser(description='Mininet demo')

parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=False, default='simple_switch' )

parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)

parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=2)

parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')

parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)

parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

parser.add_argument('--runtime-json', type=str, action='store', required=True)

 

args = parser.parse_args()

class SimpleTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        s1 = self.addSwitch('s1', cls=None)

        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2')

        self.addLink(h1, s1)
        self.addLink(h2, s1)

def configureP4Switch(**switch_args):
    class ConfiguredP4RuntimeSwitch(P4RuntimeSwitch):
        def __init__(self, *opts, **kwargs):
            kwargs.update(switch_args)
            P4RuntimeSwitch.__init__(self, *opts, **kwargs)

        def describe(self):
            print("%s -> gRPC port: %d" % (self.name, self.grpc_port))

    return ConfiguredP4RuntimeSwitch


def myNetwork():
    topo = SimpleTopo()

    p4runtime_switch = configureP4Switch(
        sw_path=args.behavioral_exe,
        json_path=args.json)

    net = Mininet(topo=topo, link=TCLink, host=P4Host, controller=None, switch=p4runtime_switch)
    net.start()

    sleep(1)

    # Add arp info to host 
    h1 = net.get('h1')
    h1.cmd('arp -s 10.0.0.2 00:00:00:00:00:02')

    h2 = net.get('h2')
    h2.cmd('arp -s 10.0.0.1 00:00:00:00:00:01')

    # Insert runtime rule to switch
    sw_obj = net.get('s1')
    grpc_port = sw_obj.grpc_port
    device_id = sw_obj.device_id
    runtime_json = args.runtime_json
    with open(runtime_json, 'r') as sw_conf_file:
        p4runtime_lib.simple_controller.program_switch(
            addr='127.0.0.1:%d' % grpc_port,
            device_id=device_id,
            sw_conf_file=sw_conf_file,
            workdir=os.getcwd(),
            proto_dump_fpath='logs/s1-p4runtime-requests.txt')

    sleep(1)

    CLI(net)

    net.stop()

if __name__ == '__main__':
    myNetwork()