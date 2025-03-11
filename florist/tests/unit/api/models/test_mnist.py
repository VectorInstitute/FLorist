from unittest.mock import Mock, patch

import torch
from fl4health.utils.sampler import DirichletLabelBasedSampler

from florist.api.models.mnist import MnistNet


@patch("florist.api.models.mnist.load_mnist_data")
def test_get_data_loaders(mock_load_mnist_data: Mock):
    test_train_loader = "test-train-loader"
    test_val_loader = "test-val-loader"
    mock_load_mnist_data.return_value = (test_train_loader, test_val_loader, None)
    test_data_path = "test-data-path"
    test_batch_size = 100
    test_sampler = DirichletLabelBasedSampler(list(range(10)), sample_percentage=0.75, beta=1)

    test_model = MnistNet()
    train_loader, val_loader = test_model.get_data_loaders(test_data_path, test_batch_size, test_sampler)

    assert train_loader == test_train_loader
    assert val_loader == val_loader
    mock_load_mnist_data.assert_called_once_with(test_data_path, test_batch_size, test_sampler)


def test_get_criterion():
    test_model = MnistNet()
    criterion = test_model.get_criterion()

    assert isinstance(criterion, torch.nn.CrossEntropyLoss)
