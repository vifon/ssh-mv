#!/usr/bin/env python3

__author__ = "Wojciech Siewierski"
__version__ = "1.0.0"
__license__ = "GPL3"

import argparse
import os.path
import shlex

import paramiko

LOCAL_ROOT = "/media/NAS"
REMOTE_ROOT = "/share/MD0_DATA"
REMOTE_HOST = "example.com"


class InvalidFileException(Exception):
    pass


def deprefix(path):
    root = os.path.join(LOCAL_ROOT, "")
    if path.startswith(root):
        return path[len(root):]
    else:
        raise InvalidFileException('"{}" not in "{}"'.format(path, root))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='count',
        help="Increase the verbosity level.  May be passed multiple times.",
    )
    parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help="Do not actually move the files.  Makes sense only with --verbose!",
    )
    parser.add_argument('source_paths', nargs='+')
    parser.add_argument('target_path')
    args = parser.parse_args()

    files = args.source_paths + [args.target_path]
    for n, path in enumerate(files):
        path = os.path.join(
            REMOTE_ROOT,
            deprefix(
                os.path.abspath(path)
            )
        )
        files[n] = path

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(REMOTE_HOST)

    if args.verbose == 1:
        for x in files:
            print(x)
    elif args.verbose == 2:
        stdin, stdout, stderr = ssh.exec_command(r"printf '<%s>\n' {}".format(
            " ".join(shlex.quote(x) for x in files)
        ))
        stdout.channel.set_combine_stderr(True)
        print(stdout.read().decode(), end='')
        stdout.channel.recv_exit_status()

    if not args.dry_run:
        ssh.exec_command(r"mv -- {}".format(
            " ".join(shlex.quote(x) for x in files)
        ))
        stdout.channel.set_combine_stderr(True)
        stdout.read()
        stdout.channel.recv_exit_status()


if __name__ == '__main__':
    from sys import argv
    main(argv)
