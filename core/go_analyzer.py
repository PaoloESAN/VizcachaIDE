"""
Go code analyzer for autocomplete suggestions
"""

import subprocess
import json
import os
import re


class GoAnalyzer:
    """Analyzer for Go code to provide autocomplete suggestions"""

    def __init__(self):
        # Built-in Go keywords
        self.keywords = [
            'break', 'case', 'chan', 'const', 'continue', 'default', 'defer',
            'else', 'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import',
            'interface', 'map', 'package', 'range', 'return', 'select', 'struct',
            'switch', 'type', 'var'
        ]

        # Built-in types
        self.types = [
            'bool', 'byte', 'complex64', 'complex128', 'error', 'float32', 'float64',
            'int', 'int8', 'int16', 'int32', 'int64', 'rune', 'string',
            'uint', 'uint8', 'uint16', 'uint32', 'uint64', 'uintptr'
        ]

        # Built-in functions
        self.builtins = {
            'append': {'signature': '(slice, elements...)', 'doc': 'Appends elements to the end of a slice and returns the updated slice.'},
            'cap': {'signature': '(v Type)', 'doc': 'Returns the capacity of v, according to its type.'},
            'close': {'signature': '(c chan<- Type)', 'doc': 'Closes a channel, indicating that no more values will be sent.'},
            'complex': {'signature': '(r, i FloatType)', 'doc': 'Constructs a complex value from floating-point real and imaginary parts.'},
            'copy': {'signature': '(dst, src []Type)', 'doc': 'Copies elements from source slice to destination slice.'},
            'delete': {'signature': '(m map[Type]Type1, key Type)', 'doc': 'Deletes the element with the specified key from the map.'},
            'imag': {'signature': '(c ComplexType)', 'doc': 'Returns the imaginary part of the complex number.'},
            'len': {'signature': '(v Type)', 'doc': 'Returns the length of v, according to its type.'},
            'make': {'signature': '(Type, size ...IntegerType)', 'doc': 'Allocates and initializes an object of type slice, map, or channel.'},
            'new': {'signature': '(Type)', 'doc': 'Allocates memory for a variable of the given type and returns a pointer to it.'},
            'panic': {'signature': '(v interface{})', 'doc': 'Stops normal execution of the current goroutine.'},
            'print': {'signature': '(args ...Type)', 'doc': 'Prints arguments to standard error.'},
            'println': {'signature': '(args ...Type)', 'doc': 'Prints arguments to standard error with spaces and newline.'},
            'real': {'signature': '(c ComplexType)', 'doc': 'Returns the real part of the complex number.'},
            'recover': {'signature': '()', 'doc': 'Regains control of a panicking goroutine.'},
        }

        # Common standard library packages and their functions
        self.stdlib = {
            'fmt': {
                'Print': 'Formats using the default formats and writes to standard output.',
                'Println': 'Formats using the default formats, adds newline, writes to standard output.',
                'Printf': 'Formats according to a format specifier and writes to standard output.',
                'Sprint': 'Formats using the default formats and returns the resulting string.',
                'Sprintf': 'Formats according to a format specifier and returns the resulting string.',
                'Scan': 'Scans text read from standard input.',
                'Scanf': 'Scans text read from standard input with format.',
                'Scanln': 'Scans text read from standard input until newline.',
            },
            'strings': {
                'Contains': 'Reports whether substr is within s.',
                'HasPrefix': 'Tests whether string begins with prefix.',
                'HasSuffix': 'Tests whether string ends with suffix.',
                'Index': 'Returns the index of the first instance of substr in s.',
                'Join': 'Concatenates the elements of a to create a single string.',
                'Replace': 'Returns a copy of s with replacements.',
                'Split': 'Slices s into all substrings separated by sep.',
                'ToLower': 'Returns s with all Unicode letters mapped to lowercase.',
                'ToUpper': 'Returns s with all Unicode letters mapped to uppercase.',
                'Trim': 'Returns a slice of s with leading and trailing cutset removed.',
                'TrimSpace': 'Returns a slice of s with leading and trailing whitespace removed.',
            },
            'strconv': {
                'Atoi': 'Converts string to int.',
                'Itoa': 'Converts int to string.',
                'ParseBool': 'Parses a string to boolean.',
                'ParseFloat': 'Parses a string to float64.',
                'ParseInt': 'Parses a string to int64.',
                'FormatBool': 'Formats a boolean to string.',
                'FormatFloat': 'Formats a float to string.',
                'FormatInt': 'Formats an int to string.',
            },
            'os': {
                'Create': 'Creates or truncates the named file.',
                'Open': 'Opens the named file for reading.',
                'Exit': 'Causes the program to exit with the given status code.',
                'Getenv': 'Retrieves the value of the environment variable.',
                'Setenv': 'Sets the value of the environment variable.',
                'Remove': 'Removes the named file or directory.',
                'Mkdir': 'Creates a new directory with the specified name.',
                'ReadFile': 'Reads the named file and returns the contents.',
                'WriteFile': 'Writes data to the named file.',
            },
            'io': {
                'Copy': 'Copies from src to dst until EOF.',
                'ReadAll': 'Reads from r until EOF and returns the data.',
                'WriteString': 'Writes the contents of the string s to w.',
            },
            'time': {
                'Now': 'Returns the current local time.',
                'Sleep': 'Pauses the current goroutine for the specified duration.',
                'Since': 'Returns the time elapsed since t.',
                'Parse': 'Parses a formatted string and returns the time value.',
                'Format': 'Formats time according to a layout.',
            },
            'math': {
                'Abs': 'Returns the absolute value of x.',
                'Ceil': 'Returns the least integer value greater than or equal to x.',
                'Floor': 'Returns the greatest integer value less than or equal to x.',
                'Max': 'Returns the larger of x or y.',
                'Min': 'Returns the smaller of x or y.',
                'Pow': 'Returns x**y, the base-x exponential of y.',
                'Sqrt': 'Returns the square root of x.',
                'Round': 'Returns the nearest integer, rounding half away from zero.',
            },
            'encoding/json': {
                'Marshal': 'Returns the JSON encoding of v.',
                'Unmarshal': 'Parses the JSON-encoded data and stores the result.',
            },
            'net/http': {
                'Get': 'Issues a GET to the specified URL.',
                'Post': 'Issues a POST to the specified URL.',
                'ListenAndServe': 'Listens on the TCP network address and calls Serve.',
            },
            'bufio': {
                'NewReader': 'Returns a new Reader.',
                'NewScanner': 'Returns a new Scanner to read from r.',
            },
        }
        
        # User-defined elements
        self.imported_packages = {}
        self.user_defined_vars = set()
        self.user_defined_funcs = {}
        self.gopls_available = self._check_gopls()

    def _check_gopls(self):
        """Check if gopls is available"""
        try:
            subprocess.run(['gopls', 'version'], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def _analyze_code(self, code):
        """Analyze code to extract imports, variables, and functions"""
        self.imported_packages = {}
        self.user_defined_vars = set()
        self.user_defined_funcs = {}
        
        # Parse imports (single line, aliased, and multi-line blocks)
        import_pattern = r'import\s+(?:"([^"]+)"|(\w+)\s+"([^"]+)"|\(([^)]+)\))'
        for match in re.finditer(import_pattern, code, re.MULTILINE):
            if match.group(1):
                # Simple import: import "fmt"
                pkg_path = match.group(1)
                pkg_name = pkg_path.split('/')[-1]
                self.imported_packages[pkg_name] = pkg_path
            elif match.group(2):
                # Aliased import: import f "fmt"
                alias = match.group(2)
                pkg_path = match.group(3)
                self.imported_packages[alias] = pkg_path
            elif match.group(4):
                # Multi-line import block
                imports_block = match.group(4)
                for line in imports_block.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('//'):
                        pkg_match = re.match(r'(?:(\w+)\s+)?"([^"]+)"', line)
                        if pkg_match:
                            alias = pkg_match.group(1)
                            pkg_path = pkg_match.group(2)
                            if alias:
                                self.imported_packages[alias] = pkg_path
                            else:
                                pkg_name = pkg_path.split('/')[-1]
                                self.imported_packages[pkg_name] = pkg_path
        
        # Parse variable declarations (var, const)
        var_pattern = r'(?:var|const)\s+(\w+)'
        for match in re.finditer(var_pattern, code):
            self.user_defined_vars.add(match.group(1))
        
        # Parse short variable declarations (:=)
        short_var_pattern = r'(\w+)\s*:='
        for match in re.finditer(short_var_pattern, code):
            var_name = match.group(1)
            if var_name != '_':
                self.user_defined_vars.add(var_name)
        
        # Parse function declarations
        func_pattern = r'func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, code):
            func_name = match.group(1)
            params = match.group(2)
            self.user_defined_funcs[func_name] = params

    def get_completions(self, code, cursor_position, file_path=None):
        """Get autocomplete suggestions for the given code and cursor position

        Args:
            code: Full code text
            cursor_position: Current cursor position in the code
            file_path: Path to the current file (optional)

        Returns:
            List of completion dictionaries
        """
        # Analyze the code first
        self._analyze_code(code)
        
        # Get the word being typed
        word_start = cursor_position
        while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] == '_'):
            word_start -= 1

        prefix = code[word_start:cursor_position].lower()
        completions = []

        # Check if we're after a package name (e.g., "fmt.")
        package_match = self._get_package_context(code, cursor_position)
        if package_match:
            package_name = package_match
            
            # Check standard library
            if package_name in self.stdlib:
                for method, doc in self.stdlib[package_name].items():
                    if method.lower().startswith(prefix):
                        completions.append({
                            'name': method,
                            'signature': f'{package_name}.{method}(...)',
                            'doc': doc,
                            'kind': 'function'
                        })
            # Check imported packages
            elif package_name in self.imported_packages:
                pkg_path = self.imported_packages[package_name]
                if pkg_path in self.stdlib:
                    for method, doc in self.stdlib[pkg_path].items():
                        if method.lower().startswith(prefix):
                            completions.append({
                                'name': method,
                                'signature': f'{package_name}.{method}(...)',
                                'doc': doc,
                                'kind': 'function'
                            })
        else:
            # Show keywords
            for keyword in self.keywords:
                if keyword.startswith(prefix):
                    completions.append({
                        'name': keyword,
                        'signature': '',
                        'doc': f'Go keyword',
                        'kind': 'const'
                    })

            # Show types
            for type_name in self.types:
                if type_name.startswith(prefix):
                    completions.append({
                        'name': type_name,
                        'signature': '',
                        'doc': f'Built-in type',
                        'kind': 'type'
                    })

            # Show built-in functions
            for func_name, func_info in self.builtins.items():
                if func_name.startswith(prefix):
                    completions.append({
                        'name': func_name,
                        'signature': func_info['signature'],
                        'doc': func_info['doc'],
                        'kind': 'function'
                    })

            # Show user-defined variables
            for var_name in self.user_defined_vars:
                if var_name.lower().startswith(prefix):
                    completions.append({
                        'name': var_name,
                        'signature': '',
                        'doc': 'User-defined variable',
                        'kind': 'variable'
                    })

            # Show user-defined functions
            for func_name, params in self.user_defined_funcs.items():
                if func_name.lower().startswith(prefix):
                    completions.append({
                        'name': func_name,
                        'signature': f'({params})',
                        'doc': 'User-defined function',
                        'kind': 'function'
                    })

            # Show imported packages
            for package in self.imported_packages.keys():
                if package.lower().startswith(prefix):
                    completions.append({
                        'name': package,
                        'signature': '',
                        'doc': f'Imported package: {self.imported_packages[package]}',
                        'kind': 'package'
                    })

        # Sort by relevance (exact prefix match first, then alphabetically)
        completions.sort(key=lambda x: (not x['name'].lower().startswith(prefix), x['name'].lower()))
        return completions[:30]  # Limit to 30 suggestions

    def _get_package_context(self, code, cursor_position):
        """Check if cursor is after a package name (e.g., 'fmt.')

        Args:
            code: Full code text
            cursor_position: Current cursor position

        Returns:
            Package name if found, None otherwise
        """
        # Look backwards for a dot
        i = cursor_position - 1
        while i >= 0 and code[i].isspace():
            i -= 1

        if i >= 0 and code[i] == '.':
            # Found a dot, get the package name before it
            end = i
            i -= 1
            while i >= 0 and (code[i].isalnum() or code[i] == '_'):
                i -= 1
            package_name = code[i + 1:end]
            return package_name
        return None