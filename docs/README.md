# 项目文档

根目录 [README.md](../README.md) 提供功能概览与快速编译；本目录为详细说明。

| 文档 | 说明 |
|------|------|
| [DEPLOY.md](DEPLOY.md) | 新电脑部署（Cursor + EIM）、打包迁移、常见问题 |
| [DEVELOPMENT.md](DEVELOPMENT.md) | 代码分层、注释规范、模块 API、新增功能步骤 |
| [HARDWARE.md](HARDWARE.md) | LCD / 摇杆接线与 GPIO |
| [LED.md](LED.md) | D4/D5 闪烁测试（默认关，menuconfig 开启） |
| [archive/README-legacy.md](archive/README-legacy.md) | **归档**：原 1100+ 行完整 README |

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/setup-env.ps1` | 新电脑安装 ESP-IDF v5.3.2（EIM） |
| `scripts/build.ps1` | v5.3.2 / EIM 环境编译 |
| `scripts/build-v55.ps1` | ESP-IDF v5.5 编译（推荐） |
| `scripts/package-project.ps1` | 打包源码 zip |
| `scripts/ota-console.ps1` | 打开 OTA 网页控制台 |

## 版本

见根目录 README「版本历史」。发布标签：`v1.0.0`、`v1.0.1` 等。
