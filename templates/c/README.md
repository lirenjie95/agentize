# C SDK

- `CMakeLists.txt`：用于构建 C SDK 的 CMake 配置文件。
- `src/`：包含 C SDK 源文件的文件夹（可通过 `AGENTIZE_SOURCE_PATH` 更改）。
  - `hello.c`：一个示例 C 源代码，其中的 `hello` 函数向屏幕打印 "Hello, World!"。
- `include/`：包含 C SDK 头文件的文件夹。
  - `hello.h`：`hello` 函数的头文件。
- `tests/`：包含 C SDK 测试用例的文件夹。
  - `test_main.c`：一个添加到 `ctest` 的简单用例，调用 `hello` 函数并检查 stdout 输出是否为 "Hello, World!"。
- `Makefile`：定义 C SDK 构建命令的 Makefile。
  - `make build`：执行 `cmake -S . -B build && cmake --build build` 构建 SDK。
  - `make clean`：执行 `make -C build clean` 清理构建文件。
  - `make test`：运行 C SDK 的测试用例。
