"""Math: expression calculator, percentage, statistics, quadratic solver."""

from __future__ import annotations

import ast
import math
import statistics
from typing import Any

from ..schema import Field, Module, error, kv, listout, note, opts, value

TRIG = {"sin", "cos", "tan"}
INV_TRIG = {"asin", "acos", "atan", "atan2"}

FUNCTIONS: dict[str, Any] = {
    "sqrt": math.sqrt,
    "cbrt": lambda x: math.copysign(abs(x) ** (1.0 / 3.0), x),
    "abs": abs,
    "exp": math.exp,
    "ln": math.log,
    "log": math.log10,
    "log2": math.log2,
    "floor": math.floor,
    "ceil": math.ceil,
    "round": round,
    "hypot": math.hypot,
    "pow": math.pow,
    "min": min,
    "max": max,
}

CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}

# Trig needs the angle mode, so it is handled separately from FUNCTIONS.
NAMES = set(FUNCTIONS) | set(CONSTANTS) | TRIG | INV_TRIG

NORMALISE = str.maketrans({"×": "*", "÷": "/", "−": "-", "^": "**", "π": "pi", "√": "sqrt"})


def _eval_node(node: ast.AST, mode: str) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, mode)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("only numbers are allowed")
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id in CONSTANTS:
            return CONSTANTS[node.id]
        raise ValueError(f"unknown name “{node.id}”")
    if isinstance(node, ast.UnaryOp):
        val = _eval_node(node.operand, mode)
        if isinstance(node.op, ast.USub):
            return -val
        if isinstance(node.op, ast.UAdd):
            return val
        raise ValueError("unsupported unary operator")
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, mode)
        right = _eval_node(node.right, mode)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            if right == 0:
                raise ValueError("division by zero")
            return left / right
        if isinstance(op, ast.FloorDiv):
            if right == 0:
                raise ValueError("division by zero")
            return left // right
        if isinstance(op, ast.Mod):
            if right == 0:
                raise ValueError("modulo by zero")
            return left % right
        if isinstance(op, ast.Pow):
            if abs(right) > 4096:
                raise ValueError("exponent too large")
            return left**right
        raise ValueError("unsupported operator")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in NAMES:
            raise ValueError("unknown function")
        if node.keywords:
            raise ValueError("keyword arguments are not supported")
        args = [_eval_node(a, mode) for a in node.args]
        name = node.func.id
        if name in TRIG:
            x = math.radians(args[0]) if mode == "deg" else args[0]
            return {"sin": math.sin, "cos": math.cos, "tan": math.tan}[name](x)
        if name in INV_TRIG:
            raw = {"asin": math.asin, "acos": math.acos, "atan": math.atan, "atan2": math.atan2}[name](
                *args
            )
            return math.degrees(raw) if mode == "deg" else raw
        return float(FUNCTIONS[name](*args))
    raise ValueError("that expression is not supported")


def evaluate(expression: str, mode: str = "deg") -> float:
    clean = (expression or "").translate(NORMALISE).strip()
    if not clean:
        raise ValueError("empty expression")
    if len(clean) > 500:
        raise ValueError("expression too long")
    tree = ast.parse(clean, mode="eval")
    return _eval_node(tree, mode)


def _pretty(n: float) -> str:
    if n != n or n in (float("inf"), float("-inf")):
        return "undefined"
    if n == int(n) and abs(n) < 1e15:
        return f"{int(n):,}"
    return f"{n:,.10g}"


