import ray
import random
import time

# Initialize Ray
ray.init()

@ray.remote
def monte_carlo_pi_part(num_samples):
    """Estimate Pi using Monte Carlo simulation for a partition of samples."""
    count = 0
    for _ in range(num_samples):
        x, y = random.random(), random.random()
        if x**2 + y**2 <= 1.0:
            count += 1
    return count

@ray.remote
def aggregate_results(partial_results):
    """Aggregate partial results from workers to compute the total count."""
    return sum(partial_results)

# Main computation
def estimate_pi(total_samples, num_workers):
    """Distribute the computation of Pi approximation using Ray."""
    samples_per_worker = total_samples // num_workers

    # Start remote tasks for Monte Carlo simulation
    start_time = time.time()
    futures = [
        monte_carlo_pi_part.remote(samples_per_worker) for _ in range(num_workers)
    ]

    # Aggregate results using another distributed task
    partial_results = ray.get(futures)
    total_inside_circle = ray.get(aggregate_results.remote(partial_results))
    end_time = time.time()

    # Calculate Pi
    pi_estimate = (4 * total_inside_circle) / total_samples

    # Print computation time
    print(f"Time taken for computation: {end_time - start_time:.2f} seconds")
    return pi_estimate

if __name__ == "__main__":
    # Total samples and number of workers
    TOTAL_SAMPLES = 100_000_000  # Increase the total samples significantly
    NUM_WORKERS = 100  # Use more workers to distribute the load

    start_time = time.time()
    pi = estimate_pi(TOTAL_SAMPLES, NUM_WORKERS)
    end_time = time.time()

    print(f"Estimated Pi: {pi}")
    print(f"Total time taken: {end_time - start_time:.2f} seconds")

# Shutdown Ray
ray.shutdown()
