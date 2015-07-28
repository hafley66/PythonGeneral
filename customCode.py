#!/usr/bin/env python
import os, sys, socket, struct, select, time, numpy as np, matplotlib.pyplot as plt
class Destination:
    def __init__(self, destination):
        self.destination = ""
        
        self.success = {}
        self.success["ttl"] = []
        self.success["rtt"] = []
        
        self.failure = {}
        self.failure["ttl"] = []
        self.failure["rtt"] = []

    def add_success(self, ttl, rtt):
        self.success[ttl] = rtt
        self.success.ttl += [ttl]
        self.success.rtt += [rtt]

    def add_failure(self, ttl, rtt):
        self.failure[ttl] = rtt
        self.failure.ttl += [ttl]
        self.failure.rtt += [rtt]

    def get_best_rtt(self):
        return sorted(self.success.rtt)[0]
    def get_best_ttl(self):
        return sorted(self.success.ttl)[0]

    def graph_with_plt(self, index):
        success = self.success
        failure = self.failure
        plt.scatter(success.ttl, success.rtt, c='r', marker='p')
        plt.scatter(failure.ttl, failure.rtt, c='b', marker='o')
        plt.xlabel('TTL (hops)')
        plt.ylabel('RTT')
        plt.title('[RTT VS TTL]\n' + str(self.destination))
        plt.savefig(str(index) + ".png")
        plt.clf()