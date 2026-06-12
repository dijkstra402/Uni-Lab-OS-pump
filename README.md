# 注射泵 — 标准设备类模板 (Syringe Pump Device Class Template)

基于 [LabDeviceTemplate](https://github.com/Xuwznln/LabDeviceTemplate) 的 Uni-Lab-OS 外部设备包。

定义「注射泵」这一设备**大类**的标准动作(action)与状态属性(property)。同一大类下不同品牌的注射泵都应实现这套统一接口，使**一套工作流可以跨品牌控制整类设备**。

> 本模板只定义标准接口，方法体为 `pass`（占位）。具体品牌的真实实现由各驱动包继承/对接。

## 标准接口

### 动作 (action)

| 方法 | 说明 | 参数 |
|------|------|------|
| `initialize()` | 初始化 | — |
| `move_absolute(position)` | 绝对控制 | `position` 绝对位置 |
| `aspirate(aspirate_position)` | 抽液 | `aspirate_position` 抽液目标位置 |
| `dispense(dispense_position)` | 排液 | `dispense_position` 排液目标位置 |

### 状态属性 (property)

| 属性 | 说明 | 类型 |
|------|------|------|
| `status` | 设备运行状态 | str |
| `fault` | 故障标志 | bool |
| `fault_code` | 故障代码 | int |
| `current_position` | 当前位置 | int |

## 目录结构

```
├── README.md
├── requirements.txt              # Python 依赖（模板为空，实现时追加）
├── pyproject.toml                # 包配置（支持 pip install -e .）
├── .github/workflows/
│   └── check_registry.yml        # CI 自动验证注册表
├── syringe_pump/                 # 设备包
│   ├── __init__.py
│   └── syringe_pump.py           # 注射泵标准类定义
└── .gitignore
```

## 本地验证

```bash
# 创建 conda 环境并安装 unilabos
mamba create -n unilab python=3.11.14 -c conda-forge -y
mamba activate unilab
mamba install uni-lab::unilabos -c uni-lab -c robostack-staging -c conda-forge -y

# 校验注册表 (check mode)
unilab --check_mode --devices ./syringe_pump --external_devices_only
```

Push 代码后，GitHub Actions 会自动运行 `--check_mode` 验证设备定义是否正确。

## 为某品牌实现真实驱动

1. 继承本标准类，或在新类中实现同名 action / property；
2. 在方法体内填入该品牌的真实通信逻辑（替换 `pass`）；
3. 在 `requirements.txt` 中追加所需依赖；
4. 保持 action 名称、参数名与 property 名称不变，以确保跨品牌工作流兼容。

## License

MIT
