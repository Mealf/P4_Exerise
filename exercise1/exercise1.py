#!/usr/bin/env python3

from p4_mininet import P4Switch, P4Host

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI

import argparse

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

 

args = parser.parse_args()

class SimpleTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        s1 = self.addSwitch('s1',  sw_path = args.behavioral_exe, json_path = args.json, thrift_port = args.thrift_port,
         cls = P4Switch, pcap_dump = args.pcap_dump)

        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2')

        self.addLink(h1, s1)
        self.addLink(h2, s1)

def myNetwork():
    topo = SimpleTopo()
    net = Mininet(topo=topo, link=TCLink, host=P4Host, controller=None)
    net.start()
    CLI(net)

if __name__ == '__main__':
    myNetwork()