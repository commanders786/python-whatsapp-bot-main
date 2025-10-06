import logging
import os
import sys
from app import create_app
from waitress import serve

# Set environment variables to limit threading
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['MKL_NUM_THREADS'] = '4'
os.environ['OPENBLAS_NUM_THREADS'] = '4'
os.environ['NUMEXPR_NUM_THREADS'] = '4'

# Set resource limits to prevent thread exhaustion (Unix/Linux only)
if sys.platform != 'win32':
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_NPROC, (200, 200))  # Limit processes
        resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))  # Limit file descriptors
    except (ValueError, OSError) as e:
        logging.warning(f"Could not set resource limits: {e}")
else:
    logging.info("Running on Windows - resource limits not applicable")

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Get thread count from environment or use safe default
    thread_count = int(os.getenv('WAITRESS_THREADS', 32))
    
    logging.info(f"Starting Flask app with Waitress on http://0.0.0.0:8000 with {thread_count} threads")
    logging.info(f"Thread limits: OMP={os.environ.get('OMP_NUM_THREADS')}, MKL={os.environ.get('MKL_NUM_THREADS')}")
    
    serve(app, host="0.0.0.0", port=8000, threads=thread_count)
