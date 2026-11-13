# wrap-omp sandbox for oh-my-pi

This is a simple script to run [oh-my-pi](https://github.com/can1357/oh-my-pi) in [bubblewrap](https://github.com/containers/bubblewrap) sandbox. Provides isolation in case agent hallucinates and starts executing some commands it should not. 

__Note:__ This is __NOT__ a protection against malicious plugins or skills. Hackers are more clever than agents. The fact that various models failed to escape the sandbox in my testing does not mean anything in case of skilled attacker.

## Sandbox boundary
- filesystem is a blank tmpfs with critical folders mounted __read only__
- minimal set of files required for oh-my-pi to function
- only `~/.omp` and a workspace inside `$HOME` are writeable (`$PWD` by default)
- when the workspace is `$HOME` or outside it, nothing of it is mounted: omp
  starts in the sandbox home, which holds only `~/.omp` (writeable) and the
  read-only `~/.local` / `~/.bun` mounts
- host environment variables are not passed to the sandbox

## Configurable
You can edit `~/.config/wrap-omp.conf` to add variables and files passed to the sandbox

`"env"` copies variables that already exist on the host. `"set_env"` instead
sets literal values that exist only inside the sandbox:

```json
"set_env": { "KDE_HOME_READONLY": "1" }
```

The host environment is untouched, so the variable is visible to omp and the
commands it runs, but not to anything started outside the sandbox. If the same
name appears in both `"env"` and `"set_env"`, the `"set_env"` value wins.

`"read_only_mounts"` and `"writeable_mounts"` accept simple `*` globs. Their
`"try_mount_read_only"` / `"try_mount_writeable"` variants differ only in that a
path that does not exist is skipped instead of failing the sandbox.

`"shared_temp": true` backs the sandbox `/tmp` with a fresh directory under the
host `/tmp` (`mktemp -d`, printed on stderr at startup, kept after exit)
instead of an empty tmpfs, so you can inspect what the sandbox wrote. Other
mounts on `/tmp` still stack on top of it. `"shared_temp_cleanup": true`
deletes that directory when the sandbox exits.

The directory's host path is exported to the sandbox as `REALTEMP`. A host
editor launched from inside the sandbox cannot open `/tmp/foo` directly, since
that path only means something inside the sandbox; `omp-code` is a
`$VISUAL`/`$EDITOR` shim that rewrites `/tmp/...` arguments to
`$REALTEMP/...` and leaves everything else alone:

```json
"set_env": { "VISUAL": "omp-code", "EDITOR": "omp-code" }
```

It runs `/usr/bin/code` on the host with `--ozone-platform=headless
--logsPath /tmp/vscode-logs` (that log path stays the literal `/tmp` path) and
moves the given files after those flags. With `REALTEMP` unset it passes
arguments through unchanged.

D-Bus access is off unless enabled. The `dbus` object starts a filtered
`xdg-dbus-proxy` for the `system` and/or `session` bus and passes the policy
arguments (`--see`, `--talk`, `--own`, `--call`, `--broadcast`) through.

Image clipboard access is off unless `"clipboard_bridge": true`. `wrap-omp`
then starts `omp-clip-broker` on the host and binds only its socket and the
`omp-clip-shim` script into the sandbox (`omp-clip-shim` replaces `wl-paste`,
found through PATH). The broker serves exactly one thing — the current
`image/png` from the host clipboard, capped at 32 MiB. On Wayland it reads the
clipboard with `wl-paste`; on WSL it runs `powershell.exe` through interop on
the host, so the sandbox never gets `/mnt/c`, `/run/WSL`, or a Windows binary.
There is no request protocol, no MIME argument, no `SET_PNG`, and no clipboard
text; the sandbox also never gets a Wayland socket or `XDG_RUNTIME_DIR`.
Copying *out* keeps working through OSC 52 in the terminal. Text paste via
`ctrl+v` stays unavailable; use the terminal's own paste.

WSL is `linux`, so omp binds image paste to `ctrl+v` only (`alt+v` is the
Windows default) and Windows Terminal often consumes `ctrl+v`. Bind it
explicitly in the omp keybindings if paste does nothing:

```yaml
app.clipboard.pasteImage: ["ctrl+v", "alt+v"]
```

The broker socket is `SOCK_SEQPACKET`, so a normal Wayland client
(`SOCK_STREAM`) pointed at it fails at `connect()` with `EPROTOTYPE` and exits
cleanly. Either way the sandbox has no compositor, so the clip directory is not
a Wayland endpoint.

## Minimalistic
No containers, package definition scripts or other hard to configure stuff. If project builds on host it will build in sandbox.

Just a read only copy of your system intended to prevent agent from installing packages and changing settings it should not.

# Usage
## Installation
- copy `wrap-omp`, `omp-clip-shim`, `omp-clip-broker` and `omp-code` to
  your executable path. For example `cp wrap-omp omp-clip-shim omp-clip-broker
  omp-code ~/.local/bin` (the shim, broker and code wrapper must sit next
  to `wrap-omp`)
- copy config template and adapt it for your needs: `cp wrap-omp.conf.template ~/.config/wrap-omp.conf`

## Running
In your project folder do `wrap-omp <any omp arguments>`

oh-my-pi will function as usual provided required API keys have been passed in config file.