from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt
import numpy
import pandas
from matplotlib.axes import Axes
from scipy.interpolate import CloughTocher2DInterpolator as CT2DI


def bisection_search(
    function: Callable[[float], float],
    seek_value: float,
    bounds: Optional[Tuple[float, float]] = None,
    atol: Optional[float] = None,
    max_iters: Optional[int] = None,
) -> Tuple[float, bool]:
    """bounded goalseek of a function using bisection search.

    Parameters
    ----------
    function : callable
        This function must be differentiable and must be defined at the `seek_value`. The
        function must also be montonic with respect to the seek_value within the `bounds`.
        For example, a parabola y=x*x cannot be solved for y=1 if the bounds are set to (2,2)
        since two solutions exist. additionally, this algorithm supports only positive solutions,
        so bounds must be set such that they enclose the positive solution.
        Goal seeking will begin at the midpoint of the user provided bounds, or at 0.5.
        This routine terminates ideally when `seek_value == function(guess)`, or when
        the function returns an estimate within `atol` percent difference of the `seek_value`.
    seek_value : float
        The value to seek by guessing inputs to the function.
    bounds : 2-tuple (float, float), optional (default=(0, 1))
        The returned value will be between these bounds `(lower, upper)`, should be positive.
    atol : float, optional (default=1e-3)
        The absolute difference (as decimal) allowed between the `seek_value` and the returned
        guess. When the guess is within this tolerance the search will terminate and return
        the current guess.
    max_iters : int, optional (default=25)
        The max number of tries before exiting with current guess value.

    Returns
    -------
    guess, converged : float, bool
        function returns a 2-tuple with the current guess, and whether it converged within
        `atol`.

    """

    if atol is None:  # pragma: no cover
        atol = 1e-3
    if max_iters is None:  # pragma: no cover
        max_iters = 25
    if bounds is None:
        bounds = (0, 1)

    old_result, result = bounds
    guess = (result + old_result) / 2
    converged = False

    for _ in range(max_iters):

        check = function(guess)

        if numpy.isnan(check):  # pragma: no cover

            check = 1e6

        diff = check - seek_value
        # print(f"{old_result:.3f}, {guess:.3f}, {check:.3f}, {diff:.3f}")

        if abs(diff) < atol:
            converged = True
            return guess, converged

        if diff > 0:
            result = guess
        else:
            old_result = guess

        guess = (result + old_result) / 2

    return guess, converged


