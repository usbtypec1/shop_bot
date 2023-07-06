import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from structlog.stdlib import BoundLogger

import cart.tasks
from cart.repositories import CartRepository
from database import session_factory

logger: BoundLogger = structlog.get_logger('app')


def main():
    cart_repository = CartRepository(session_factory)
    scheduler = BlockingScheduler()
    scheduler.add_job(
        func=cart.tasks.release_expired_cart_products,
        trigger=IntervalTrigger(minutes=1),
        args=(cart_repository, 1800)
    )

    logger.info('Jobs started')
    scheduler.start()


if __name__ == '__main__':
    main()
