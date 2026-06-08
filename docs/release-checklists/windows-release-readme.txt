AncientBook Windows 快速使用说明

1. 双击 AncientBook.exe 启动软件。
2. 点击「文档」旁边的「选择」，选择要转换的文件。
3. 点击「输出文件夹」旁边的「选择」，选择 PDF 输出文件夹。
4. 在「字体」中选择一个已安装的中文字体，例如「微软雅黑 / Microsoft YaHei」或「宋体 / SimSun」。只有你确实要使用自己的字体文件时，才使用「自选字体」。
5. 选择页面模板、纸张大小、字号和栏数密度。右侧会显示古籍页面预览。
6. 点击「生成 PDF」。

输出文件会自动生成在你选择的文件夹里。
例如 sample.txt 会生成 sample-AncientBook.pdf。
如果同名文件已经存在，会自动生成 sample-AncientBook-2.pdf 这类安全文件名。

可选安全校验：
如果你同时下载了 AncientBook-Windows.zip.sha256，可以在 PowerShell 中运行：
Get-FileHash .\AncientBook-Windows.zip -Algorithm SHA256
Get-Content .\AncientBook-Windows.zip.sha256
两个结果里的 64 位哈希值一致，说明 zip 文件与发布时的文件一致。

支持的输入格式：
.txt, .text, .md, .markdown, .docx, 可复制文字的 .pdf, .rtf, .html, .htm, .odt

旧版 .doc 文件请先另存为 .docx。
扫描版 PDF 暂不自动 OCR。

安全说明：
AncientBook 在本机处理文档，不上传你的文字。
软件不内置商业或来源不明的字体文件。
字体来自 Windows 已安装字体，或来自你自己选择且有权使用的本地字体文件。

更多项目说明请看 README-project.md。
英文项目说明请看 README.en.md。
AncientBook 项目本身使用 MIT License，许可正文请看 LICENSE。
第三方依赖许可说明请看 licenses\THIRD_PARTY_NOTICES.md。
