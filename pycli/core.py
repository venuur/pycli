from argparse import ArgumentParser
from functools import partial

import pandas as pd

import sys
import inspect

class _CliApplication:
    _default_command_writer = partial(print, file=sys.stdout)
    _special_arg_types = {
        pd.DataFrame: pd.read_csv
    }

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
        self._command_parsers = dict()
        self._command_funcs = dict()
        self._command_func_args = dict()
        self._command_writer = dict()
        self._command_writer_args = dict()

    def _add_func_subparser(self, func, output=None):
        doc = _parse_docstring(func)
        func_types = func.__annotations__
        func_name = func.__name__

        command = self._subparser.add_parser(
            func_name,
            description=' '.join([
                doc['func'],
                'Returns ' +
                doc['ret']['desc'][0].lower() +
                doc['ret']['desc'][1:]]))
        self._command_funcs[func_name] = func
        func_args = self._command_func_args.setdefault(func_name, set())
        parameters = inspect.signature(func).parameters
        for p in parameters:
            p_type = {
                'type': self._special_arg_types.get(t, t)
                for name, t in func_types.items()
                if name == p
            }
            print('DEBUG p_type', p_type)
            command.add_argument(
                p,
                help=doc['args'][p]['desc'],
                **p_type
            )
            func_args.add(p)
            print('DEBUG', command)

        if output is None:
            self._command_writer[func_name] = self._default_command_writer
            self._command_writer_args[func_name] = set()
        elif output == 'plot':
            self._command_writer[func_name] = _plot_saver
            command.add_argument(
                '--filename', '-f',
                dest='_filename',
                help='Filename to save plot to.'
            )
            self._command_writer_args[func_name] = {'_filename'}

        self._command_parsers[func_name] = command

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
        func_ret = self._command_funcs[args._command](**kwargs)
        command_writer_args = self._command_writer_args[args._command]
        writer_kwargs = {
            argname: value
            for argname, value in args.__dict__.items()
            if argname in command_writer_args
        }
        self._command_writer[args._command](func_ret)

    def _run_batch(self, batchfile:str=None):
        if str is not None:
            with open(batchfile, 'r') as batchargs:
                for argstr in batchargs:
                    self._run_single(argstr)
        else:
            for argstr in sys.stdin:
                self._run_single(argstr)


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
        'ret': ret_parts
    }


def _plot_saver(void_ret, filename='plot.png'):
    from matplotlib.pyplot import savefig

    savefig(filename)


def add_cli(output=None):
    def _add_cli(func):
        application._add_func_subparser(func, output=output)

    return _add_cli

def run_application(argstr=None):
    application.run(argstr)


application = _CliApplication()


