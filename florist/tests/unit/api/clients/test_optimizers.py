from unittest.mock import Mock, patch

from florist.api.clients.optimizers import Optimizer


def test_optimizer_list():
    assert Optimizer.list() == [Optimizer.SGD.value, Optimizer.ADAM_W.value]


@patch("florist.api.clients.optimizers.torch")
def test_optimizer_get_sgd(mock_torch: Mock):
    test_model_parameters = Mock()
    test_optimizer = "test-optimizer"
    mock_torch.optim.SGD.return_value = test_optimizer

    optimizer = Optimizer.get(Optimizer.SGD, test_model_parameters)

    assert optimizer == test_optimizer
    mock_torch.optim.SGD.assert_called_with(test_model_parameters, lr=0.001, momentum=0.9)


@patch("florist.api.clients.optimizers.torch")
def test_optimizer_get_adam_w(mock_torch: Mock):
    test_model_parameters = Mock()
    test_optimizer = "test-optimizer"
    mock_torch.optim.AdamW.return_value = test_optimizer

    optimizer = Optimizer.get(Optimizer.ADAM_W, test_model_parameters)

    assert optimizer == test_optimizer
    mock_torch.optim.AdamW.assert_called_with(test_model_parameters, lr=0.01)
