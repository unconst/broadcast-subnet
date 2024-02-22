import torch.multiprocessing as mp
import time
from mapreduce import Peer
import mapreduce.utils as utils
import bittensor as bt
from argparse import ArgumentParser
import os

# Maximum size for benchmarking, set to 50 MB
benchmark_max_size = 50 * 1024 * 1024 

# Setting up the argument parser
parser = ArgumentParser()

parser.add_argument( '--auto_update', default = 'on', help = "Auto update" ) # major, minor, patch, no
parser.add_argument ('--port.range', default = '9000:9010', help = "Opened Port range" )
parser.add_argument('--validator.uid', type = int, default= 0, help='Validator UID')
parser.add_argument('--netuid', type = int, default= 10, help='Subnet UID')

bt.subtensor.add_args(parser)
bt.logging.add_args(parser)
bt.wallet.add_args(parser)
bt.axon.add_args(parser)
config = bt.config(parser)
            
"""
Performs benchmarking operations for the given validator.

Args:
    wallet (bt.Wallet): Bittensor wallet instance.
    validator_uid (int): Validator's unique identifier.
    netuid (int): Network unique identifier.
    network (str): Network information.
"""
def benchmark():
    bt.logging.info("")
    bt.logging.info(f"Starting benchmarking bot")
    
    # Initialize Peer instance
    peer = Peer(1, 1, config = config, benchmark_max_size = benchmark_max_size)

    # Initialize process group with the fetched configuration
    if not peer.benchmark():
        # Not able to benchmark, wait a bit
        time.sleep(2)
        return
    peer.destroy_process_group()
    bt.logging.success("Benchmarking completed")

"""
The main function to continuously run the benchmarking process.
"""
def main():
    
    while True: 
        # Check if there is a new version available
        if config.auto_update != "off":
            if utils.update_repository():
                bt.logging.success("🔁 Repository updated, exiting benchmark")
                exit(0)
                
        # Start the benchmarking process
        p = mp.Process(target=benchmark)
        p.start()
        # Wait for the process to complete, with a specified timeout
        p.join(timeout=60)  # Set your desired timeout in seconds
        
        # Check if the process is still alive after the timeout
        if p.is_alive():
            # If the process is still running after the timeout, terminate it
            bt.logging.warning("Benchmark process exceeded timeout, terminating...")
            p.terminate()
            # Wait a bit for the process to terminate
            p.join()
        
        # Sleep for a short duration before starting the next process
        time.sleep(1)

if __name__ == '__main__':
    # Check if there is enough free memory to run the benchmark
    bt.logging.info(f"Available memory: {utils.human_readable_size(utils.get_available_memory())}")
    if utils.get_available_memory() < benchmark_max_size * 2:
        bt.logging.error("🔴 Not enough memory to run benchmark")
        exit(1)
    main()