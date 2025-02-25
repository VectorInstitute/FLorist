from unittest.mock import Mock, patch, ANY

from florist.api.models.mnist import MnistNet
from florist.api.clients.clients import Client, LocalDataClient, FedProxLocalDataClient
from florist.api.clients.optimizers import Optimizer
from florist.api.servers.strategies import Strategy


def test_class_for_client():
    assert Client.class_for_client(Client.FEDAVG) == LocalDataClient
    assert Client.class_for_client(Client.FEDPROX) == FedProxLocalDataClient


def test_list():
    assert Client.list() == [Client.FEDAVG.value, Client.FEDPROX.value]


def test_list_by_strategy():
    assert Client.list_by_strategy(Strategy.FEDAVG) == [Client.FEDAVG.value]
    assert Client.list_by_strategy(Strategy.FEDPROX) == [Client.FEDPROX.value]


@patch("florist.api.models.mnist.load_mnist_data")
def test_local_model_get_data_loaders(mock_load_mnist_data: Mock):
    test_data_path = "test-data-path"
    test_device = "cpu"
    test_config = {"batch_size": 200}
    test_train_loader = "test-train-loader"
    test_val_loader = "test-val-loader"
    test_client = LocalDataClient(data_path=test_data_path, metrics=[], device=test_device)
    test_client.set_model(MnistNet())

    mock_load_mnist_data.return_value = (test_train_loader, test_val_loader, {})

    train_loader, val_loader = test_client.get_data_loaders(config=test_config)

    assert train_loader == test_train_loader
    assert val_loader == test_val_loader
    mock_load_mnist_data.assert_called_with(test_data_path, test_config["batch_size"], None)


@patch("florist.api.clients.optimizers.torch")
def test_local_model_get_optimizer(mock_torch: Mock):
    test_optimizer = "test-optimizer"
    mock_torch.optim.SGD.return_value = test_optimizer
    test_client = LocalDataClient(data_path="test-data-path", metrics=[], device="cpu")
    test_client.set_optimizer_type(Optimizer.SGD)

    test_parameters = "test-parameters"
    test_model = MnistNet()
    test_model.parameters = Mock()
    test_model.parameters.return_value = test_parameters
    test_client.set_model(test_model)

    optimizer = test_client.get_optimizer(config={})

    assert optimizer == test_optimizer
    mock_torch.optim.SGD.assert_called_with(test_parameters, lr=0.001, momentum=0.9)


@patch("florist.api.models.mnist.torch")
def test_local_model_get_criterion(mock_torch: Mock):
    test_criterion = "test-criterion"
    mock_torch.nn.CrossEntropyLoss.return_value = test_criterion
    test_client = LocalDataClient(data_path="test-data-path", metrics=[], device="cpu")
    test_client.set_model(MnistNet())

    criterion = test_client.get_criterion(config={})

    assert criterion == test_criterion


@patch("florist.api.models.mnist.load_mnist_data")
@patch("florist.api.clients.clients.DirichletLabelBasedSampler")
def test_fedprox_local_model_get_data_loaders(mock_sampler: Mock, mock_load_mnist_data: Mock):
    test_data_path = "test-data-path"
    test_device = "cpu"
    test_config = {"batch_size": 200}
    test_train_loader = "test-train-loader"
    test_val_loader = "test-val-loader"
    test_client = FedProxLocalDataClient(data_path=test_data_path, metrics=[], device=test_device)
    test_client.set_model(MnistNet())

    mock_load_mnist_data.return_value = (test_train_loader, test_val_loader, {})

    train_loader, val_loader = test_client.get_data_loaders(config=test_config)

    assert train_loader == test_train_loader
    assert val_loader == test_val_loader
    mock_load_mnist_data.assert_called_with(test_data_path, test_config["batch_size"], ANY)
    mock_sampler.assert_called_with(list(range(10)), sample_percentage=0.75, beta=1)
