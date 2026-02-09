## 缺少环境变量（AJG_EMAIL / AJG_PASSWORD）

抓取脚本默认从环境变量读取登录凭据。请在同一个终端会话中设置：

```bash
export AJG_EMAIL="lingguiwang@yeah.net"
export AJG_PASSWORD="你的密码"
```

也可参考示例文件：`scripts/ajg_config.example.env`（不要把真实密码写进 git）。

## 登录后仍被 gate 拦截 / 需要验证码

这通常是外部网站策略导致，脚本会失败退出并给出可诊断错误信息。

建议：
- 稍后重试；
- 确认账号权限；
- 如页面结构变化，需要更新脚本解析逻辑。

## 无法发现最新年份链接 / 无法定位数据接口

当 `charteredabs.org` 页面结构变化时可能发生。脚本会提示失败原因。

建议：
- 先确认入口页面是否仍包含年份链接；
- 必要时根据实际页面更新探测逻辑。

