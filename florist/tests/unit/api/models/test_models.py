from florist.api.models.models import Model
from florist.api.models.mnist import MnistNet


def test_get_model_class():
    assert Model.MNIST.get_model_class() == MnistNet


def test_list():
    assert Model.list() == [Model.MNIST.value]
