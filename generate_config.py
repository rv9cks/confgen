#!/usr/bin/env python3
import re
import configparser
from datetime import datetime


def read_source_file(filename):
    """Read source.txt and extract only digits from each line."""
    result = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            # Remove all non-digit characters
            digits_only = re.sub(r'[^0-9]', '', line)
            result.append(digits_only)
    return result


def get_user_port_value(line_data):
    """Convert line data to +7XXXXXXXXXX@ims.rt.ru format."""
    if len(line_data) >= 10:
        last_10 = line_data[-10:]
        return f"+7{last_10}@ims.rt.ru"
    return ""


def get_number_port_value(line_data):
    """Convert line data to +7XXXXXXXXXX format."""
    if len(line_data) >= 10:
        last_10 = line_data[-10:]
        return f"+7{last_10}"
    return ""


def get_passwd_port_value(line_data):
    """Convert line data to Rz_XXXXXXX$ format."""
    if len(line_data) >= 7:
        last_7 = line_data[-7:]
        return f"Rz_{last_7}$"
    return ""


def replace_templates(content, section_params, source_data):
    """Replace all templates in the content."""
    result = content
    
    # Replace $name patterns (simple variable names from config.ini)
    for key, value in section_params.items():
        pattern = f'\\${key}'
        result = re.sub(pattern, value, result)
    
    # Replace $user_port_NN patterns
    user_port_pattern = r'\$user_port_(\d{2})'
    for match in re.finditer(user_port_pattern, result):
        nn = match.group(1)
        line_num = int(nn)
        if line_num < len(source_data):
            replacement = get_user_port_value(source_data[line_num])
            result = result.replace(f'$user_port_{nn}', replacement)
    
    # Replace $number_port_NN patterns
    number_port_pattern = r'\$number_port_(\d{2})'
    for match in re.finditer(number_port_pattern, result):
        nn = match.group(1)
        line_num = int(nn)
        if line_num < len(source_data):
            replacement = get_number_port_value(source_data[line_num])
            result = result.replace(f'$number_port_{nn}', replacement)
    
    # Replace $passwd_port_NN patterns
    passwd_port_pattern = r'\$passwd_port_(\d{2})'
    for match in re.finditer(passwd_port_pattern, result):
        nn = match.group(1)
        line_num = int(nn)
        if line_num < len(source_data):
            replacement = get_passwd_port_value(source_data[line_num])
            result = result.replace(f'$passwd_port_{nn}', replacement)
    
    return result


def main():
    # Read source.txt into array (0-indexed), keeping only digits
    source_data = read_source_file('source.txt')
    
    # Read config.ini
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    
    # Read config.xml template
    with open('config.xml', 'r', encoding='utf-8') as f:
        config_xml_content = f.read()
    
    # Iterate through each section in config.ini
    for section in config.sections():
        # Get all parameters from current section
        section_params = dict(config[section])
        
        # Replace templates in config.xml content
        generated_content = replace_templates(config_xml_content, section_params, source_data)
        
        # Get hostname for filename
        hostname = section_params.get('hostname', 'unknown')
        
        # Generate timestamp
        datetime_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create output filename
        output_filename = f'{hostname}-generated-{datetime_str}.xml'
        
        # Write to output file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(generated_content)
        
        print(f'Generated: {output_filename}')


if __name__ == '__main__':
    main()
