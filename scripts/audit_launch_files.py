import os
import ast

def find_launch_files(root_dir):
    launch_files = []
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith('.launch.py') or filename.endswith('_launch.py'):
                launch_files.append(os.path.join(root, filename))
    return launch_files

def extract_arguments_from_content(content):
    args = {}
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'DeclareLaunchArgument':
                    _process_declare_arg(node, args)
                elif isinstance(node.func, ast.Attribute) and node.func.attr == 'DeclareLaunchArgument':
                    _process_declare_arg(node, args)
    except Exception as e:
        print(f"Error parsing content: {e}")
    return args

def extract_nodes_from_content(content):
    nodes = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                is_node = False
                if isinstance(node.func, ast.Name) and node.func.id == 'Node':
                    is_node = True
                elif isinstance(node.func, ast.Attribute) and node.func.attr == 'Node':
                    is_node = True
                
                if is_node:
                    _process_node(node, nodes)
    except Exception as e:
        print(f"Error parsing content for nodes: {e}")
    return nodes

def _process_node(node, nodes):
    package = None
    executable = None
    name = None
    
    for keyword in node.keywords:
        if keyword.arg == 'package':
            if isinstance(keyword.value, ast.Constant):
                package = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                package = keyword.value.s
        elif keyword.arg == 'executable':
            if isinstance(keyword.value, ast.Constant):
                executable = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                executable = keyword.value.s
        elif keyword.arg == 'name':
            if isinstance(keyword.value, ast.Constant):
                name = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                name = keyword.value.s
    
    if package or executable:
        nodes.append({
            'package': package,
            'executable': executable,
            'name': name
        })


def _process_declare_arg(node, args):
    name = None
    default = None
    description = None
    
    # Check positional arguments
    if len(node.args) > 0 and isinstance(node.args[0], ast.Constant):
        name = node.args[0].value
    elif len(node.args) > 0 and isinstance(node.args[0], ast.Str): # Legacy python < 3.8
        name = node.args[0].s

    # Check keyword arguments
    for keyword in node.keywords:
        if keyword.arg == 'name':
            if isinstance(keyword.value, ast.Constant):
                name = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                name = keyword.value.s
        elif keyword.arg == 'default_value':
            if isinstance(keyword.value, ast.Constant):
                default = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                default = keyword.value.s
        elif keyword.arg == 'description':
            if isinstance(keyword.value, ast.Constant):
                description = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                description = keyword.value.s
    
    if name:
        args[name] = {
            'default': default,
            'description': description
        }

if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else 'src'
    files = find_launch_files(root)
    for f in sorted(files):
        print(f"File: {f}")
        try:
            with open(f, 'r') as file_obj:
                content = file_obj.read()
                args = extract_arguments_from_content(content)
                nodes = extract_nodes_from_content(content)
                
                if args:
                    print("  Arguments:")
                    for name, details in args.items():
                        print(f"    - {name}: default='{details['default']}', desc='{details['description']}'")
                else:
                    print("  Arguments: None detected (or static)")
                
                if nodes:
                    print("  Nodes:")
                    for node in nodes:
                        print(f"    - Package: {node['package']}, Executable: {node['executable']}, Name: {node['name']}")
                else:
                    print("  Nodes: None detected (or opaque)")
                    
        except Exception as e:
            print(f"  Error reading file: {e}")
        print("-" * 40)
