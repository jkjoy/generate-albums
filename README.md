# 自动化生成相册

模板来自于网络

可以自行修改模板

## 使用方法

修改`github\workflows\g.yaml`中的`repository`为你想要生成相册的仓库名称

在action中设置secret
- `TOKEN`为你的github token

`template.html`为模板文件,可自行调整 标题 等

`photos`为图片文件夹,照片上传到此文件夹中,会自动生成相册,照片名称为标题
