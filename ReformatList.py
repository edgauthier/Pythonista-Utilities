#coding: utf-8
import clipboard
import re
import console

# Match a line of text and break it apart into three pieces
# Group 1 - Leading whitespace
#           ^(\s*)
# Group 2 - An optional markdown list prefix: a number followed
#           by a period, or an unordered list marker (-, +, or *),
#           followed by whitespace.
#           (\d+\.\s+|\-\s+|\+\s+|\*\s+)?
# Group 3 - The remainder of line of text up the end of the line
#           (.*)$
LINE_REGEX = re.compile(r'^(\s*)(\d+\.\s+|\-\s+|\+\s+|\*\s+)?(.*)$')

def main():
    prefix = get_prefix()
    
    # Get the action's input (a string):
    input_string = clipboard.get()
    
    nested_list = parse_list(input_string)
    nested_list.set_prefix(prefix)
    output_string = str(nested_list).rstrip('\n')
    
    clipboard.set(output_string)
    console.alert('Clipboard Updated')

def get_prefix():
	if len(sys.argv) >= 2:
		prefix = sys.argv[1]
	else:
		prefix = 1
	return prefix

# Code based on solution provided here: 
# http://stackoverflow.com/questions/2982992/how-do-i-process-a-nested-list
def parse_list(list_string):
    # Parse a nested plain text list and return a NestedList object.
    input_lines = list_string.split('\n')
    nested_list = NestedList(None)
    # Use a stack to keep track of the current parent list item and its level
    stack = [(nested_list, -1)]
    for line in input_lines:
    	if len(line.strip()) == 0:
    		continue 
        match = LINE_REGEX.match(line)
        if not match: 
            raise ValueError('Line with unknown formatting: ' + line)
        # Current level is based on length of leading whitespace
        cur_level = len(match.group(1))
        list_item = NestedList(line)
        while True:
            parent, level = stack[-1]
            if cur_level > level: 
                break
            # Pop the list item off the stack if it's not a new parent
            # i.e. the current list item isn't a deeper level the the one 
            # on the top of the stack
            del stack[-1]
        parent.children.append(list_item)
        # Add this list item to the stack (could be a parent of the next line)
        stack.append((list_item, cur_level))
    return nested_list

class NestedList(object):

    def __init__(self, line):
        self.line = line
        self.children = []

    def __str__(self):
        output = ''
        if self.line != None:
            output = '{0}\n'.format(self.line)
        for child in self.children:
            output += '{0}'.format(child)
        return output

    def set_prefix(self, prefix):
        if self.line != None:
            self._set_prefix_for_line(prefix)
        child_prefix = prefix

        try:
            # if this is a number, reset back to 1 for the children
            int(child_prefix)
            child_prefix = 1
        except Exception:
            pass

        for child in self.children:
            child.set_prefix(child_prefix)
            try:
                # Try to increment the list counter and silently 
                # fail if the prefix isnt a number
                child_prefix += 1
            except Exception:
                pass

    def _set_prefix_for_line(self, prefix):
        try:
            # If this is a number, append a period after it
            i = int(prefix)
            prefix = '{0}.'.format(prefix)
        except:
            pass
        # Replace the list prefix with the nee prefix
        # Need to use special group syntax so as not to conflict 
        # when the prefix is a number.
        if len(prefix):
            # Append a space if we have a prefix
            prefix += ' '
        repl_string = r'\g<1>' + prefix + r'\3'
        self.line = LINE_REGEX.sub(repl_string, self.line)

main()
