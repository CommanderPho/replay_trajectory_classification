import numpy as np
from scipy.stats import multivariate_normal

from .core import atleast_2d


def simulate_poisson_spikes(rate, sampling_frequency):
    '''Given a rate, returns a time series of spikes.

    Parameters
    ----------
    rate : ndarray, shape (n_time,)
    sampling_frequency : float

    Returns
    -------
    spikes : ndarray, shape (n_time,)

    '''
    return 1.0 * (np.random.poisson(rate / sampling_frequency) > 0)


def simulate_place_field_firing_rate(means, position, max_rate=15, sigma=10):
    '''Simulates the firing rate of a neuron with a place field at `means`.

    Parameters
    ----------
    means : ndarray, shape (n_position_dims,)
    position : ndarray, shape (n_time, n_position_dims)
    max_rate : float, optional
    sigma : float, optional

    Returns
    -------
    firing_rate : ndarray, shape (n_time,)

    '''
    position = atleast_2d(position)
    n_position_dims = position.shape[1]
    firing_rate = multivariate_normal(
        means, sigma * np.eye(n_position_dims)).pdf(position)
    firing_rate /= firing_rate.max()
    firing_rate *= max_rate
    return firing_rate


def simulate_neuron_with_place_field(means, position, max_rate=15, sigma=10,
                                     sampling_frequency=500):
    '''Simulates the spiking of a neuron with a place field at `means`.

    Parameters
    ----------
    means : ndarray, shape (n_position_dims,)
    position : ndarray, shape (n_time, n_position_dims)
    max_rate : float, optional
    sigma : float, optional
    sampling_frequency : float, optional

    Returns
    -------
    spikes : ndarray, shape (n_time,)

    '''
    firing_rate = simulate_place_field_firing_rate(
        means, position, max_rate, sigma)
    return simulate_poisson_spikes(firing_rate, sampling_frequency)


def simulate_multiunit_with_place_fields(place_means, position, mark_spacing=5,
                                         n_mark_dims=4):
    '''Simulates a multiunit with neurons at `place_means`

    Parameters
    ----------
    place_means : ndarray, shape (n_neurons, n_position_dims)
    position : ndarray, shape (n_time, n_position_dims)
    mark_spacing : int, optional
    n_mark_dims : int, optional

    Returns
    -------
    multiunit : ndarray, shape (n_time, n_mark_dims)

    '''
    n_neurons = place_means.shape[0]
    mark_centers = np.arange(0, n_neurons * mark_spacing, mark_spacing)
    n_time = position.shape[0]
    marks = np.full((n_time, n_mark_dims), np.nan)
    for mean, mark_center in zip(place_means, mark_centers):
        is_spike = simulate_neuron_with_place_field(
            mean, position, max_rate=15, sigma=10,
            sampling_frequency=500) > 0
        n_spikes = int(is_spike.sum())
        marks[is_spike] = multivariate_normal(
            mean=[mark_center] * n_mark_dims).rvs(size=n_spikes)
    return marks