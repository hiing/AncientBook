# AncientBook

[English README](README.en.md)

缘起是看到[vRain](https://github.com/shanleiguang/vRain)项目是基于Perl工具链写的，并且只提供MacOS版本下载，于是VibeCoding了一下，作为Windows下竖状排版用，PDF输出。

AncientBook 是一个干净重构的 Python 桌面工具，用来把常见文档转换成古籍风格的中文竖排 PDF。

当前状态：核心 PDF 生成流程、桌面界面、Windows 打包脚本和 GitHub Release 发布包都已经完成。

## 安全原则

- 用户文档只在本机处理。
- 用户文字只作为数据读取，不作为代码执行。
- 字体来自 Windows 已安装字体，或用户自己选择且有权使用的本地字体文件。
- AncientBook 不内置商业字体或来源不明的字体文件。

## 直接下载

普通用户可以从 GitHub Release 下载 Windows 版：

[下载 AncientBook-Windows.zip](https://github.com/hiing/AncientBook/releases)

下载后解压，打开 `AncientBook-Windows` 文件夹，双击 `AncientBook.exe` 即可运行。

## 软件能做什么

- 选择一个或多个文档。
- 选择 PDF 输出文件夹。
- 从系统已安装中文字体中选择字体，也可以手动选择自己的 `.ttf` 或 `.otf` 字体文件。
- 选择古籍页面模板、纸张大小、字号和栏数密度。
- 在右侧预览古籍页面风格。
- 生成本地 PDF，不上传用户文字。

内置页面模板：

- `素雅书页`
- `朱栏格页`
- `旧藏纸页`

## 支持的输入格式

- `.txt`, `.text`
- `.md`, `.markdown`
- `.docx`
- 可复制文字的 `.pdf`
- `.rtf`
- `.html`, `.htm`
- `.odt`

旧版 `.doc` 文件会被识别，但当前版本会提示用户先另存为 `.docx`。扫描版 PDF 需要 OCR，本版本暂不自动转换。

## 用户使用步骤

1. 打开 `AncientBook.exe`。
2. 点击 `文档` 旁边的 `选择`，选择要转换的文档。第一次测试可以用 `examples\sample.txt`。
3. 点击 `输出文件夹` 旁边的 `选择`，选择 PDF 保存位置，例如 `output`。
4. 在字体列表中选择一个中文字体，例如 `微软雅黑 / Microsoft YaHei` 或 `宋体 / SimSun`。
5. 选择模板、纸张大小、字号和栏数密度。
6. 点击 `生成 PDF`。

软件会自动在输出文件夹里生成 PDF。例如 `examples\sample.txt` 会生成 `output\sample-AncientBook.pdf`。如果同名文件已经存在，会自动使用安全文件名，例如 `output\sample-AncientBook-2.pdf`。

更详细的验收说明见 `docs/release-checklists/non-programmer-acceptance.md`。

## 开发者首次运行

安装开发依赖：

```powershell
python -m pip install -e ".[dev]"
```

生成一个示例 PDF：

```powershell
ancientbook examples/sample.txt --output output/sample.pdf --overwrite
```

生成 A5 示例：

```powershell
ancientbook examples/sample.txt --output output/sample-a5.pdf --paper-size a5 --font-size large --columns fewer --template aged --overwrite
```

如果命令行需要指定字体，可以使用：

```powershell
ancientbook examples/sample.txt --output output/sample.pdf --font C:\Path\To\YourFont.ttf --overwrite
```

## 桌面版开发运行

启动桌面界面：

```powershell
ancientbook-desktop
```

桌面界面和命令行使用同一套本地 PDF 生成流程。

## 构建 Windows 桌面版

构建桌面程序：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1
```

构建完成后打开：

```text
dist\AncientBook\AncientBook.exe
```

`dist/` 是构建产物，不提交到 git。

Windows 图标位于 `assets\icon\AncientBook.ico`，PNG 源图位于 `assets\icon\AncientBook-icon.png`。

## 打包 Windows 发布包

生成给普通用户下载的 zip：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_windows_release.ps1
```

如果 `dist\AncientBook\AncientBook.exe` 已经存在，只想重新生成 zip：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/package_windows_release.ps1 -SkipBuild
```

发布包输出位置：

```text
release\AncientBook-Windows.zip
release\AncientBook-Windows.zip.sha256
```

zip 中包含 `AncientBook.exe`、运行时文件、快速说明 `README-FIRST.txt`、MIT `LICENSE`、中文项目说明 `README-project.md`、英文说明 `README.en.md`、示例文件和第三方依赖许可说明。

可以用 SHA-256 校验下载文件是否完整：

```powershell
Get-FileHash .\AncientBook-Windows.zip -Algorithm SHA256
Get-Content .\AncientBook-Windows.zip.sha256
```

两个结果里的 64 位哈希值一致，说明 zip 文件与发布时的文件一致。

## 快速验收

Windows 构建后可以运行：

```powershell
Test-Path dist\AncientBook\AncientBook.exe
python -m ancientbook.cli examples\sample.txt --output output\sample-acceptance.pdf --overwrite
```

然后打开 `output\sample-acceptance.pdf`，确认文字为竖排，并带有古籍风格页面背景、纸张纹理和边框样式。

## 字体与许可证

AncientBook 不内置商业或来源不明的字体。桌面版优先使用系统已安装字体，也允许用户选择自己有权使用的本地字体文件。

第三方依赖说明见 `docs/licenses/THIRD_PARTY_NOTICES.md`。

AncientBook 项目源码使用 MIT License。许可正文见 `LICENSE`。

