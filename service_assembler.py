from typing import Dict, List

def regroup_functions_by_service(classified: Dict[str, List[Dict[str, str]]]) -> Dict[str, Dict[str, List[str]]]:
    services = {}
    for filename, entries in classified.items():
        for entry in entries:
            service = entry['service']
            if service not in services:
                services[service] = {}
            if filename not in services[service]:
                services[service][filename] = []
            services[service][filename].append(entry['function'])
    return services

def stitch_functions(functions: List[str]) -> str:
    return '\n\n'.join(functions)

def assemble_service_code(service_map: Dict[str, Dict[str, List[str]]]) -> Dict[str, Dict[str, str]]:
    output = {}
    for service, files in service_map.items():
        output[service] = {}
        for filename, function_list in files.items():
            output[service][filename] = stitch_functions(function_list)
    return output
