from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Sequence,
    TypeVar,
    cast,
)

import numpy
import pandas
from numpy.typing import ArrayLike
from scipy.interpolate import CloughTocher2DInterpolator as CT2DI

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    pass

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
else:
    Axes = Any

DIM = TypeVar("DIM", Sequence[float | int], pandas.Series, ArrayLike)


def bisection_search(
    function: Callable[[float], float],
    seek_value: float,
    bounds: tuple[float, float] | None = None,
    atol: float | None = None,
    max_iters: int | None = None,
) -> tuple[float, bool]:
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

        if abs(diff) < atol:
            converged = True
            return guess, converged

        if diff > 0:
            result = guess
        else:
            old_result = guess

        guess = (result + old_result) / 2

    return guess, converged


class NomographBase:
    def __init__(
        self,
        *,
        x: DIM,
        t: DIM,
        y: DIM,
        interp_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """This class manages 2D interpolations of stormwater treatment facility performance
        across the size, drawdown time, and long term capture.

        Inputs for `size`, `ddt`, and `performance` should all have the same shape.

        when grouped by 'trace' each set of x and y pairs should start and stop at the
        same value, but each set does not have to be the same length. for example, each
        trace group should have a value @ x=0, and all traces should have the same value
        for their maximum x value. This allows the 2d interpolation to be properly rectangular
        instead of having portions of the searchspace undefined (numpy.nan).

        x : 1D, listlike
            indicates stormwater treatment facility size, typically either design intensity or volume

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
        self.x_data = numpy.array(x)
        self.t_data = numpy.array(t)
        self.y_data = numpy.array(y)
        self._interp_kwargs = interp_kwargs

        self._nomo: Callable | None = None
        self._ct2di: Callable | None = None

    @property
    def interp_kwargs(self) -> dict[str, Any]:  # pragma: no cover
        if self._interp_kwargs is None:
            self._interp_kwargs = {"rescale": False}
        return self._interp_kwargs

    @property
    def ct2di(self):
        if self._ct2di is None:
            self._ct2di = CT2DI(
                points=numpy.column_stack((self.x_data, self.t_data)),
                values=self.y_data,
                **self.interp_kwargs,
            )
        return self._ct2di

    @property
    def nomo(self) -> Callable:
        if self._nomo is None:

            def clipped_nomo(*args, **kwargs):
                res = self.ct2di(*args, **kwargs)
                return numpy.clip(res, a_min=0, a_max=None)

            self._nomo = clipped_nomo

        return self._nomo

    def get_x(
        self,
        at_y: float,
        t: float,
        atol: float | None = None,
        max_iters: int | None = None,
    ) -> tuple[float, bool]:
        """Goal seek at 'y' to find x at a given value of t

        This method answers the question 'how big do i make a facility to achieve
        y% capture if i keep the 'trace' `t` constant?'

        """

        if at_y <= 1e-3:  # pragma: no cover
            return 0.0, False

        at_y = numpy.clip(at_y, numpy.nanmin(self.y_data), numpy.nanmax(self.y_data))
        t = numpy.clip(t, numpy.nanmin(self.t_data), numpy.nanmax(self.t_data))

        _nomo: Callable[[float, float], float] = self.nomo

        def function(x: float) -> float:
            return _nomo(x, t)

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
        x: Any | None = None,
        t: Any | None = None,
        y: Any | None = None,
        atol: float | None = None,
        max_iters: int | None = None,
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
            result: float | Sequence[float] = self.nomo(x, t)
            return result

        # goal seek x via search
        elif x is None and y is not None:
            y = numpy.clip(y, numpy.nanmin(self.y_data), numpy.nanmax(self.y_data))

            if numpy.iterable(t) and numpy.iterable(y):
                t_iter = numpy.array(t)
                y_iter = numpy.array(y)
                if t_iter.size == y_iter.size:
                    res: list[float] = []
                    for _y, _t in zip(y_iter, t_iter, strict=True):
                        guess, _ = self.get_x(
                            at_y=_y, t=_t, atol=atol, max_iters=max_iters
                        )
                        res.append(guess)
                    arr_result: numpy.ndarray = numpy.array(res)

                    return arr_result
                else:
                    raise ValueError("y and t must be the same length")

            guess, converged = self.get_x(at_y=y, t=t, atol=atol, max_iters=max_iters)  # type: ignore

            if not converged:
                pass
                # TODO: do something fancy with the warning?
            return guess
        else:
            raise ValueError("must call with `t` and either `x` or `y`")

    def _baseplot(self, ax: Axes | None = None, **kwargs: dict[str, Any]) -> Axes:
        if ax is None:  # pragma: no branch
            _, ax = cast(tuple[Any, Axes], plt.subplots())

        xmin, xmax = numpy.nanmin(self.x_data), numpy.nanmax(self.x_data)
        xline = numpy.linspace(xmin, xmax, 100)

        fits = self(x=self.x_data, t=self.t_data)

        ax.scatter(
            self.x_data,
            fits,
            marker="o",  # type: ignore
            s=50,
            facecolor="none",
            edgecolor="k",
            alpha=0.4,
        )

        for _i, d in enumerate(sorted(set(self.t_data))):
            x = self.x_data[self.t_data == d]  # type: ignore
            y = self.y_data[self.t_data == d]  # type: ignore

            xline = numpy.linspace(numpy.nanmin(x), numpy.nanmax(x), 100)
            vals = self.nomo(xline, [d for _ in xline])

            ax.plot(xline, vals, "-k", alpha=0.2)

            ax.scatter(x, y, s=15, label=str(d), zorder=10, alpha=0.5)

        return ax

    def _basesurface(self, ax: Axes | None = None, **kwargs: dict[str, Any]) -> Axes:
        if ax is None:  # pragma: no branch
            _, ax = cast(tuple[Any, Axes], plt.subplots())

        ax.tricontourf(self.x_data, self.t_data, self.y_data, levels=255)

        t = numpy.linspace(1, numpy.max(self.t_data), 100)
        for i, perf in enumerate([0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.97]):
            x = [self(t=_t, y=perf) for _t in t]
            ax.plot(x, t, c=f"C{i}", label=f"{perf:.0%}")

        return ax

    def plot(self, *args: tuple, **kwargs: dict[str, Any]) -> Axes:  # pragma: no cover
        return self._baseplot(*args, **kwargs)  # type: ignore

    def surfaceplot(
        self, *args: tuple, **kwargs: dict[str, Any]
    ) -> Axes:  # pragma: no cover
        return self._basesurface(*args, **kwargs)  # type: ignore


class VolumeNomograph:
    def __init__(
        self,
        size: DIM,
        ddt: DIM,
        performance: DIM,
        interp_kwargs: dict[str, Any] | None = None,
        source_data: str | None = None,
    ) -> None:
        self.nomo = NomographBase(
            x=size, t=ddt, y=performance, interp_kwargs=interp_kwargs
        )

        self.size = self.nomo.x_data
        self.ddt = self.nomo.t_data
        self.performance = self.nomo.y_data
        self.source_data = source_data

    def __call__(
        self,
        *,
        size: Any | None = None,
        ddt: Any | None = None,
        performance: Any | None = None,
    ) -> Any:
        return self.nomo(x=size, t=ddt, y=performance)

    def plot(self, *args: tuple, **kwargs: dict[str, Any]) -> Axes:
        ax = self.nomo._baseplot(*args, **kwargs)  # type: ignore
        ax.set_xlabel("size")
        ax.set_ylabel("performance")
        ax.legend(loc=6, bbox_to_anchor=(1.01, 0.5), ncol=2, title="ddt")
        return ax

    def surface_plot(self, *args: tuple, **kwargs: dict[str, Any]) -> Axes:
        ax = self.nomo._basesurface(*args, **kwargs)  # type: ignore
        ax.set_xlabel("size")
        ax.set_ylabel("ddt")
        ax.legend(loc=6, bbox_to_anchor=(1.01, 0.5))
        return ax


class FlowNomograph:
    def __init__(
        self,
        intensity: DIM,
        tc: DIM,
        performance: DIM,
        interp_kwargs: dict[str, Any] | None = None,
        source_data: str | None = None,
    ) -> None:
        self.nomo = NomographBase(
            x=intensity, t=tc, y=performance, interp_kwargs=interp_kwargs
        )

        self.intensity = self.nomo.x_data
        self.tc = self.nomo.t_data
        self.performance = self.nomo.y_data
        self.source_data = source_data

    def __call__(
        self,
        *,
        intensity: Any | None = None,
        tc: Any | None = None,
        performance: Any | None = None,
    ) -> Any:
        return self.nomo(x=intensity, t=tc, y=performance)

    def plot(self, *args: tuple, **kwargs: dict[str, Any]) -> Axes:
        ax = self.nomo._baseplot(*args, **kwargs)  # type: ignore
        ax.set_xlabel("intensity")
        ax.set_ylabel("performance")
        ax.legend(ncol=2, title="tc")
        return ax

    def surface_plot(self, *args: tuple, **kwargs: dict[str, Any]) -> Axes:
        ax = self.nomo._basesurface(*args, **kwargs)  # type: ignore
        ax.set_xlabel("intensity")
        ax.set_ylabel("tc")
        ax.legend(loc=6, bbox_to_anchor=(1.01, 0.5))
        return ax
