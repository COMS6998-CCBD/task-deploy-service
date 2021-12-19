import logging_init # This needs to be first
from service.background_service.exited_service_manager import EM
from service.background_service.scheduling_manager import SM
import traceback
import time
import logging

LOG = logging.getLogger("TDS")

if __name__ == "__main__":
    while True:
        try:
            SM.schedule()
            EM.main()
        except Exception as e:
            traceback.print_exc()
            print("\n\n\n\n")
        LOG.info("sleeping.....")
        time.sleep(10)
        LOG.info("woke up.....")
