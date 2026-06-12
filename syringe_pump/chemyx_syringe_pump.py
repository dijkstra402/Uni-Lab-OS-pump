"""
Chemyx 注射泵 — 继承标准模板的真实品牌实现示例

演示「品牌驱动如何继承注射泵标准设备类(SyringePump)」:
  - 方法名 / 参数名 / property 名全部沿用标准模板 → 工作流可跨品牌
  - 方法体填入 Chemyx 私有命令 (openConnection/setVolume/setRate/startPump...)

上游 SDK: https://github.com/cukelarter/Chemyx-Syringe-Pump
真实硬件类: python_dist/core/connect.py 中的 Connection (pyserial 通信)
"""

from typing import Any, Dict, Optional

from unilabos.registry.decorators import device, action, topic_config

from syringe_pump.syringe_pump import SyringePump


@device(
    id="syringe_pump_chemyx",          # 品牌专属 id (区别于标准类 syringe_pump)
    category=["注射泵"],                 # 与标准模板同一大类 → 工作流跨品牌识别
    description="Chemyx 注射泵 (Fusion 系列)，继承注射泵标准接口。",
    display_name="Chemyx 注射泵",
)
class ChemyxSyringePump(SyringePump):
    """Chemyx 品牌注射泵，把标准动作映射到 Chemyx 私有命令。"""

    def __init__(self, device_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        初始化设备。

        Args:
            device_id[设备ID]: 设备实例 ID。
            config[设备配置]: 设备启动配置 (port/baudrate/diameter 等)。
        """
        super().__init__(device_id or "syringe_pump_chemyx", config, **kwargs)
        self._conn = None  # 上游 Connection 对象，惰性创建

    def _ensure_conn(self):
        """惰性建立与硬件的串口连接 (避免无硬件时导入即失败)。"""
        if self._conn is None:
            from core.connect import Connection  # 上游 SDK
            self._conn = Connection(
                port=self.config.get("port", "COM1"),
                baudrate=self.config.get("baudrate", 9600),
            )
        return self._conn

    @action(description="初始化")
    def initialize(self) -> Dict[str, Any]:
        """打开串口并设置注射器直径/单位。"""
        conn = self._ensure_conn()
        conn.openConnection()
        if "diameter" in self.config:
            conn.setDiameter(self.config["diameter"])
        if "units" in self.config:
            conn.setUnits(self.config["units"])
        self.data["status"] = "idle"
        return {"success": True}

    @action(description="绝对控制")
    def move_absolute(self, position: int = 0) -> Dict[str, Any]:
        """
        移动到绝对位置 (按目标体积驱动柱塞)。

        Args:
            position[绝对位置设置]: 目标体积/位置。
        """
        conn = self._ensure_conn()
        conn.setVolume(position)
        conn.startPump()
        self.data["status"] = "running"
        return {"success": True}

    @action(description="抽液")
    def aspirate(self, aspirate_position: int = 0) -> Dict[str, Any]:
        """
        抽液: 设置正向体积并启动泵。

        Args:
            aspirate_position[抽液位置设置]: 抽液目标体积/位置。
        """
        conn = self._ensure_conn()
        conn.setVolume(abs(aspirate_position))   # 正值 = 抽液
        conn.startPump()
        self.data["status"] = "aspirating"
        return {"success": True}

    @action(description="排液")
    def dispense(self, dispense_position: int = 0) -> Dict[str, Any]:
        """
        排液: 设置反向体积并启动泵。

        Args:
            dispense_position[排液位置设置]: 排液目标体积/位置。
        """
        conn = self._ensure_conn()
        conn.setVolume(-abs(dispense_position))  # 负值 = 排液
        conn.startPump()
        self.data["status"] = "dispensing"
        return {"success": True}

    @property
    @topic_config()
    def status(self) -> str:
        """从 Chemyx 读取实时泵状态。"""
        if self._conn is None:
            return self.data.get("status", "idle")
        try:
            return str(self._conn.getPumpStatus())
        except Exception:
            return self.data.get("status", "idle")

    @property
    @topic_config()
    def current_position(self) -> int:
        """从 Chemyx 读取已位移体积作为当前位置。"""
        if self._conn is None:
            return self.data.get("current_position", 0)
        try:
            return int(self._conn.getDisplacedVolume())
        except Exception:
            return self.data.get("current_position", 0)
