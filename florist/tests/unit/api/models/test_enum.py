from florist.api.models.enum import Model
from florist.api.models.mnist import MnistNet


def test_class_for_model():
    assert Model.class_for_model(Model.MNIST) == MnistNet


def test_list():
    assert Model.list() == [Model.MNIST.value]
