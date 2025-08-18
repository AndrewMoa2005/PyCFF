# -*- coding: utf-8 -*-
# Algorithm implementation of curve fitting function

from typing import Callable
import numpy as np
import scipy.optimize as sopt
import inspect
import random
import warnings


class LinearFit:
    def __init__(
        self,
        x_data: list[float],
        y_data: list[float],
        degree: int = 2,  # Degree of the polynomial to fit
        y_intercept: float = None,  # y value when x = x0 (optional)
    ):
        """
        Using numpy to fit polynomial functions.
        Args:
            x_data (list[float]): x data
            y_data (list[float]): y data
            degree (int, optional): degree of the polynomial to fit. Defaults to 2.
            y_intercept (float, optional): y value when x = x0 (optional). Defaults to None.
        Raises:
            ValueError: x_data and y_data must have the same length.
            ValueError: Degree must be at least 1.
            ValueError: x_data must be sorted in ascending or descending order.
            ValueError: x_data cannot contain zero if y_intercept is provided.
        """
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have the same length.")
        if degree < 1:
            raise ValueError("Degree must be at least 1.")
        self.y_intercept = None
        x_is_ascending = x_data == sorted(x_data)
        x_is_descending = x_data == sorted(x_data, reverse=True)
        if not (x_is_ascending or x_is_descending):
            raise ValueError("x_data must be sorted in ascending or descending order.")
        self.x_data = np.array(x_data)
        self.y_data = np.array(y_data)
        if y_intercept is not None:
            if 0 in x_data:
                raise ValueError(
                    "x_data cannot contain zero if y_intercept is provided."
                )
            self.y_intercept = y_intercept
        self.degree: int = degree
        self.params: list[float] = None

    def x_data_order(self) -> bool:
        """
        return True if x_data is sorted in ascending order, False otherwise.
        Returns:
            bool: True if x_data is sorted in ascending order, False otherwise.
        """
        return self.x_data.tolist() == sorted(self.x_data.tolist())

    def insert_y_intercept(
        self, y_intercept: float = None
    ) -> tuple[list[float], list[float]]:
        """
        Add y_intercept to the data if it is not None.
        Args:
            y_intercept (float, optional): y value when x = x0 (optional). Defaults to None.
        Returns:
            tuple[list[float], list[float]]: x data and y data with y_intercept added.
        """
        if y_intercept is not None:
            self.y_intercept = y_intercept
            y0 = y_intercept
        else:
            if self.y_intercept is None:
                return None, None
            y0 = self.y_intercept
        ascending = self.x_data_order()
        y_list: list = self.y_data.tolist()
        x_list: list = self.x_data.tolist()

        def insert_num_in_list():
            for i, x in enumerate(x_list):
                if (ascending and x > 0) or (not ascending and x < 0):
                    x_list.insert(i, 0)
                    y_list.insert(i, y0)
                    break

        if x_list[0] > 0 and x_list[-1] > 0:
            x_list.insert(0, 0)
            y_list.insert(0, y0)
        elif x_list[0] < 0 and x_list[-1] < 0:
            x_list.append(0)
            y_list.append(y0)
        else:
            insert_num_in_list()
        return np.array(x_list), np.array(y_list)

    def fit(self, degree: int = None) -> list[float]:
        """
        Fit the model to the data.
        Args:
            degree (int, optional): degree of the polynomial to fit. Defaults to None.
        Returns:
            list[float]: coefficients of the polynomial fit [a[n], a[n-1], ..., a[0]].
        Raises:
            ValueError: Degree must be at least 1.
            ValueError: x_data must be sorted in ascending or descending order.
        """
        if degree is not None:
            if degree < 1:
                raise ValueError("Degree must be at least 1.")
            self.degree = degree
        if self.y_intercept is not None:
            xy = self.insert_y_intercept()
            if xy is None:
                raise ValueError("insert y_intercept failed.")
            x, y = xy
            print("Fitting x list:", x)
            print("Fitting y list:", y)
        else:
            x, y = self.x_data, self.y_data
        self.params = np.polyfit(
            x,
            y,
            self.degree,
        ).tolist()
        if self.y_intercept is not None:
            # Adjust the constant term to match the y_intercept at x=0
            self.params[-1] = self.y_intercept
        return self.params

    def yval(self, x: float) -> float:
        """
        Return the result of the function calculation.
        Args:
            x (float): x value
        Returns:
            float: y value
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        return float(np.polyval(self.params, x))

    def ylist(self, x: list[float] = None) -> list[float]:
        """
        Return the new y_data list of the function calculation.
        Args:
            x (list[float], optional): x data. Defaults to None.
        Returns:
            list[float]: y data.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if x is None:
            x = self.x_data.tolist()
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        p = np.poly1d(self.params)
        return p(np.array(x)).tolist()

    def r_squared(self, y_pred: list[float] = None) -> float:
        """
        calculate the R-squared value of the model.
        Args:
            y_pred (list[float], optional): predicted y data. Defaults to None.
        Returns:
            float: R-squared value.
        Raises:
            ValueError: Model has not been fitted yet.
            ValueError: predicted values length must match actual values length.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        y_true = np.array(self.y_data)
        y_p = np.array(y_pred) if y_pred is not None else np.array(self.ylist())
        if len(y_p) != len(y_true):
            raise ValueError(
                "predicted values length [%s] must match actual values length [%s]."
                % (len(y_p), len(y_true))
            )
        # calculate r_squared
        y_mean = np.mean(y_true)
        SS_tot = np.sum((y_true - y_mean) ** 2)
        SS_res = np.sum((y_true - y_p) ** 2)
        r_squared = (
            1 - (SS_res / SS_tot) if SS_tot != 0 else 1.0
        )  # avoid division by zero

        return r_squared

    def predict(self, y: list[float]) -> tuple[list[float], list[int]]:
        """
        predict the new x_data list base on input y_data.
        Args:
            y (list[float]): y data.
        Returns:
            tuple[list[float], list[int]]: x data and number of iterations.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        warnings.warn(
            "function predict is deprecated, use function solve instead",
            DeprecationWarning,
        )
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        p = np.poly1d(self.params)
        dp = np.polyder(p, 1)  # First derivative of the polynomial
        # Use Newton's method to find the roots for each y value
        x: list[float] = []
        n: list[int] = []
        max_iterations = 10 ** (
            len(self.params) + 2
        )  # Maximum iterations for convergence
        tolerance = 1e-12  # Convergence tolerance
        for y_val in y:
            # Approach the value of y using Newton's iteration method.
            x0 = 0.0 if abs(dp(0)) < tolerance else y_val / dp(0)
            n_iter = 0
            converged = False
            while n_iter < max_iterations:
                y0 = p(x0)
                if abs(y0 - y_val) < tolerance:
                    converged = True
                    break
                h0 = dp(x0)
                if abs(h0) < tolerance:
                    x0 += 0.1 if (y0 - y_val) < 0 else -0.1
                else:
                    x0 = x0 - (y0 - y_val) / h0
                n_iter += 1
            x.append(float(x0) if converged else float("nan"))
            n.append(n_iter)
        return x, n

    def solveval(self, y: float, limit: bool = True) -> float | dict:
        """
        solve the new x value base on input y value.
        Args:
            y (float): y value.
            limit (bool, optional): limit the x value. Defaults to True.
        Returns:
            float | dict: x value.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        if y < min(self.y_data) or y > max(self.y_data):
            warnings.warn(f"y value {y} is out of range.", UserWarning)
        coef = self.params.copy()
        coef[-1] = coef[-1] - y
        p = np.poly1d(coef)
        xval = np.roots(p)
        if len(xval) > 1:
            warnings.warn(
                f"Multiple solutions found {xval} for y value {y}", UserWarning
            )
            if limit is False:
                val: list[float] = []
                for i in xval:
                    val.append(float(i))
                return {"x": val, "y": y}
            else:
                for i in xval:
                    if i > min(self.x_data) and i < max(self.x_data):
                        return float(i)
        else:
            return float(xval)

    def solve(self, ylist: list[float], limit: bool = True) -> list[float | dict]:
        """
        solve the new x value base on input y value.
        Args:
            ylist (list[float]): y data.
            limit (bool, optional): limit the x value. Defaults to True.
        Returns:
            list[float | dict]: x data.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        xlist: list[float | dict] = []
        for y in ylist:
            xlist.append(self.solveval(y, limit))
        return xlist

    def formula(self, x: str = "x", decimal: int = 3, scientific: bool = False) -> str:
        """
        return the formula of the model.
        Args:
            x (str, optional): variable name. Defaults to "x".
            decimal (int, optional): decimal places. Defaults to 3.
            scientific (bool, optional): scientific notation. Defaults to False.
        Returns:
            str: formula of the model.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        formula: str = ""
        for i, param in enumerate(self.params):
            l = len(self.params) - 1 - i
            if l == 0:
                if param == 0:
                    formula = formula[:-3]
                    continue
                if scientific:
                    formula += f"{param:.{decimal}e}"
                else:
                    formula += f"{param:.{decimal}f}"
            else:
                if scientific:
                    formula += f"{param:.{decimal}e} * {x}**{l} + "
                else:
                    formula += f"{param:.{decimal}f} * {x}**{l} + "
        formula = formula.replace("+ -", "- ")
        formula = formula.replace("+-", "- ")
        formula = formula.replace("x**1", "x")
        return formula


class NonLinearFit:
    def __init__(
        self,
        x_data: list[float],
        y_data: list[float],
        func: Callable[[float, list[float]], float],
        p0: list[float] = None,
    ):
        """
        Using scipy.optimize to fit non-linear functions.
        Args:
            x_data (list[float]): x data.
            y_data (list[float]): y data.
            func (Callable[[float, list[float]], float]): function to fit.
            p0 (list[float], optional): initial guess for the parameters. Defaults to None.
        Raises:
            ValueError: x_data and y_data must have the same length.
            ValueError: x_data must be sorted in ascending or descending order.
            ValueError: Function must have at least two arguments (x, *params)
            ValueError: p0 length must match function parameters count
        Notes:
        ------
            func : func(x, *p) -> float
            p : list of parameters, len(p) = len(p0)
            define 1: def func(x, p0, p1, p2): return p0 * x**2 + p1 * x + p2
            define 2: def func(x, p0, p1): return eval('p0 * np.sin(x * p1)')
            define 3: lambda x, a, b, c: a * np.exp(b * x) + c
            define 4: lambda x, a, b, c: eval("a * np.log(b * x) + c")
            define 5: eval("lambda x, a, b, c: a * np.exp(b * x) + c")
            Warning: Do not allow users to execute the eval() function.
        """
        if func.__code__.co_argcount < 2:
            raise ValueError("Function must have at least two arguments (x, *params)")
        if p0 is not None and len(p0) != func.__code__.co_argcount - 1:
            raise ValueError("p0 length must match function parameters count")
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have the same length.")
        x_is_ascending = x_data == sorted(x_data)
        x_is_descending = x_data == sorted(x_data, reverse=True)
        if not (x_is_ascending or x_is_descending):
            raise ValueError("x_data must be sorted in ascending or descending order.")
        self.x_data = x_data
        self.y_data = y_data
        self.func = func
        if p0 is None:
            self.refresh_p0()
        else:
            self.p0 = p0
        self.params: list[float] = None

    def x_data_order(self) -> bool:
        """
        return True if x_data is sorted in ascending order, False otherwise.
        Returns:
            bool: True if x_data is sorted in ascending order, False otherwise.
        """
        return self.x_data == sorted(self.x_data)

    def refresh_p0(self, p: list[float] = None):
        """
        refresh or reset p0.
        Args:
            p (list[float], optional): initial guess for the parameters. Defaults to None.
        Raises:
            ValueError: Function must have at least two arguments (x, *params)
            ValueError: p0 length must match function parameters count
        """
        param_count = self.func.__code__.co_argcount - 1
        if param_count < 1:
            raise ValueError("Function must have at least two arguments (x, *params)")
        if p is not None:
            if len(p) != param_count:
                raise ValueError("p0 length must match function parameters count")
            self.p0 = p
        else:
            x = np.array(self.x_data)
            y = np.array(self.y_data)
            min_range = np.min(y / x)
            max_range = np.max(y / x)
            self.p0 = [
                float(random.uniform(min_range, max_range)) for _ in range(param_count)
            ]

    def fit(self, p0: list[float] = None) -> list[float]:
        """
        fit the model.
        Args:
            p0 (list[float], optional): initial guess for the parameters. Defaults to None.
        Returns:
            list[float]: fitted parameters.
        Raises:
            ValueError: Model fit failed.
            ValueError: Parameter fit failed.
        """
        if p0 is None:
            if self.p0 is None:
                self.refresh_p0()
        else:
            self.p0 = p0
        max_fev = 10 ** (self.func.__code__.co_argcount + 1)
        try:
            params, _ = sopt.curve_fit(
                self.func,
                self.x_data,
                self.y_data,
                p0=self.p0,
                maxfev=max_fev,
                epsfcn=10 - 12,
            )
        except RuntimeError as e:
            raise ValueError(f"Model fit failed: {str(e)}") from e
        if len(params) != len(self.p0):
            raise ValueError("Parameter fit failed.")
        self.params = params.tolist() if isinstance(params, np.ndarray) else [params]
        return self.params

    def yval(self, x: float) -> float:
        """
        Return the result of the function calculation.
        Args:
            x (float): x value
        Returns:
            float: y value
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        return self.func(x, *self.params)

    def ylist(self, x: list[float] = None) -> list[float]:
        """
        Return the result of the function calculation for each x value.
        Args:
            x_data (list[float], optional): x data. Defaults to None.
        Returns:
            list[float]: y values.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        if x is None:
            x = self.x_data
        return self.func(np.array(x), *self.params).tolist()

    def r_squared(self, y_pred: list[float] = None) -> float:
        """
        Return the coefficient of determination (R-squared) of the model.
        Args:
            y_pred (list[float]): predicted y values.
        Returns:
            float: R-squared value.
        Raises:
            ValueError: Model has not been fitted yet.
            ValueError: predicted values length must match actual values length.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        y_true = np.array(self.y_data)
        y_p = np.array(y_pred) if y_pred is not None else np.array(self.ylist())
        if len(y_p) != len(y_true):
            raise ValueError(
                "predicted values length [%s] must match actual values length [%s]."
                % (len(y_p), len(y_true))
            )

        # calculate r_squared
        y_mean = np.mean(y_true)
        SS_tot = np.sum((y_true - y_mean) ** 2)
        SS_res = np.sum((y_true - y_p) ** 2)
        r_squared = (
            1 - (SS_res / SS_tot) if SS_tot != 0 else 1.0
        )  # avoid division by zero

        return r_squared

    def solve(self, y: list[float], limit: bool = True) -> list[float | dict]:
        """
        solve the new x value base on input y value.
        Args:
            y (list[float]): y values.
            limit (bool, optional): limit the x value. Defaults to True.
        Returns:
            list[float | dict]: x values.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        xlist: list[float | dict] = []
        for y in y:
            xlist.append(self.solveval(y, limit))
        return xlist

    def solveval(self, y: float, limit: bool = True) -> float | dict:
        """
        solve the new x value base on input y value.
        Args:
            y (float): y value.
            limit (bool, optional): limit the x value. Defaults to True.
        Returns:
            float | dict: x value.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        if y < min(self.y_data) or y > max(self.y_data):
            warnings.warn(f"y value {y} is out of range.", UserWarning)

        def func_solve(X):
            return self.func(X, *self.params) - y

        max_iter = 10 ** (self.func.__code__.co_argcount + 1)
        x0 = 0
        try:
            x = [sopt.newton(func_solve, x0, tol=1e-12, maxiter=max_iter)]
        except RuntimeError as e:
            raise ValueError(f"Solution failed: {str(e)}") from e
        if len(x) == 1:
            return float(x[0])
        else:
            warnings.warn(f"Multiple solutions found {x} for y value {y}", UserWarning)
            if limit:
                for i in x:
                    if i > min(self.x_data) and i < max(self.x_data):
                        return float(i)
            else:
                val: list[float] = []
                for i in x:
                    val.append(float(i))
                return {"x": val, "y": y}

    def source(
        self,
    ) -> str:
        """
        print the function formula
        Returns:
            str: source code of the function.
        Raises:
            ValueError: Model has not been fitted yet.
        """
        warnings.warn(
            "Unable to capture the source code of lambda expression wrapped in eval().",
            DeprecationWarning,
        )
        if self.params is None:
            raise ValueError("Model has not been fitted yet.")
        try:
            source_code = inspect.getsource(self.func)
        except Exception as e:
            print("An error occurred while capturing the source code : %s" % str(e))
            return None
        return source_code

    def args(self) -> list[str]:
        """
        return the arguments of the function.
        Returns:
            list[str]: arguments of the function.
        """
        return list(self.func.__code__.co_varnames)


