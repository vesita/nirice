"""Niri 动效方案预设。"""

from __future__ import annotations

from nirice.models import AnimationPreset

# ==============================================================================
# 1. 动效方案（animations 代码块）
# ==============================================================================

ARCTIC_ANIMATIONS = """animations {
    // 工作区与横向滚动视口
    workspace-switch {
        spring damping-ratio=1.0 stiffness=1000 epsilon=0.0001
    }
    horizontal-view-movement {
        spring damping-ratio=1.0 stiffness=900 epsilon=0.0001
    }

    // 窗口生命周期
    window-open {
        duration-ms 200
        curve "ease-out-quad"
    }
    window-close {
        duration-ms 200
        curve "ease-out-cubic"
    }
    window-movement {
        spring damping-ratio=1.0 stiffness=800 epsilon=0.0001
    }
    window-resize {
        spring damping-ratio=1.0 stiffness=1000 epsilon=0.0001
    }

    // 界面浮层
    config-notification-open-close {
        spring damping-ratio=0.6 stiffness=1200 epsilon=0.001
    }
    screenshot-ui-open {
        duration-ms 300
        curve "ease-out-quad"
    }
    overview-open-close {
        spring damping-ratio=1.0 stiffness=900 epsilon=0.0001
    }
}
"""

SNAPPY_ANIMATIONS = """animations {
    workspace-switch {
        spring damping-ratio=1.0 stiffness=1600 epsilon=0.0001
    }
    horizontal-view-movement {
        spring damping-ratio=1.0 stiffness=1500 epsilon=0.0001
    }

    window-open {
        duration-ms 110
        curve "ease-out-quad"
    }
    window-close {
        duration-ms 90
        curve "ease-out-cubic"
    }
    window-movement {
        spring damping-ratio=1.0 stiffness=1400 epsilon=0.0001
    }
    window-resize {
        spring damping-ratio=1.0 stiffness=1600 epsilon=0.0001
    }

    config-notification-open-close {
        spring damping-ratio=0.8 stiffness=1800 epsilon=0.001
    }
    screenshot-ui-open {
        duration-ms 150
        curve "ease-out-quad"
    }
    overview-open-close {
        spring damping-ratio=1.0 stiffness=1500 epsilon=0.0001
    }
}
"""

SILKY_ANIMATIONS = """animations {
    workspace-switch {
        spring damping-ratio=0.85 stiffness=650 epsilon=0.0001
    }
    horizontal-view-movement {
        spring damping-ratio=0.85 stiffness=600 epsilon=0.0001
    }

    window-open {
        duration-ms 300
        curve "ease-out-expo"
    }
    window-close {
        duration-ms 260
        curve "ease-out-quart"
    }
    window-movement {
        spring damping-ratio=0.9 stiffness=550 epsilon=0.0001
    }
    window-resize {
        spring damping-ratio=0.9 stiffness=650 epsilon=0.0001
    }

    config-notification-open-close {
        spring damping-ratio=0.7 stiffness=900 epsilon=0.001
    }
    screenshot-ui-open {
        duration-ms 380
        curve "ease-out-expo"
    }
    overview-open-close {
        spring damping-ratio=0.85 stiffness=600 epsilon=0.0001
    }
}
"""

# niri 关闭动效即移除整个 animations 段；空块在部分版本会被判为非法，
# 因此这里用极短时长 + 满阻尼弹簧来达到事实上的"瞬时"效果。
INSTANT_ANIMATIONS = """animations {
    workspace-switch {
        spring damping-ratio=1.0 stiffness=100000 epsilon=0.0001
    }
    horizontal-view-movement {
        spring damping-ratio=1.0 stiffness=100000 epsilon=0.0001
    }
    window-open {
        duration-ms 1
        curve "linear"
    }
    window-close {
        duration-ms 1
        curve "linear"
    }
    window-movement {
        spring damping-ratio=1.0 stiffness=100000 epsilon=0.0001
    }
    window-resize {
        spring damping-ratio=1.0 stiffness=100000 epsilon=0.0001
    }
    config-notification-open-close {
        duration-ms 1
        curve "linear"
    }
    screenshot-ui-open {
        duration-ms 1
        curve "linear"
    }
    overview-open-close {
        spring damping-ratio=1.0 stiffness=100000 epsilon=0.0001
    }
}
"""

ANIMATION_PRESETS: dict[str, AnimationPreset] = {
    "arctic": AnimationPreset(
        name="Arctic",
        description="CachyOS 默认的弹簧流体动效（900~1000 刚度、200ms 缓动窗口开合）",
        animations_kdl=ARCTIC_ANIMATIONS,
        notes=["均衡的弹簧阻尼，滚动视口跟随干脆利落。"],
    ),
    "snappy": AnimationPreset(
        name="Snappy",
        description="高刷电竞级极速响应（110ms 窗口开合、1600 刚度视口）",
        animations_kdl=SNAPPY_ANIMATIONS,
        notes=["零延迟反馈，适合高刷新率屏幕。"],
    ),
    "silky": AnimationPreset(
        name="Silky",
        description="丝滑柔顺的长缓动（300ms ease-out-expo、低阻尼弹簧）",
        animations_kdl=SILKY_ANIMATIONS,
        notes=["强调优雅与连贯，代价是响应稍慢。"],
    ),
    "instant": AnimationPreset(
        name="Instant",
        description="几乎无动效的瞬时切换（1ms 线性）",
        animations_kdl=INSTANT_ANIMATIONS,
        notes=["最省电、最直接，适合远程桌面或低性能设备。"],
    ),
}
