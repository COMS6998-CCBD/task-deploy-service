import logging_init # This needs to be first
from service.background_service.exited_service_manager import EM
import traceback
import time
import logging

LOG = logging.getLogger("TDS")

if __name__ == "__main__":
    while True:
        try:
            EM.main()
        except Exception as e:
            traceback.print_exc()
            print("\n\n\n\n")
        LOG.info("sleeping.....")
        time.sleep(60)
        LOG.info("woke up.....")
