#!/usr/bin/env python3
import os
import subprocess
import irrhound.irrhound
from typing import *
import sys

def main():
    with open("input_asns") as asn_file:
        input_rule_segments = map(process_input_line, asn_file)
        combined_input = " or ".join(input_rule_segments)
        
    with open("output_asns") as asn_file:
        output_rule_segments = map(process_output_line, asn_file)
        combined_output = " or ".join(output_rule_segments)

    input_rule = f" if ({combined_input})" + "{ accept; }"
    output_rule = f" if ({combined_output})" + "{ accept; }"
    do_update(input_rule, output_rule)

def do_update(input_rule, output_rule):
    host = os.getenv("router")
    host_port = os.getenv("router_port", "22")
    cmd = "/routing/filter/rule/export"
    current_rules_text = subprocess.check_output(
        ["ssh", f"admin@{host}", "-p" , host_port, cmd]).decode('utf-8')
    current_rules = current_rules_text.split("add chain=")
    input_indexes = []
    output_indexes = []
    # There is a firt non-rule chunk of text so start at -1
    c = -1
    for rule in current_rules:
        if "comment=input-rule" in rule:
            input_indexes.append(str(c))
        if "comment=output-rule" in rule:
            output_indexes.append(str(c))
        c = c + 1
    print(f"Going to update input {input_indexes} and {output_indexes}")
    output_numbers = ",".join(output_indexes)
    cmd=f"/routing/filter/rule/set rule=\"{output_rule}\" numbers={output_numbers}"
    subprocess.check_output(
        ["ssh", f"admin@{host}", "-p" , host_port, cmd]).decode('utf-8')
    input_numbers = ",".join(input_indexes)
    cmd=f"/routing/filter/rule/set rule=\"{input_rule}\" numbers={input_numbers}"
    subprocess.check_output(
        ["ssh", f"admin@{host}", "-p" , host_port, cmd]).decode('utf-8')



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
