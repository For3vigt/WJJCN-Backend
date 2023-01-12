import main
import pytest


def test_Compare_Texts():
    assert "Hello World, this is a test" == main.compareTexts("Hello World, this is a test", "this is a test")

def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4