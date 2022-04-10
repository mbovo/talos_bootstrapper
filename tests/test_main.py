from porcupine import cli
from click import testing
import pkg_resources


def test_assert_true():
    assert True


def test_main_cli():
    runner = testing.CliRunner()
    assert runner.invoke(cli.main, "").exit_code == 0


def test_main_version():
    runner = testing.CliRunner()
    result = runner.invoke(cli.main, "version")
    assert result.exit_code == 0
    assert result.stdout == f"Porcupine - Talos Linux bootstrapper v{pkg_resources.get_distribution('porcupine').version}\n"
