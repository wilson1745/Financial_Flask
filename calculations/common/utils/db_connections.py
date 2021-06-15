# 類別
class DbConnections:

    # 建構式
    def __init__(self, tool):
        if tool == 'mysql':
            self.server = "localhost"
            self.database = "financial_db"
            self.username = "root"
            self.password = "1qaz2wsx"
            self.driver = "{MySQL ODBC 8.0 Unicode Driver}"
            # self.driver = "{MySQL ODBC 8.0 ANSI Driver}"
            self.port = 3306
        elif tool == 'mysql_ansi':
            self.server = "localhost"
            self.database = "financial_db"
            self.username = "root"
            self.password = "1qaz2wsx"
            self.driver = "{MySQL ODBC 8.0 ANSI Driver}"
            self.port = 3306
        elif tool == 'mssql':
            self.server = "LAPTOP-WILSON-C"
            self.database = "Financial"
            self.username = "sa"
            self.password = "tXK3A$.K"
            self.driver = "{ODBC Driver 17 for SQL Server}"
            self.port = 1433
        else:
            raise TypeError("Unknown DB category")
