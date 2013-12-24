import os
import sys

def main():
    scriptdir = os.path.dirname(__file__)
    fn, = sys.argv[1:]
    assert fn.endswith('.mb')

    build_dir = fn[:-3]
    os.makedir(build_dir)

main()