class Calculator(Module):
    id = "calc"
    category = "math"
    title = "Calculator"
    subtitle = "Expressions, functions and constants"
    icon = "calculator"
    view = "calculator"
    keywords = (
        "calculator", "expression", "arithmetic", "sin", "cos", "tan", "sqrt",
        "power", "sqrt", "log", "pi", "evaluate", "compute",
    )
    fields = (
        Field(
            "expr",
            "text",
            "Expression",
            default="",
            placeholder="2 * (3 + 4) ^ 2",
            hint="Functions: sqrt, ln, log, sin, cos, tan, abs, round",
            mono=True,
        ),
        Field(
            "angle",
            "select",
            "Angles",
            default="deg",
            options=opts(("deg", "Degrees"), ("rad", "Radians")),
            visible_when={"key": "expr", "not": ""},
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        expr = str(v["expr"]).strip()
        if not expr:
            return [note("Type an expression, or use the keypad below.")]
        try:
            result = evaluate(expr, v["angle"])
        except ZeroDivisionError:
            return [error("Division by zero.")]
        except Exception as exc:  # ValueError, SyntaxError, OverflowError
            return [error(f"{exc}")]
        outputs = [
            value("Result", _pretty(result)),
            kv(
                "Details",
                [
                    ("Exact", f"{result!r}"),
                    ("Rounded", f"{round(result, 6):,}"),
                    ("Scientific", f"{result:.6e}"),
                ],
            ),
        ]
        if v["angle"] == "deg" and any(fn in expr for fn in ("sin", "cos", "tan")):
            outputs.append(note("Trig functions are reading degrees."))
        return outputs


class Percentage(Module):
    id = "percent"
    category = "math"
    title = "Percentage"
    subtitle = "Of, is, change and adjust"
    icon = "percent"
    keywords = ("percent", "percentage", "increase", "decrease", "change", "discount", "tip", "markup", "of")
    fields = (
        Field(
            "mode",
            "select",
            "Question",
            default="of",
            options=opts(
                ("of", "What is X% of Y?"),
                ("is", "X is what percent of Y?"),
                ("change", "Percent change from X to Y"),
                ("apply", "Increase or decrease X by Y%"),
            ),
        ),
        Field("a", "number", "X", default=15.0, step=1.0),
        Field("b", "number", "Y", default=80.0, step=1.0),
        Field(
            "direction",
            "select",
            "Direction",
            default="up",
            options=opts(("up", "Increase"), ("down", "Decrease")),
            visible_when={"key": "mode", "in": ["apply"]},
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        a, b = float(v["a"]), float(v["b"])
        mode = v["mode"]
        if mode == "of":
            result = a / 100.0 * b
            return [
                value("Result", _pretty(result)),
                kv("Working", [(f"{_pretty(a)}% of {_pretty(b)}", _pretty(result)), ("As fraction", f"{_pretty(a)}/100 × {_pretty(b)}")]),
            ]
        if mode == "is":
            if b == 0:
                return [error("Cannot compute a percentage of zero.")]
            result = a / b * 100.0
            return [
                value("Result", f"{_pretty(result)}%"),
                kv("Working", [(f"{_pretty(a)} ÷ {_pretty(b)}", _pretty(a / b)), ("Percent", f"{_pretty(result)}%")]),
            ]
        if mode == "change":
            if a == 0:
                return [error("Percent change from zero is undefined.")]
            result = (b - a) / abs(a) * 100.0
            word = "increase" if result > 0 else "decrease" if result < 0 else "no change"
            return [
                value("Change", f"{result:+,.4f}%".replace("+", "+" if result >= 0 else "")),
                kv(
                    "Working",
                    [
                        ("Difference", _pretty(b - a)),
                        ("Direction", word),
                        ("Multiplier", f"×{b / a:,.6g}"),
                    ],
                ),
            ]
        pct = b / 100.0
        result = a * (1 + pct) if v["direction"] == "up" else a * (1 - pct)
        return [
            value("Result", _pretty(result)),
            kv(
                "Working",
                [
                    ("Amount", f"{_pretty(abs(result - a))}"),
                    ("Original", _pretty(a)),
                    ("Multiplier", f"×{1 + pct if v['direction'] == 'up' else 1 - pct:,.6g}"),
                ],
            ),
        ]


NUM_RE = None


def parse_numbers(text: str) -> list[float]:
    import re

    global NUM_RE
    if NUM_RE is None:
        NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
    return [float(x) for x in NUM_RE.findall(text or "")]


class StatisticsTool(Module):
    id = "stats"
    category = "math"
    title = "Statistics"
    subtitle = "Mean, median, spread and quartiles"
    icon = "bars"
    keywords = ("statistics", "mean", "average", "median", "mode", "stdev", "variance", "quartile", "sum", "spread")
    fields = (
        Field(
            "numbers",
            "textarea",
            "Numbers",
            default="",
            placeholder="12, 7, 3, 21, 7 …",
            hint="Separate with commas, spaces or new lines",
            rows=4,
            mono=True,
        ),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        nums = parse_numbers(v["numbers"])
        if not nums:
            return [note("Paste numbers — commas, spaces or new lines all work.")]
        n = len(nums)
        mean = statistics.fmean(nums)
        med = statistics.median(nums)
        modes = statistics.multimode(nums)
        spread = max(nums) - min(nums)
        pairs: list[tuple[str, Any]] = [
            ("Count", n),
            ("Sum", _pretty(sum(nums))),
            ("Mean", f"{mean:,.6g}"),
            ("Median", _pretty(med)),
            ("Mode", ", ".join(_pretty(m) for m in modes[:4])),
            ("Min", _pretty(min(nums))),
            ("Max", _pretty(max(nums))),
            ("Range", _pretty(spread)),
        ]
        if n >= 2:
            variance = statistics.variance(nums)
            pairs.extend(
                [
                    ("Std dev (sample)", f"{math.sqrt(variance):,.6g}"),
                    ("Variance", f"{variance:,.6g}"),
                    ("Std dev (pop.)", f"{statistics.pstdev(nums):,.6g}"),
                ]
            )
            if n >= 4:
                q1, _, q3 = statistics.quantiles(nums, n=4, method="inclusive")
                pairs.append(("IQR", f"{q3 - q1:,.6g}"))
        outputs = [kv("Summary", pairs)]
        if n >= 2:
            if n >= 4:
                q1, _, q3 = statistics.quantiles(nums, n=4, method="inclusive")
                outputs.append(
                    kv("Quartiles", [("Q1", f"{q1:,.6g}"), ("Mid", f"{med:,.6g}"), ("Q3", f"{q3:,.6g}")])
                )
            outputs.append(listout("Sorted", [f"{x:,.6g}" for x in sorted(nums)]))
        else:
            outputs.append(note("Add at least two values for spread."))
        return outputs


class Quadratic(Module):
    id = "quadratic"
    category = "math"
    title = "Quadratic Solver"
    subtitle = "ax² + bx + c = 0, roots and vertex"
    icon = "parabola"
    keywords = ("quadratic", "roots", "discriminant", "parabola", "vertex", "solve", "equation", "algebra", "complex")
    fields = (
        Field("a", "number", "a", default=1.0, step=1.0),
        Field("b", "number", "b", default=-3.0, step=1.0),
        Field("c", "number", "c", default=2.0, step=1.0),
    )

    @classmethod
    def run(cls, v: dict[str, Any]) -> list[dict[str, Any]]:
        a, b, c = float(v["a"]), float(v["b"]), float(v["c"])
        if a == 0:
            if b == 0:
                return [error("Not an equation: a and b are both zero.")]
            return [
                value("Root", _pretty(-c / b)),
                note("a = 0, so this solves as a linear equation."),
            ]
        disc = b * b - 4 * a * c
        vertex_x = -b / (2 * a)
        vertex_y = c - b * b / (4 * a)
        if disc > 0:
            roots = [(-b + math.sqrt(disc)) / (2 * a), (-b - math.sqrt(disc)) / (2 * a)]
            kind = "two real roots"
            root_pairs = [("x₁", _pretty(roots[0])), ("x₂", _pretty(roots[1]))]
        elif disc == 0:
            kind = "one repeated root"
            root_pairs = [("x", _pretty(vertex_x))]
        else:
            re = -b / (2 * a)
            im = math.sqrt(-disc) / (2 * a)
            kind = "two complex roots"
            root_pairs = [
                ("x₁", f"{re:,.6g} + {abs(im):,.6g}i"),
                ("x₂", f"{re:,.6g} − {abs(im):,.6g}i"),
            ]
        return [
            kv("Roots", root_pairs),
            kv(
                "Equation",
                [
                    ("Discriminant", f"{disc:,.6g}"),
                    ("Nature", kind),
                    ("Vertex", f"({vertex_x:,.6g}, {vertex_y:,.6g})"),
                    ("Axis", f"x = {vertex_x:,.6g}"),
                ],
            ),
            value("Factored", _factored(a, b, c, disc), mono=True),
        ]


def _factored(a: float, b: float, c: float, disc: float) -> str:
    if disc < 0:
        return "no real factorisation"
    if disc == 0:
        return f"{_pretty(a)}(x − ({_pretty(-b / (2 * a))}))²"
    r1 = (-b + math.sqrt(disc)) / (2 * a)
    r2 = (-b - math.sqrt(disc)) / (2 * a)
    left = "" if a == 1 else _pretty(a)
    return f"{left}(x − {_pretty(r1)})(x − {_pretty(r2)})"
