# Security Model & Threat Assessment

**Counter-Example Generator & Zero-Spoiler DSA Debugger**  
**Role:** Teammate 1 — Execution, Backend, and Security Engineer

---

## 1. Security Philosophy: Defense in Depth

Student submissions represent **untrusted arbitrary code execution**. Under no circumstances is arbitrary student code ever executed inside the backend FastAPI process using `exec()`, `eval()`, or dynamic imports.

The architecture applies defense in depth across multiple layers:

```
[Layer 1: Input Validation]
  -> Reject empty submissions, validate request constraints via Pydantic

[Layer 2: AST Static Analysis]
  -> Fast syntax tree inspection (`check_syntax`) before spawning processes

[Layer 3: Process & OS Isolation]
  -> Ephemeral temporary directory (`tempfile.mkdtemp`)
  -> Environment variable scrubbing (no `DATABASE_URL`, API keys, or tokens passed)
  -> Python isolated invocation (`python -I -B -s`)

[Layer 4: Resource Throttling & Limits]
  -> Subprocess timeout enforcement (`process.kill()`)
  -> Binary output byte capping (prevents memory bombs)
  -> Output path scrubbing (traceback sanitization)

[Layer 5: Container Isolation (Docker Mode)]
  -> `--network none` (complete air-gap)
  -> `--read-only` root filesystem
  -> `--pids-limit=32` (fork bomb mitigation)
  -> `--memory=128m` & `--cpus=1.0` (resource containment)
  -> `--cap-drop=ALL` (no privileged capabilities)
  -> Unprivileged user execution (`1000:1000`)
```

---

## 2. Threat Vector Mitigations

| Threat Vector | Attack Code Example | Implemented Mitigation | Verification Test |
| :--- | :--- | :--- | :--- |
| **Infinite Loop / Hang** | `while True: pass` | Strict timeout timer on `process.communicate()`. Automatic process kill. Returns `timeout`. | `test_security_infinite_loop_timeout` |
| **Output Flooding / Bomb** | `print('A' * 10**8)` | Binary stream capped at `MAX_OUTPUT_BYTES` (64KB). Process flagged with `output_limit_exceeded`. | `test_security_excessive_output_bomb` |
| **Secret Leaks** | `import os; print(os.environ)` | Environment is completely sanitized. Child processes only receive basic OS runtime variables (`PATH`, `TEMP`). | `test_security_environment_variable_isolation` |
| **Host File Tampering** | `open('hack.txt', 'w')` | Code executes in isolated ephemeral directory. In Docker, root FS is mounted read-only (`--read-only`). | `test_security_file_writing_contained_or_isolated` |
| **Network Probing / SSRF**| `import socket; socket.connect()` | Docker runs with `--network none`. In local mode, child has no access to backend internal IPC. | `test_security_socket_import_handling` |
| **Memory Exhaustion** | `a = [0] * (10**8)` | Subprocess memory error caught; Docker enforces strict `--memory=128m` cgroup limits. | `test_security_memory_exhaustion_attempt` |
| **Path Disclosure** | System traceback paths | Traceback paths are sanitized with regex to remove internal directory layouts. | `test_syntax_error`, `test_runtime_division_by_zero` |

---

## 3. Remaining Limitations & Production Recommendations

While the sandbox implements rigorous layers of defense, **Docker containers and local subprocesses share the host kernel**:

1. **Kernel Exploits:** Zero-day kernel privilege escalations could escape standard container namespaces. For high-assurance public deployments, utilize a microVM or gVisor sandbox (such as **Firecracker** or **gVisor `runsc`** runtime).
2. **Local Fallback Mode:** When Docker is not available on the host machine, the system operates in `LocalSubprocessSandbox`. While environment variables, timeouts, directories, and outputs are isolated, OS syscall permissions are that of the local user. In shared production environments, Docker or gVisor must be enabled.
3. **CPU Throttling on Windows Subprocesses:** Windows subprocess limits rely on Job Objects for hard memory/CPU caps if Docker is absent. In Docker Linux mode, cgroup limits (`--cpus`, `--memory`) provide enforced isolation.
