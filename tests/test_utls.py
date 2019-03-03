import pytest

from app.utils import (
    hasName,
    isFloat,
    isInt,
    file_ext_checker,
    hasValues,
    key_preferred,
    key_checkboxes,
)

has_name_fail = ["", [], {}, None]
has_name_pass = ["1", [1], {1: 1}]


@pytest.mark.parametrize("fail_value", has_name_fail)
def test_has_name_fail(fail_value):
    assert not hasName(fail_value)


@pytest.mark.parametrize("pass_value", has_name_pass)
def test_has_name_pass(pass_value):
    assert hasName(pass_value)


@pytest.mark.parametrize("fail_value", has_name_fail)
def test_has_values_fail(fail_value):
    assert not hasValues(fail_value)


@pytest.mark.parametrize("pass_value", has_name_pass)
def test_has_values_pass(pass_value):
    assert hasValues(pass_value)


is_float_fail = ["a", False, None]
is_float_pass = ["1", 1.1, "1.1", 1]


@pytest.mark.parametrize("fail_value", is_float_fail)
def test_is_float_fail(fail_value):
    assert not isFloat(fail_value)


@pytest.mark.parametrize("pass_value", is_float_pass)
def test_is_float_pass(pass_value):
    assert isFloat(pass_value)


is_int_fail = ["a", 1.1, "1.1", False, None]
is_int_pass = ["1", 1]


@pytest.mark.parametrize("fail_value", is_int_fail)
def test_is_int_fail(fail_value):
    assert not isInt(fail_value)


@pytest.mark.parametrize("pass_value", is_int_pass)
def test_is_int_pass(pass_value):
    assert isInt(pass_value)


file_ext_checker_fail = [("name", " "), ("name.text", "txt")]
file_ext_checker_pass = [("name.tXt", "TXT"), ("name.txt", ".txt"), ("name", "")]


@pytest.mark.parametrize("fail_value", file_ext_checker_fail)
def test_file_ext_checker_fail(fail_value):
    assert not file_ext_checker(fail_value[0], fail_value[1])


@pytest.mark.parametrize("pass_value", file_ext_checker_pass)
def test_file_ext_checker_pass(pass_value):
    assert file_ext_checker(pass_value[0], pass_value[1])


key_preferred_fail = ["fail", "fail_PREFERRED"]
key_preferred_pass = ["pass_preferred", "preferred"]


@pytest.mark.parametrize("fail_value", key_preferred_fail)
def test_key_preferred_fail(fail_value):
    assert not key_preferred(fail_value)


@pytest.mark.parametrize("pass_value", key_preferred_pass)
def test_key_preferred_pass(pass_value):
    assert key_preferred(pass_value)


key_checkboxes_fail = ["fail", "fail_CHECKBOXES"]
key_checkboxes_pass = ["pass_checkboxes", "checkboxes"]


@pytest.mark.parametrize("fail_value", key_checkboxes_fail)
def test_key_checkboxes_fail(fail_value):
    assert not key_checkboxes(fail_value)


@pytest.mark.parametrize("pass_value", key_checkboxes_pass)
def test_key_checkboxes_pass(pass_value):
    assert key_checkboxes(pass_value)
