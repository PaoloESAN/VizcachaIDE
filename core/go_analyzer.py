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
        
        # Code snippets for common patterns
        self.snippets = {
            'fori': {
                'name': 'fori',
                'snippet': 'for i := 0; i < len; i++ {\n\t\n}',
                'doc': 'For loop with index',
                'kind': 'snippet'
            },
            'forr': {
                'name': 'forr',
                'snippet': 'for _, v := range collection {\n\t\n}',
                'doc': 'For range loop',
                'kind': 'snippet'
            },
            'forri': {
                'name': 'forri',
                'snippet': 'for i, v := range collection {\n\t\n}',
                'doc': 'For range loop with index',
                'kind': 'snippet'
            },
            'forw': {
                'name': 'forw',
                'snippet': 'for condition {\n\t\n}',
                'doc': 'While-style for loop',
                'kind': 'snippet'
            },
            'ife': {
                'name': 'ife',
                'snippet': 'if err != nil {\n\treturn err\n}',
                'doc': 'If error check',
                'kind': 'snippet'
            },
            'iferr': {
                'name': 'iferr',
                'snippet': 'if err != nil {\n\tlog.Fatal(err)\n}',
                'doc': 'If error with log.Fatal',
                'kind': 'snippet'
            },
        }
        
        # Common Go standard library packages for import suggestions
        self.stdlib_packages = [
            ('fmt', 'Package fmt implements formatted I/O'),
            ('os', 'Package os provides a platform-independent interface to operating system functionality'),
            ('io', 'Package io provides basic interfaces to I/O primitives'),
            ('strings', 'Package strings implements simple functions to manipulate UTF-8 encoded strings'),
            ('strconv', 'Package strconv implements conversions to and from string representations'),
            ('time', 'Package time provides functionality for measuring and displaying time'),
            ('math', 'Package math provides basic constants and mathematical functions'),
            ('bufio', 'Package bufio implements buffered I/O'),
            ('bytes', 'Package bytes implements functions for the manipulation of byte slices'),
            ('encoding/json', 'Package json implements encoding and decoding of JSON'),
            ('encoding/xml', 'Package xml implements a simple XML 1.0 parser'),
            ('net/http', 'Package http provides HTTP client and server implementations'),
            ('net/url', 'Package url parses URLs and implements query escaping'),
            ('path', 'Package path implements utility routines for manipulating slash-separated paths'),
            ('path/filepath', 'Package filepath implements utility routines for manipulating filename paths'),
            ('regexp', 'Package regexp implements regular expression search'),
            ('sort', 'Package sort provides primitives for sorting slices and user-defined collections'),
            ('sync', 'Package sync provides basic synchronization primitives'),
            ('errors', 'Package errors implements functions to manipulate errors'),
            ('log', 'Package log implements a simple logging package'),
            ('flag', 'Package flag implements command-line flag parsing'),
            ('context', 'Package context defines the Context type'),
            ('crypto/md5', 'Package md5 implements the MD5 hash algorithm'),
            ('crypto/sha256', 'Package sha256 implements the SHA224 and SHA256 hash algorithms'),
            ('database/sql', 'Package sql provides a generic interface around SQL databases'),
            ('html/template', 'Package template implements data-driven templates for HTML output'),
            ('text/template', 'Package template implements data-driven templates for text output'),
            ('reflect', 'Package reflect implements run-time reflection'),
            ('runtime', 'Package runtime contains operations that interact with Go runtime system'),
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
        # Don't check gopls at initialization - it's slow and we don't use it
        self.gopls_available = False

    def _check_gopls(self):
        """Check if gopls is available"""
        # Disabled - not currently used and slows down initialization
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
        
        # Check if we're in an import context
        if self._is_in_import_context(code, cursor_position):
            # Get the partial package name being typed
            word_start = cursor_position
            # Include / for package paths
            while word_start > 0 and (code[word_start - 1].isalnum() or code[word_start - 1] in ('_', '/')):
                word_start -= 1
            
            prefix = code[word_start:cursor_position].lower()
            completions = []
            
            # Show standard library packages
            for pkg_name, pkg_doc in self.stdlib_packages:
                if pkg_name.lower().startswith(prefix) or prefix in pkg_name.lower():
                    completions.append({
                        'name': pkg_name,
                        'signature': '',
                        'doc': pkg_doc,
                        'kind': 'package'
                    })
            
            # Sort by relevance
            completions.sort(key=lambda x: (not x['name'].lower().startswith(prefix), x['name'].lower()))
            return completions[:30]
        
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
            
            # Show snippets
            for snippet_key, snippet_data in self.snippets.items():
                if snippet_key.startswith(prefix) or snippet_data['name'].startswith(prefix):
                    completions.append({
                        'name': snippet_data['name'],
                        'signature': '',
                        'doc': snippet_data['doc'],
                        'kind': 'snippet',
                        'snippet': snippet_data['snippet']
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
    
    def _is_in_import_context(self, code, cursor_position):
        """Check if cursor is within an import statement
        
        Args:
            code: Full code text
            cursor_position: Current cursor position
            
        Returns:
            True if cursor is in import context, False otherwise
        """
        # Look backwards to find if we're in an import statement
        # Search for import keyword and opening parenthesis or quote
        
        # Get text before cursor
        text_before = code[:cursor_position]
        
        # Find the last import statement
        last_import = text_before.rfind('import')
        if last_import == -1:
            return False
        
        # Get text from import to cursor
        text_from_import = code[last_import:cursor_position]
        
        # Check if we're in parentheses import block: import ( ... )
        open_paren = text_from_import.find('(')
        if open_paren != -1:
            # Check if there's a closing paren before cursor
            close_paren = text_from_import.find(')', open_paren)
            if close_paren == -1:  # No closing paren yet
                # We're inside the import block
                return True
        
        # Check for single line import: import "..."
        # Make sure we're after 'import' and before any newline
        remaining = text_from_import[6:].lstrip()  # Skip 'import'
        if '\n' not in remaining:
            # We're on the same line as import
            # Check if we're inside quotes or ready to type
            if '"' in remaining:
                # Count quotes to see if we're inside
                quote_count = remaining.count('"')
                if quote_count == 1 or quote_count % 2 == 1:
                    # Odd number of quotes, we're inside a string
                    return True
            return True
        
        return False

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