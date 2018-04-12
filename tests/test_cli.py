#!/usr/bin/env python
# -*- coding: utf-8 -*-
from click.testing import CliRunner

import cli


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.check_drivers)
    assert result.exit_code == 0
    help_result = runner.invoke(cli.cli, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
