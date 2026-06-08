AncientBook v0.1.0 是第一个公开 Windows 桌面版发布包。

下载方式：

1. 下载 `AncientBook-Windows.zip`
2. 可选下载 `AncientBook-Windows.zip.sha256`，用 SHA-256 校验 zip 是否完整
3. 解压压缩包
4. 双击 `AncientBook.exe`

Windows PowerShell 校验方式：

```powershell
Get-FileHash .\AncientBook-Windows.zip -Algorithm SHA256
Get-Content .\AncientBook-Windows.zip.sha256
```

两个结果里的 64 位哈希值一致，说明 zip 文件与发布时的文件一致。

本版能力：

- 支持 `.txt`、`.md`、`.docx`、可复制文字的 `.pdf`、`.rtf`、`.html`、`.odt` 输入
- 生成古籍风格竖排 PDF
- 支持选择输出文件夹，自动生成安全文件名
- 支持 Windows 已安装中文字体，也支持用户手动选择有权使用的字体文件
- 内置 `素雅书页`、`朱栏格页`、`旧藏纸页` 三种样式
- 本地处理文档，不上传用户文字

许可说明：

- AncientBook 项目源码使用 MIT License
- 第三方依赖和用户字体遵循各自许可证
