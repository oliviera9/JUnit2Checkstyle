#!/usr/bin/env python

import argparse
from xml.dom import minidom
from xml.parsers.expat import ExpatError

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=argparse.FileType('r'))
    parser.add_argument("output", type=argparse.FileType('w'))
    args = parser.parse_args()

    try:
        input = minidom.parse(args.input)
    except ExpatError:
        print "%s cannot be correctly parsed" % args.input
        exit(1)

    impl = minidom.getDOMImplementation()
    output = impl.createDocument(None, "checkstyle", None)
    errors = input.getElementsByTagName('testcase')
    top_element = output.documentElement
    top_element.setAttribute("version", "4.3")
    files = {}
    for e in errors:
        filename = e.getAttribute('classname')
        if filename in files.keys():
            element = files[filename]
        else:
            element = output.createElement('file')
            element.setAttribute('name', filename)
            top_element.appendChild(element)
            files[filename] = element
        try:
            in_error = e.getElementsByTagName('failure')[0]
        except IndexError:
            continue

        f, line, column, message = in_error.getAttribute('message').split(':')
        type = in_error.getAttribute('type')
        out_error = output.createElement("error")
        out_error.setAttribute('line', line)
        out_error.setAttribute('column', column)
        if type[0] == "E":  # check if there is an error or a warning
            severity = "error"
        else:
            severity = "warning"
        out_error.setAttribute('severity', severity)
        out_error.setAttribute('message', message)
        out_error.setAttribute('source', "lua.rules.%s" % type)

        element.appendChild(out_error)

    args.output.write(output.toprettyxml(encoding='utf-8'))

    args.input.close()
    args.output.close()
