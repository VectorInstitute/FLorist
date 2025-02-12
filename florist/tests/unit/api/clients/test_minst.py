from unittest.mock import Mock, patch, ANY

from florist.api.models.mnist import MnistNet
from florist.api.clients.mnist import MnistClient, MnistFedProxClient


@patch("florist.api.clients.mnist.load_mnist_data")
def test_mnist_get_data_loaders(mock_load_mnist_data: Mock):
    test_data_path = "test-data-path"
    test_device = "cpu"
    test_config = {"batch_size": 200}
    test_train_loader = "test-train-loader"
    test_val_loader = "test-val-loader"
    test_client = MnistClient(data_path=test_data_path, metrics=[], device=test_device)
    mock_load_mnist_data.return_value = (test_train_loader, test_val_loader, {})

    train_loader, val_loader = test_client.get_data_loaders(config=test_config)

    assert train_loader == test_train_loader
    assert val_loader == test_val_loader
    mock_load_mnist_data.assert_called_with(test_data_path, batch_size=test_config["batch_size"])


def test_mnist_get_model():
    test_client = MnistClient(data_path="test-data-path", metrics=[], device="cpu")

    model = test_client.get_model(config={})

    assert isinstance(model, MnistNet)


@patch("florist.api.clients.mnist.torch")
def test_mnist_get_optimizer(mock_torch: Mock):
    test_optimizer = "test-optimizer"
    mock_torch.optim.SGD.return_value = test_optimizer
    test_client = MnistClient(data_path="test-data-path", metrics=[], device="cpu")
    test_client.model = Mock()

    optimizer = test_client.get_optimizer(config={})

    assert optimizer == test_optimizer
    mock_torch.optim.SGD.assert_called_with(ANY, lr=0.001, momentum=0.9)
    test_client.model.parameters.assert_called()


@patch("florist.api.clients.mnist.torch")
def test_mnist_get_criterion(mock_torch: Mock):
    test_criterion = "test-criterion"
    mock_torch.nn.CrossEntropyLoss.return_value = test_criterion
    test_client = MnistClient(data_path="test-data-path", metrics=[], device="cpu")

    criterion = test_client.get_criterion(config={})

    assert criterion == test_criterion


@patch("florist.api.clients.mnist.load_mnist_data")
@patch("florist.api.clients.mnist.DirichletLabelBasedSampler")
def test_mnist_fedprox_get_data_loaders(mock_sampler: Mock, mock_load_mnist_data: Mock):
    test_data_path = "test-data-path"
    test_device = "cpu"
    test_config = {"batch_size": 200}
    test_train_loader = "test-train-loader"
    test_val_loader = "test-val-loader"
    test_client = MnistFedProxClient(data_path=test_data_path, metrics=[], device=test_device)
    mock_load_mnist_data.return_value = (test_train_loader, test_val_loader, {})

    train_loader, val_loader = test_client.get_data_loaders(config=test_config)

    assert train_loader == test_train_loader
    assert val_loader == test_val_loader
    mock_load_mnist_data.assert_called_with(test_data_path, test_config["batch_size"], ANY)
    mock_sampler.assert_called_with(list(range(10)), sample_percentage=0.75, beta=1)


def test_mnist_fedprox_get_model():
    test_client = MnistFedProxClient(data_path="test-data-path", metrics=[], device="cpu")

    model = test_client.get_model(config={})

    assert isinstance(model, MnistNet)


@patch("florist.api.clients.mnist.torch")
def test_mnist_fedprox_get_optimizer(mock_torch: Mock):
    test_optimizer = "test-optimizer"
    mock_torch.optim.AdamW.return_value = test_optimizer
    test_client = MnistFedProxClient(data_path="test-data-path", metrics=[], device="cpu")
    test_client.model = Mock()

    optimizer = test_client.get_optimizer(config={})

    assert optimizer == test_optimizer
    mock_torch.optim.AdamW.assert_called_with(ANY, lr=0.01)
    test_client.model.parameters.assert_called()


@patch("florist.api.clients.mnist.torch")
def test_mnist_fedprox_get_criterion(mock_torch: Mock):
    test_criterion = "test-criterion"
    mock_torch.nn.CrossEntropyLoss.return_value = test_criterion
    test_client = MnistFedProxClient(data_path="test-data-path", metrics=[], device="cpu")

    criterion = test_client.get_criterion(config={})

    assert criterion == test_criterion
