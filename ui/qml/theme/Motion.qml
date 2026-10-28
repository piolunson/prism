pragma Singleton
import QtQuick

/* Apple's motion idea — springy, interruptible, momentum-aware — translated to
   QML's spring integrator.

   QML's SpringAnimation does not accept Apple's (damping ratio, response) pair
   directly, and naive values in ω₀ = 2π/response units diverge numerically
   (measured: spring ≥ 160 explodes).  These presets were measured with
   tools/spring_probe.py on a 100 px move, so the numbers below are observed
   settle times, not hopes:

       spring 12, damping 3.4  → 384 ms, no overshoot   (sheets, large surfaces)
       spring 16, damping 4.0  → 272 ms, no overshoot   (hover lifts, palette)
       spring 22, damping 5.5  → 192 ms, no overshoot   (selection, small reveals)
       spring 30, damping 8.0  → 128 ms, no overshoot   (press feedback)
       spring 20, damping 0.6  → 176 ms, ~8% overshoot  (flick release)

   House style is critically damped by default; bounce is reserved for gestures
   that actually carried momentum. */
QtObject {
    readonly property real mass: 1.0

    readonly property real springPress: 30
    readonly property real dampingPress: 8.0

    readonly property real springQuick: 22
    readonly property real dampingQuick: 5.5

    readonly property real springSettle: 16
    readonly property real dampingSettle: 4.0

    readonly property real springSheet: 12
    readonly property real dampingSheet: 3.4

    readonly property real springFlick: 20
    readonly property real dampingFlick: 0.6

    /* Apple's exponential-decay momentum projection (Designing Fluid
       Interfaces).  decelerationRate 0.998 ≈ natural scroll feel. */
    function project(velocity, rate) {
        var d = (rate === undefined) ? 0.998 : rate;
        return (velocity / 1000) * d / (1 - d);
    }

    /* Progressive resistance past a boundary instead of a hard stop. */
    function rubberband(overshoot, dimension, constant) {
        var c = (constant === undefined) ? 0.55 : constant;
        return (overshoot * dimension * c) / (dimension + c * Math.abs(overshoot));
    }

    function clamp(value, low, high) {
        return Math.max(low, Math.min(high, value));
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }
}
