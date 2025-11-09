from datetime import datetime
import sys, os

def getPathAndFilename():
    """
    :returns: a tuple with [0] the full path including
              filename of the script being run as well
              as [1] the path including filename
              starting with the directory that the
              script is in.
    """

    return (os.path.abspath(sys.argv[0]).split('/'),
            '/'.join(os.path.abspath(sys.argv[0]).split('/')[-2:])
            )

def count_string_lines(s):
    return len(s.split('\n'))

def multiline_indent(s, num_spaces):
    s2 = ''
    s = [(num_spaces * ' ') + line.lstrip() for line in s.split('\n')]
    for item in s:
       s2 = s2 + item + '\n' 
    return s2

def tprint(message, multiline_header = '', use_as_method=1):

    bullet = '> '
    stamp = str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    separator = ' | '
    tab = '\t'

    #if a non-string type is passed (e.g. a dataframe, list, etc.)
    #then convert the param value to a string
    if type(message) is not str:
        message = str(message)

    #if the string is multiline, then add the header and pad the
    #string with 27 spaces in order to line it up with a normal
    #single line message.  This is useful for printing df output
    if count_string_lines(message) > 1:
        message = multiline_header + '\n\n' + multiline_indent(message, 27)

    #print the output by default
    if use_as_method==1:
        print(bullet, stamp, separator, message)

    #the return will not be needed unless the user passes
    #use_as_method=0 (actually, any value other than 1)
    return bullet + stamp + separator + message
