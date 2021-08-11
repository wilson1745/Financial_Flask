import traceback

import pydotplus
from sklearn import datasets, tree
from sklearn.model_selection import train_test_split

from calculations.common.exceptions.core_exception import CoreException

if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    try:
        iris = datasets.load_iris()
        # print(f"iris: {iris}")

        X = iris.data
        y = iris.target
        # print(f"X: {X}")
        # print(f"y: {y}")

        clf = tree.DecisionTreeClassifier(criterion="entropy").fit(X, y)
        print(f"clf.score(X, y): {clf.score(X, y)}")

        """ 決策樹模型輸出 """
        dot_data = tree.export_graphviz(clf, out_file=None)
        graph = pydotplus.graph_from_dot_data(dot_data)
        graph.write_pdf("./files/tree_iris.pdf")

        """ 拆分訓練集與測試集 """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
        clf = tree.DecisionTreeClassifier(criterion="entropy").fit(X_train, y_train)
        print(f"clf.score(X_train,y_train): {clf.score(X_train, y_train)}")
        print(f"clf.predict(X_test): {clf.predict(X_test)}")
        print(f"clf.score(X_test,y_test): {clf.score(X_test, y_test)}")

        """ 過度配適初步調整 """
        clf = tree.DecisionTreeClassifier(criterion="entropy", max_depth=3).fit(X_train, y_train)
        print(f"clf.predict(X_test): {clf.predict(X_test)}")
        print(f"clf.score(X_train,y_train): {clf.score(X_train, y_train)}")
        print(f"clf.score(X_test,y_test): {clf.score(X_test, y_test)}")

        clf = tree.DecisionTreeClassifier(criterion="gini", max_depth=3).fit(X_train, y_train)
        print(f"clf.predict(X_test): {clf.predict(X_test)}")
        print(f"clf.score(X_test,y_test): {clf.score(X_test, y_test)}")

        dot_data = tree.export_graphviz(clf, out_file=None)
        graph = pydotplus.graph_from_dot_data(dot_data)
        graph.write_pdf("./files/iris_gini_max3.pdf")

    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