class NomographBase(object):
    def __init__(
        self,
        *,
        x: Sequence[float],
        t: Sequence[float],
        y: Sequence[float],
        interp_kwargs: Dict[str, Any] = None,
    ) -> None:
        """This class manages 2D interpolations of BMP performance
        across the size, drawdown time, and long term capture.

        Inputs for `size`, `ddt`, and `performance` should all have the same shape.

        when grouped by 'trace' each set of x and y pairs should start and stop at the
        same value, but each set does not have to be the same length. for example, each
        trace group should have a value @ x=0, and all traces should have the same value
        for their maximum x value. This allows the 2d interpolation to be properly rectangular
        instead of having portions of the searchspace undefined (numpy.nan).

        x : 1D, listlike
            indicates BMP size, typically either design intensity or volume

        t : 1D, listlike
            indicates the 'trace' of the nomograph, typically drawdown time or
            time of concentration.

        y : 1D, listlike
            indicates the performance

        interp_kwargs : dict, optional (default=None)
            passed to the clough tocher interpolator


                Example Volume Based Nomograph
                ------------------------------

        y = fraction long term capture as decimal
            ^
        1.0 |            _ _-----  t = 12 hr ddt
            |         _--
            |       /
            |     /
            |   /
            |  /
            | /
            |/
        0.0 ---------------------------------
            x = facility volume / design volume



                Example Flow Based Nomograph
                ----------------------------

        y = fraction long term capture as decimal
            ^
        1.0 |            _ _-----  t = 15 min time of concentration
            |         _--
            |       /
            |     /
            |   /
            |  /
            | /
            |/
        0.0 ---------------------------------
            x = Design Intensity in/hr

        """
        self.x_data = x
        self.t_data = t
        self.y_data = y
        self._interp_kwargs = interp_kwargs

        self._nomo = None

    @property
    def interp_kwargs(self) -> Dict[str, Any]:  # pragma: no cover
        if self._interp_kwargs is None:
            self._interp_kwargs = {"rescale": True}
        return self._interp_kwargs

    @property
    def nomo(self) -> CT2DI:
        if self._nomo is None:
            self._nomo = CT2DI(
                points=numpy.column_stack((self.x_data, self.t_data)),
                values=self.y_data,
                **self.interp_kwargs,
            )
        return self._nomo

    def get_x(
        self,
        at_y: float,
        t: float,
        atol: Optional[float] = None,
        max_iters: Optional[int] = None,
    ) -> Tuple[float, bool]:
        """Goal seek at 'y' to find x at a given value of t

        This method answers the question 'how big do i make a facility to achieve
        y% capture if i keep the 'trace' `t` constant?'

        """

        if at_y <= 1e-3:  # pragma: no cover
            return 0.0, False

        at_y = numpy.clip(at_y, numpy.nanmin(self.y_data), numpy.nanmax(self.y_data))
        t = numpy.clip(t, numpy.nanmin(self.t_data), numpy.nanmax(self.t_data))

        _nomo: Callable[[float, float], float] = self.nomo

        function: Callable[[float], float] = lambda x: _nomo(x, t)
        vmin, vmax = numpy.nanmin(self.x_data), numpy.nanmax(self.x_data)

        result, converged = bisection_search(
            function=function,
            seek_value=at_y,
            bounds=(vmin, vmax),
            atol=atol,
            max_iters=max_iters,
        )

        return result, converged

    def __call__(
        self,
        *,
        x: Optional[Any] = None,
        t: Optional[Any] = None,
        y: Optional[Any] = None,
        atol: Optional[float] = None,
        max_iters: Optional[int] = None,
    ) -> Any:
        """This calls the underlying 2d interpolator with any two of the inputs x, t, or y.

        this call is not well-typed because numpy's typing is extremely tolerant, e.g, array
        broadcasting floats * numpy.array. This means that if we declare types as unions, like
        Union[float, Sequence[float]] then we will end up unable to parse types after using the
        function since the return will be a union, even though we know we called it with a float.

        At the time of development (March 2020) mypy does not follow type check logic other than
        the built-in `isinstance` method, which doesn't work well for numpy types. For now,
        these interpolators are tolerantly typed.
        """

        if t is None:
            raise ValueError("`t` is required")

        t = numpy.clip(t, numpy.nanmin(self.t_data), numpy.nanmax(self.t_data))

        # solve for y via regular nomograph given size and which trace
        if y is None and x is not None:
            x = numpy.clip(x, numpy.nanmin(self.x_data), numpy.nanmax(self.x_data))
            result: Union[float, Sequence[float]] = self.nomo(x, t)
            return result

        # goal seek x via search
        elif x is None and y is not None:
            y = numpy.clip(y, numpy.nanmin(self.y_data), numpy.nanmax(self.y_data))

            if numpy.iterable(t) and numpy.iterable(y):
                if len(t) == len(y):

                    res: List[float] = []
                    for _y, _t in zip(y, t):

                        guess, _ = self.get_x(
                            at_y=_y, t=_t, atol=atol, max_iters=max_iters
                        )
                        res.append(guess)
                    arr_result: Sequence[float] = numpy.array(res)

                    return arr_result
                else:
                    raise ValueError("y and t must be the same length")

            guess, converged = self.get_x(at_y=y, t=t, atol=atol, max_iters=max_iters)

            if not converged:
                pass
                # TODO: do something fancy with the warning?
            return guess
        else:
            raise ValueError("must call with `t` and either `x` or `y`")

    def _baseplot(
        self, ax: Optional[Axes] = None, **kwargs: Dict[str, Any]
    ) -> Axes:  # pragma: no cover

        if ax is None:
            ax = plt.gca()

        xmin, xmax = numpy.nanmin(self.x_data), numpy.nanmax(self.x_data)
        xline = numpy.linspace(xmin, xmax, 100)

        fits = self(x=self.x_data, t=self.t_data)

        ax.scatter(
            self.x_data,
            fits,
            marker="o",
            s=50,
            facecolor="none",
            edgecolor="k",
            alpha=0.4,
        )

        for i, d in enumerate(sorted(set(self.t_data))):

            x = self.x_data[self.t_data == d]
            y = self.y_data[self.t_data == d]

            xline = numpy.linspace(numpy.nanmin(x), numpy.nanmax(x), 100)
            vals = self.nomo(xline, [d for _ in xline])

            ax.plot(xline, vals, "-k", alpha=0.2)

            ax.scatter(x, y, s=15, label=str(d), zorder=10, alpha=0.5)

        return ax

    def plot(self, *args: Tuple, **kwargs: Dict[str, Any]) -> Axes:  # pragma: no cover
        return self._baseplot(*args, **kwargs)


class VolumeNomograph(object):
    def __init__(
        self,
        size: Union[pandas.Series, numpy.ndarray],
        ddt: Union[pandas.Series, numpy.ndarray],
        performance: Union[pandas.Series, numpy.ndarray],
        interp_kwargs: Optional[Dict[str, Any]] = None,
        source_data: str = None,
    ) -> None:

        self.nomo = NomographBase(
            x=size, t=ddt, y=performance, interp_kwargs=interp_kwargs
        )

        self.size = self.nomo.x_data
        self.ddt = self.nomo.t_data
        self.performance = self.nomo.y_data
        self.source_data = source_data

    def plot(self, *args: Tuple, **kwargs: Dict[str, Any]) -> Axes:  # pragma: no cover
        ax = self.nomo._baseplot(*args, **kwargs)
        ax.set_xlabel("size")
        ax.set_ylabel("performance")
        ax.legend(ncol=2, title="ddt")
        return ax

    def __call__(
        self,
        *,
        size: Optional[Any] = None,
        ddt: Optional[Any] = None,
        performance: Optional[Any] = None,
    ) -> Any:
        return self.nomo(x=size, t=ddt, y=performance)


class FlowNomograph(object):
    def __init__(
        self,
        intensity: Union[pandas.Series, numpy.ndarray],
        tc: Union[pandas.Series, numpy.ndarray],
        performance: Union[pandas.Series, numpy.ndarray],
        interp_kwargs: Optional[Dict[str, Any]] = None,
        source_data: str = None,
    ) -> None:

        self.nomo = NomographBase(
            x=intensity, t=tc, y=performance, interp_kwargs=interp_kwargs
        )

        self.intensity = self.nomo.x_data
        self.tc = self.nomo.t_data
        self.performance = self.nomo.y_data
        self.source_data = source_data

    def plot(self, *args: Tuple, **kwargs: Dict[str, Any]) -> Axes:  # pragma: no cover
        ax = self.nomo._baseplot(*args, **kwargs)
        ax.set_xlabel("intensity")
        ax.set_ylabel("performance")
        ax.legend(ncol=2, title="tc")
        return ax

    def __call__(
        self,
        *,
        intensity: Optional[Any] = None,
        tc: Optional[Any] = None,
        performance: Optional[Any] = None,
    ) -> Any:
        return self.nomo(x=intensity, t=tc, y=performance)
