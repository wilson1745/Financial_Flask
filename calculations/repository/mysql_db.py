from mysql.connector import pooling

from calculations import log


class ConnectionPool(object):

    def __init__(self):
        """ Database Resident Connection Pooling (DRCP) """
        # Create the session pool
        self.pool = pooling.MySQLConnectionPool(pool_name="pynative_pool",
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host="localhost",
                                                database="financial_db",
                                                user="root",
                                                password="1qaz2wsx")
        log.debug(f"self.pool: {self.pool}")

# if __name__ == "__main__":
#     try:
#         pool = ConnectionPool()
#         log.debug(pool)
#     except Exception as e:
#         CoreException.show(e, traceback.format_exc())
