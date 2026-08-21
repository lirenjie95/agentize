本文件夹包含受支持语言 SDK 的模板。
目前支持的语言为 C、C++ 和 Python。
所有语言共享相似的结构和接口，并带有一些语言特定的文件和文件夹。

所有模板都有：

- 根文件夹中的 `Makefile`，定义以下命令：
    - `make setup`：生成一个（项目级的）`setup.sh` 脚本，用于为 SDK 设置环境变量。
    - 这与 agentize 仓库的 `make setup` 不同，后者生成的是用于 `wt` 和 `agentize` CLI 函数的跨项目 `setup.sh`。
    - `make build`：构建 SDK。
    - `make clean`：清理所有构建文件。
    - `make test`：运行测试用例。

- 根文件夹中的 `bootstrap.sh` 脚本，用于从模板初始化 SDK。
    - 这使得 `make agentize`（见 ../Makefile）简单到只需将此脚本复制到目标文件夹并运行它。
    - 该脚本会对模板文件进行必要的修改。
    - 完成后，它会删除自身。
