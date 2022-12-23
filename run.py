#!/usr/bin/env python3
import os
import subprocess
import irrhound.irrhound
from typing import *

def main():
    with open("input_asns") as asn_file:
        input_rule_segments = map(process_input_line, asn_file)
        combined_input = " or ".join(input_rule_segments)
    with open("output_asns") as asn_file:
        output_rule_segments = map(process_output_line, asn_file)
        combined_output = " or ".join(output_rule_segments)

def process_input_line(line):
    line = line.rstrip()
    print(f"Processing {line}")
    return generate_rule_segment(*line.split(" "))

def process_output_line(line):
    line = line.rstrip()
    return generate_rule_segment(*line.split(" "), direction="bgp-output-local-as")

def generate_rule_segment(asn: str, asmacro: str, asmacro6: Optional[str] = None, direction: str = "bgp-input-remote-as") -> str:
    """
    Generate a rule for rejecting bad routes for a given ASN. In most cases the direction should be either
    - bgp-input-remote-as
    - bgp-output-local-as
    """
    if asmacro6 is None:
        asmacro6 = asmacro
    routes = irrhound.irr_hunt_routes(asn, asmacro, asmacro6)
    return routes_to_rule_segment(asn, direction, routes['routes'])

def routes_to_rule_segment(asn: str, direction: str, routes: dict) -> str:
    def extract_cidrs(routes):
        return set(map(lambda route: route['cidr'], routes))
    def route_to_segment(cidr):
        return f"dst in {cidr}"
    cidrs = extract_cidrs(routes)
    route_matches_segments = map(route_to_segment, cidrs)
    route_matches = " or ".join(route_matches_segments)
    rule = f"( {direction} == {asn} and ( {route_matches} ) )"
    return rule
    
if __name__ == '__main__':
    main()
