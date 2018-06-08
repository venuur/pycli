from argparse import ArgumentParser

import sys
import inspect

class _CliApplication:
    def __init__(self):
        self._parser = ArgumentParser()
        self._parser.add_argument(
            '--batch', '-b',
            help='Run application on batch file with each line containing arguments for this application.'
        )
        self._internal_argnames = {'_command'}
        self._subparser = self._parser.add_subparsers(
            dest='_command',
            help='Function to call.'
        )
        self._command_parsers = list()
        self._command_funcs = dict()
        self._command_func_args = dict()

    @staticmethod
    def _parse_docstring(func):
        func_doc, arg_ret = func.__doc__.split('Args:')
        func_doc = func_doc.strip()

        arg_raw, ret_raw = arg_ret.split('Returns:')

        arg_strs = [s.strip() for s in arg_raw.strip().split('\n')]
        arg_parts = dict()
        for arg in arg_strs:
            a_name_type, a_desc = arg.split(':')
            a_desc = a_desc.strip()

            a_name, a_type = a_name_type.split()
            a_name = a_name.strip()
            a_type = a_type.strip()
            arg_parts[a_name] = {
                'name': a_name,
                'type': a_type,
                'desc': a_desc
            }

        ret_type, ret_desc = ret_raw.strip().split(':')
        ret_type = ret_type.strip()
        ret_desc = ret_desc.strip()
        ret_parts = {
            'type': ret_type,
            'desc': ret_desc
        }

        return {
            'func': func_doc,
            'args': arg_parts,
            'ret':  ret_parts
        }

    def _add_func_subparser(self, func):
        doc = self._parse_docstring(func)

        command = self._subparser.add_parser(
            func.__name__,
            description=' '.join([
                doc['func'],
                'Returns ' +
                doc['ret']['desc'][0].lower() +
                doc['ret']['desc'][1:]]))
        self._command_funcs[func.__name__] = func
        func_args = self._command_func_args.get(func.__name__, set())
        parameters = inspect.signature(func).parameters
        for p in parameters:
            command.add_argument(
                p,
                help=doc['args'][p]['desc']
            )
            func_args.add(p)
            print('DEBUG', command)
        self._command_parsers.append(command)

    def run(self, argstr:str=None):
        if argstr is None:
            args = self._parser.parse_args()
        else:
            args = self._parser.parse_args(argstr.split())

        if args.batch is not None:
            self._run_batch(args.batch)
        else:
            self._run_single(argstr)

    def _run_single(self, argstr):
        if argstr is None:
            args = self._parser.parse_args()
        else:
            args = self._parser.parse_args(argstr.split())

        func_kwargs = self._command_func_args[args._command]
        kwargs = {
            argname: value
            for argname, value in args.__dict__.items()
            if argname in func_kwargs
        }
        print(self._command_funcs[args._command](**kwargs), file=sys.stdout)

    def _run_batch(self, batchfile:str=None):
        if str is not None:
            with open(batchfile, 'r') as batchargs:
                for argstr in batchargs:
                    self._run_single(argstr)
        else:
            for argstr in sys.stdin:
                self._run_single(argstr)

application = _CliApplication()


def add_cli(func):
    application._add_func_subparser(func)
    return func

def run_application(argstr=None):
    application.run(argstr)