if __name__ == "__main__":
    """
    test cff
    """
    import matplotlib.pyplot as plt

    x_data = [2, 4, 6, 8, 10]
    print("Original x_data : ", x_data)
    y_data = [0.1, 0.6, 1.5, 2.5, 3.5]
    print("Original y_data : ", y_data)

    def test_linear_fit():
        poly_fit = LinearFit(x_data, y_data, degree=2)
        params = poly_fit.fit()
        print("Fitted parameters : ", params)
        formula = poly_fit.formula(decimal=8, scientific=True)
        print("Formula : [y = %s]." % formula)
        y_pred = poly_fit.ylist()
        print("Predicted y values : ", y_pred)
        r_squared = poly_fit.r_squared()
        print("R-squared : ", r_squared)
        y_old = [0.2, 1.3, 2.4, 3.6]
        x_new = poly_fit.solve(y_old, limit=False)
        print(
            "Predicted x %s values for given y data %s ."
            % (
                x_new,
                y_old,
            )
        )
        print("Solve x %s value for y = 0.35." % poly_fit.solveval(0.35))
        x_val = 3
        y_val = poly_fit.yval(x_val)
        print("Y = %s at given X = %s " % (y_val, x_val))
        plt.scatter(x_data, y_data, label="Original Data")
        plt.plot(x_data, y_pred, label="Fitted Curve")
        plt.legend()
        plt.show()

    def test_non_linear_fit():
        nonl_fit = NonLinearFit(
            x_data,
            y_data,
            eval("lambda x, a, b, c : a * x**2 + b * x + c"),
        )
        params = nonl_fit.fit()
        print("initial p0 : ", nonl_fit.p0)
        print("Fitted parameters : ", params)
        print("Source Code : %s" % nonl_fit.source())
        print("Arguments : %s" % nonl_fit.args())
        y_pred = nonl_fit.ylist()
        print("Predicted y values : ", y_pred)
        r_squared = nonl_fit.r_squared()
        print("R-squared : ", r_squared)
        y_old = [0.2, 1.3, 2.4, 3.6]
        x_new = nonl_fit.solve(y_old, limit=False)
        print("Predicted x %s values for given y data %s . " % (x_new, y_old))
        print("Solve x %s value for y = 0.35." % nonl_fit.solveval(0.35))
        x_val = 3
        y_val = nonl_fit.yval(x_val)
        print("Y = %s at given X = %s " % (y_val, x_val))
        plt.scatter(x_data, y_data, label="Original Data")
        plt.plot(x_data, y_pred, label="Fitted Curve")
        plt.legend()
        plt.show()

    print("----- Linear Fit Test -----")
    test_linear_fit()
    print("----- End of Linear Fit Test -----")

    print("----- Non-Linear Fit Test -----")
    test_non_linear_fit()
    print("----- End of Non-Linear Fit Test -----")
